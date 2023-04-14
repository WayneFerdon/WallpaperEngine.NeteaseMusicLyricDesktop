# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:30:29
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-14 02:30:29
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\ELogMonitor.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import re
import time as tm
import traceback
import json
from CharaterMethods import *
from Constants import *
from ELogEncoding import *
from DisplayManager import DisplayManager
from Debug import Debug
from Singleton import Singleton
from MainLoop import LoopObject
from LyricManager import LyricManager
from PropertyEnum import *
from collections.abc import Callable

class LogType(PropertyEnum):
    Undefined = -1
    AppExit = 0
    Play = 1
    Load = 2
    SeekPos = 3
    Resume = 4
    Pause = 5

    @enumproperty 
    def method(self) -> Callable[[str], bool]: ...
    @enumproperty
    def key(self) -> str: ...

    @classmethod
    def __init_properties__(cls) -> None:
        cls.Play.method =  ELogMonitor.Instance.OnPlay
        cls.AppExit.method = ELogMonitor.Instance.OnAppExit
        cls.Play.method = ELogMonitor.Instance.OnPlay
        cls.Load.method = ELogMonitor.Instance.OnLoadDuration
        cls.SeekPos.method = ELogMonitor.Instance.OnSeekPosition
        cls.Resume.method = ELogMonitor.Instance.OnResume
        cls.Pause.method = ELogMonitor.Instance.OnPause

        cls.AppExit.key = "App exit."
        cls.Play.key = "player._$play"
        cls.Load.key = "??? __onAudioPlayerLoad"
        cls.SeekPos.key = "OnSeek"
        cls.Resume.key = "??? player._$resume do"
        cls.Pause.key = "??? player._$pause do"
        
        return super().__init_properties__()

class ELogMonitor(Singleton, LoopObject):
    def OnStart(self):
        super().OnStart()
        Debug.LogLow('ELogMonitor.OnStart')
        self.InitializeLog()
        Debug.LogLow('ELogMonitor.OnStartEnd')

    def InitializeLog(self):
        self.IsInitializing = True
        self.FileSize = 0
        self.SeekOffset = 1024
        fileCreatTime = datetime.fromtimestamp(os.path.getctime(LOGPATH)).astimezone()
        while True:
            self.LogFile = None
            self.LastestLog = None
            self.LastUpdate = fileCreatTime
            self.ModifiedTime = 0
            if not self.CheckFileSize():
                self.ReloadLogFile()
            self.Analysis()
            if LyricManager.Song and LyricManager.SongLength:
                break
            if self.SeekOffset >= self.FileSize:
                break
            self.SeekOffset *= 4
        self.IsInitializing = False

    def OnUpdate(self):
        super().OnUpdate()
        modifiedTime = os.path.getmtime(LOGPATH)
        if self.ModifiedTime >= modifiedTime:
            return
        self.ModifiedTime = modifiedTime
        if self.CheckFileSize(): # which will raise Exception if failed too many times
            self.Analysis()
        else:
            self.InitializeLog()

    def Analysis(self):
        lastest = self.GetLastestLines()
        new = list[str]()
        while len(lastest) > 0:
            line = lastest.pop()
            if line == self.LastestLog:
                break
            new.append(line)
        
        remain = len(new)
        while remain > 0:
            line = new.pop()
            remain = len(new)
            if remain == 0:
                self.LastestLog = line
            try:
                self.AnalysisLog(line)
            except Exception:
                Debug.LogError(traceback.format_exc())
    
    def GetLastestLines(self) -> list[str]:
        lines = (b"\n").join(self.LogFile.readlines())
        decoded, newEncode = self.Decode(lines)
        decoded = RemoveAll(decoded.split("\n"), "")
        if len(newEncode) == 0:
            return decoded
        if self.IsInitializing:
            return decoded
        Debug.LogAlert('------------------------------------------------------')
        Debug.LogAlert('UNKNOW ENCODES FOUND----------------------------------')
        Debug.LogAlert('new encodes: ', newEncode)
        Debug.LogAlert('------------------------------------------------------')
        for line in decoded:
            for code in decoded:
                if str(code) not in line:
                    continue
                print(line)
                break
        Debug.LogAlert('END UNKNOW ENCODES FOUND------------------------------')
        return decoded

    def CheckFileSize(self):
        if not self.LogFile:
            return False
        # check file size
        prevFileSize = self.FileSize
        self.FileSize = os.path.getsize(LOGPATH)
        if not self.FileSize: # None or 0
            return False
        return self.FileSize >= prevFileSize
    
    def ReloadLogFile(self):
        for _ in range(RELOAD_ATTEMPT):
            if self.LogFile:
                self.LogFile.close()
            try:
                self.LogFile = open(LOGPATH, "rb")
                self.FileSize = os.path.getsize(LOGPATH)
                self.LogFile.seek(max(0, self.FileSize-self.SeekOffset), 0)
                return False
            except Exception:
                Debug.LogError(traceback.format_exc())
                tm.sleep(1)
        raise Exception(f"Open {LOGPATH} failed after try {RELOAD_ATTEMPT} times")

    def AnalysisLog(self, content:str):
        logType = self.CheckLogType(content)
        if logType == LogType.Undefined:
            # return if not defined info got
            return
        if self.IsInitializing:
            # return if it's still initializing
            # only update output after initialization
            return
        
        # update last known position
        if logType in [LogType.SeekPos, LogType.Resume]:
            DisplayManager.Instance.OutputCurrentLyric(True)
        # clear output
        if logType == LogType.AppExit:
            DisplayManager.WriteOutput("")

    def GetLogInfoWithTime(self, content:str):
        if "[info]" in content:
            time, info =  re.split("\\[info]", content.strip().strip("\n"))
            time = re.split("\\[(.*?)]", time)
            time = datetime.strptime(time[3], "%Y-%m-%dT%H:%M:%S.%f%z")
            return time, info
        time = str(self.LastUpdate.year)
        time += re.split(":", re.split("\\[(.*?)]", content)[1])[2]
        time += ".000001"
        time = datetime.strptime(time, "%Y%m%d/%H%M%S.%f").astimezone()
        return time, None

    def OnAppExit(self, content:str) -> LogType:
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += tm.time() - DisplayManager.Instance.LastResume
        DisplayManager.Instance.PlayState = PLAY_STATE.EXITED
        time, _ = self.GetLogInfoWithTime(content)
        if time < self.LastUpdate:
            return False
        self.LastUpdate = time
        Debug.Log(time, "App Exit")
        return True
    
    def OnSeekPosition(self, content:str):
        time, _ = self.GetLogInfoWithTime(content)
        DisplayManager.Instance.LastPosition = float(content.split('OnSeek pos:')[1])
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastResume = time.timestamp()
        Debug.Log(time, "Seek Position:", DisplayManager.Instance.LastPosition)
        return True

    def CheckLogType(self, content:str) -> LogType:
        for state in LogType:
            if not state.key:
                continue
            if state.key not in content:
                continue
            Debug.LogElog(content)
            if state.method(content):
                return state
        if not self.IsInitializing:
            if "_p._$$Player" in  content:
                Debug.LogElogPlayer(content)
            else:
                Debug.LogElogLow(content)
        return LogType.Undefined

    def GetInfoLog(self, content:str) -> tuple[datetime, str]:
        time, info = self.GetLogInfoWithTime(content)
        if not info:
            return None, None
        if time < self.LastUpdate:
            return None, None
        self.LastUpdate = time
        return time, info

    def OnPlay(self, content:str):
        time, info = self.GetInfoLog(content)
        if not info:
            return False
        LyricManager.Song = str(re.split("_", re.split("\"", info)[1])[0])
        if not self.IsInitializing:
            LyricManager.PrepareLyric()
            LyricManager.LastSyncAttemp = None
        if DisplayManager.Instance.PlayState != PLAY_STATE.EXITED:
            DisplayManager.Instance.LastPosition = 0.0
        DisplayManager.Instance.NextLyricTime = 0.0
        # require load and resume next
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.Log(time, "Play song:", LyricManager.Song)
        return True

    def OnLoadDuration(self, content:str):
        time, info  = self.GetInfoLog(content)
        if not info:
            return False
        Debug.Log(time, "Load Duration of {}:".format(LyricManager.Song), LyricManager.SongLength)
        if not LyricManager.Song:
            return False
        LyricManager.SongLength = float(json.loads(
            re.split("\t", info)[0])["duration"])
        return True

    def OnResume(self, content:str):
        time, info = self.GetInfoLog(content)
        if not info:
            return False
        
        DisplayManager.Instance.PlayState = PLAY_STATE.PLAYING
        DisplayManager.Instance.LastResume = time.timestamp()
        Debug.Log(time, "Resume")
        return True

    def OnPause(self, content:str):
        time, info = self.GetInfoLog(content)
        if not info:
            return False
        
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += time.timestamp() - DisplayManager.Instance.LastResume
            self.LastPauseTime = time.timestamp()
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.Log(time, "Pause", DisplayManager.Instance.LastPosition)
        return True

    @staticmethod
    def Decode(datas:list[bytes]) -> list[str]:
        newCodes, exclusiveNew = list[bytes](), list[bytes]()
        strings = list[str]()
        keys = ENCODING.keys()
        encode, inLong = SPCEncode.UNKNOW, list[str]()
        for data in datas:
            # encode special encode
            if encode.size + 2 > len(inLong):
                inLong.append(str(data))
                if encode.size + 2 == len(inLong):
                    encoded = "【{}】".format('_'.join(inLong))
                    if encode.known and encoded in encode.known.keys():
                        encoded = encode.known[encoded]
                    strings.append(encoded)
                continue
            # check if it's special encode
            encode = SPCEncode.GetByCode(data)
            if encode is not SPCEncode.UNKNOW:
                inLong = [encode.name, str(data)]
                continue
            # known encodes
            if data in keys:
                strings.append(ENCODING[data])
                continue
            # unknown encodes
            strings.append("【" + str(data) + "】")
            if data in newCodes:
                continue
            if data in exclusiveNew:
                continue
            newCodes.append(data)
        return "".join(strings), newCodes
