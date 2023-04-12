# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:30:29
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-12 08:37:02
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\ELogMonitor.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import re
import time
import traceback
import json
from Constants import *
from ELogEncoding import ENCODING
from DisplayManager import DisplayManager
from Debug import Debug
from Singleton import Singleton
from MainLoop import LoopObject
from LyricManager import LyricManager

class NeteaseLogType():
    def __init__(self, state:LOG_VALID_INFO, method:classmethod, key:str) -> None:
        self.State = state
        self.Method = method
        self.Key = key

class ELogMonitor(Singleton, LoopObject):
    def __init__(self):
        super().__init__()
        self.ModifiedTime = 0
        self.LastestLog = INITIAL_SELF_LAST_LOG
        self.LastUpdate = ZERO_DATETIME
        self.LOG_TYPES = list[NeteaseLogType]()
        self.LOG_TYPES.append(NeteaseLogType(
            LOG_VALID_INFO.PLAY, self.OnPlay, "player._$play"
        ))
        self.LOG_TYPES.append(NeteaseLogType(
            LOG_VALID_INFO.LOAD, self.OnLoadDuration, "???__onAudioPlayerLoad"
        ))
        self.LOG_TYPES.append(NeteaseLogType(
            LOG_VALID_INFO.RESUME, self.OnResume, "player._$resumedo"
        ))
        self.LOG_TYPES.append(NeteaseLogType(
            LOG_VALID_INFO.PAUSE, self.OnPause, "player._$pausedo"
        ))

    def InitializeSeekPosition(self):
        self.LogFile.seek(0, 0)

    def OnStart(self):
        super().OnStart()
        Debug.LogLow('ELogMonitor.OnStart')
        self.IsInitializing = True
        self.LogFile = open(LOGPATH, "rb")
        self.FileSize = os.path.getsize(LOGPATH)
        self.InitializeSeekPosition()
        self.Analysis()
        self.IsInitializing = False
        Debug.LogLow('ELogMonitor.OnStartEnd')

    def OnUpdate(self):
        super().OnUpdate()
        modifiedTime = os.path.getmtime(LOGPATH)
        if self.ModifiedTime >= modifiedTime:
            return
        self.ModifiedTime = modifiedTime
        self.CheckFileSize()
        self.Analysis()

    def Analysis(self):
        lines = self.GetDecodedLastestLines()
        if self.LastestLog == INITIAL_SELF_LAST_LOG:
            newLines = lines
        else:
            lines.reverse()
            newLines = list[str]()
            for line in lines:
                if line == self.LastestLog:
                    break
                newLines.insert(0, line)
        for line in newLines:
            self.AnalysisLog(line)
        if len(newLines)>0:
            self.LastestLog = newLines[-1]
    
    def GetDecodedLastestLines(self) -> list[str]:
        lines = self.GetLastLines()
        result = list[str]()
        isStart = True
        for each in lines:
            if not isStart:
                result.append(b"\n")
            result += each
            isStart = False
        result = self.Decode(result)
        return result

    def GetLastLines(self):
        try:
            self.FileSize = os.path.getsize(LOGPATH)
            if self.FileSize == 0:
                return None
            self.InitializeSeekPosition()
            return self.LogFile.readlines()
        except FileNotFoundError:
            return None
    
    def CheckFileSize(self):
        currentFileSize = os.path.getsize(LOGPATH)
        if currentFileSize >= self.FileSize:
            self.FileSize = currentFileSize
            return
        self.InitializeSeekPosition()
        for i in range(RELOAD_ATTEMPT):
            try:
                self.LogFile.close()
            except Exception:
                pass
            try:
                self.LogFile.close()
                self.LogFile = open(LOGPATH, "rb")
                self.FileSize = os.path.getsize(LOGPATH)
                return
            except Exception:
                if i == RELOAD_ATTEMPT - 1:
                    raise Exception(f"Open {LOGPATH} failed after try 10 times")
                time.sleep(1)

    def AnalysisLog(self, content:str):
        if not self.IsInitializing:
            Debug.LogElog(content)
        validInfo = self.CheckAppExit(content)
        if validInfo == LOG_VALID_INFO.NONE:
            validInfo = self.CheckOnSeekPosition(content)
        if validInfo == LOG_VALID_INFO.NONE:
            validInfo = self.CheckLogInfo(content)
        if validInfo == LOG_VALID_INFO.NONE:
            return # return if not valid info got
        if self.IsInitializing:
            return # return if it's still initializing, only update output after initialization
        
        # update last known position
        if validInfo in [LOG_VALID_INFO.SEEKPOS, LOG_VALID_INFO.RESUME]:
            DisplayManager.Instance.OutputCurrentLyric(DisplayManager.Instance.LastPosition)
        # clear output
        if validInfo == LOG_VALID_INFO.APPEXIT:
            DisplayManager.WriteOutput("")

    def GetLogTimeFromContent(self, content:str):
        if self.LastUpdate == ZERO_DATETIME:
            year = datetime.fromtimestamp(os.path.getctime(LOGPATH)).year
        else:
            year = self.LastUpdate.year
        
        zoneOffset = (datetime.now()-datetime.now().utcnow()).seconds/3600
        zoneOffsetStr = str(int(zoneOffset)) + ":00"
        if zoneOffset < 10:
            zoneOffsetStr = "0" + zoneOffsetStr
        
        logTimeStr = str(year) + re.split(":", re.split("\\[(.*?)]", content)[1])[2] + ".000001+" + zoneOffsetStr
        return datetime.strptime(logTimeStr, "%Y%m%d/%H%M%S.%f%z")

    def CheckAppExit(self, content:str) -> LOG_VALID_INFO:
        if "Appexit." not in content:
            return LOG_VALID_INFO.NONE
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += time.time() - DisplayManager.Instance.LastResume
        DisplayManager.Instance.PlayState = PLAY_STATE.EXITED
        logTime = self.GetLogTimeFromContent(content)
        if logTime < self.LastUpdate:
            return
        self.LastUpdate = logTime
        Debug.Log(logTime, "App Exit")
        return LOG_VALID_INFO.APPEXIT

    def CheckOnSeekPosition(self, content:str):
        if 'OnSeekpos' not in content:
            return LOG_VALID_INFO.NONE
        logTime = self.GetLogTimeFromContent(content)
        DisplayManager.Instance.LastPosition = float(content.split('OnSeekpos:')[1])
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastResume = logTime.timestamp()
        Debug.Log(logTime, "Seek Position:", DisplayManager.Instance.LastPosition)
        return LOG_VALID_INFO.SEEKPOS

    def CheckLogInfo(self, content:str) -> LOG_VALID_INFO:
        if "[info]" not in content:
            return LOG_VALID_INFO.NONE
        logInfo = re.split("\\[info]", content.strip().strip("\n"))
        result = re.split("\\[(.*?)]", logInfo[0])
        if len(result) < 6:
            return LOG_VALID_INFO.NONE

        logTimeStr = result[5]
        logTime = datetime.strptime(logTimeStr, "%Y-%m-%dT%H:%M:%S.%f%z")
        # NOTE: the GetLogTimeFromContent() is less accuracy than the above one
        # logTime = self.GetLogTimeFromContent(content)

        if logTime < self.LastUpdate:
            return LOG_VALID_INFO.NONE
        self.LastUpdate = logTime
        logInfo = logInfo[1]
        for state in self.LOG_TYPES:
            if state.Key in logInfo:
                state.Method(logTime, logInfo)
                return state.State
        return LOG_VALID_INFO.NONE

    def OnPlay(self, logTime:datetime, logInfo:str):
        LyricManager.Song = str(re.split("_", re.split("\"", logInfo)[1])[0])
        if not self.IsInitializing:
            LyricManager.PrepareLyric()
            LyricManager.LastSyncAttemp = None
        if DisplayManager.Instance.PlayState != PLAY_STATE.EXITED:
            DisplayManager.Instance.LastPosition = 0.0
        DisplayManager.Instance.NextLyricTime = 0.0
        # require load and resume next
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.Log(logTime, "Play song:", LyricManager.Song)

    def OnLoadDuration(self, logTime:datetime, logInfo:str):
        LyricManager.SongLength = float(json.loads(
            re.split("\t", logInfo)[0])["duration"])
        Debug.Log(logTime, "Load Duration:", LyricManager.SongLength)

    def OnResume(self, logTime:datetime, _):
        DisplayManager.Instance.PlayState = PLAY_STATE.PLAYING
        DisplayManager.Instance.LastResume = logTime.timestamp()
        Debug.Log(logTime, "Resume")

    def OnPause(self, logTime:datetime, _):
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += logTime.timestamp() - DisplayManager.Instance.LastResume
            self.LastPauseTime = logTime.timestamp()
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.Log(logTime, "Pause", DisplayManager.Instance.LastPosition)

    @staticmethod
    def Decode(datas:list[str]) -> list[str]:
        stringList = list[str]()
        keys = ENCODING.keys()
        for data in datas:
            if data in keys:
                stringList.append(ENCODING[data])
            else:
                stringList.append("【" + str(data) + "】")
            continue
        resultList = list[str]()
        for each in str("".join(stringList)).split("\n"):
            if each != "":
                resultList.append(each)
        return resultList
