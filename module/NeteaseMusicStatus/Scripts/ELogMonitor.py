# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:30:29
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-22 03:16:56
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\ELogMonitor.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

from ElogEncoding import *
from DisplayManager import *

class NeteaseLogType():
    def __init__(self, state:LOG_VALID_INFO, method:classmethod, key:str) -> None:
        self.State = state
        self.Method = method
        self.Key = key

class ELogMonitor(LoopObject):
    # 静态变量
    Instance=None
    _flag=False
    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance=super().__new__(cls)
        return cls.Instance
    def __init__(self):
        if ELogMonitor._flag:
            return
        ELogMonitor._flag=True
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
            LOG_VALID_INFO.SETPOS, self.OnSetPosition, "???_$setPosition"
        ))
        self.LOG_TYPES.append(NeteaseLogType(
            LOG_VALID_INFO.RESUME, self.OnResume, "player._$resumedo"
        ))
        self.LOG_TYPES.append(NeteaseLogType(
            LOG_VALID_INFO.PAUSE, self.OnPause, "player._$pausedo"
        ))

    def OnStart(self):
        super().OnStart()
        self.IsInitializing = True
        self.LogFile = open(LOGPATH, "rb")
        self.FileSize = os.path.getsize(LOGPATH)
        self.LatestOffset = self.FileSize
        self.LogFile.seek(max(self.LatestOffset-200000, 0), 0)
        self.Analysis()
        self.IsInitializing = False

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
            # to use seek from end, must use mode "rb"
            if self.LatestOffset <= self.FileSize:
                lines = self.LogFile.readlines()
                return lines
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
                    raise Exception("Open %s failed after try 10 times" % LOGPATH)
                time.sleep(1)

    def AnalysisLog(self, content:str):
        if not self.IsInitializing:
            Debug.LogElog(content)
        try:
            validInfo = self.CheckAppExit(content)
            if validInfo == LOG_VALID_INFO.NONE:
                validInfo = self.CheckLogInfo(content)
            if validInfo == LOG_VALID_INFO.NONE or self.IsInitializing:
                return
        except Exception as e:
            Debug.LogError(e, "\n", traceback.format_exc())
            return
        if validInfo in [LOG_VALID_INFO.SETPOS, LOG_VALID_INFO.RESUME]:
            DisplayManager.Instance.OutPutCurrentLyric(DisplayManager.Instance.LastPosition)
        if validInfo == LOG_VALID_INFO.APPEXIT:
            DisplayManager.Instance.WriteOutPut("")

    def CheckAppExit(self, content:str) -> LOG_VALID_INFO:
        if "Appexit." not in content:
            return LOG_VALID_INFO.NONE
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += time.time() - DisplayManager.Instance.LastResumeTime
        DisplayManager.Instance.PlayState = PLAY_STATE.EXITED

        if self.LastUpdate == ZERO_DATETIME:
            year = datetime.fromtimestamp(os.path.getctime(LOGPATH)).year
        else:
            year = self.LastUpdate.year
        
        zoneOffset = (datetime.now()-datetime.now().utcnow()).seconds/3600
        zoneOffsetStr = str(int(zoneOffset)) + ":00"
        if zoneOffset < 10:
            zoneOffsetStr = "0" + zoneOffsetStr
        
        logTimeStr = str(year) + re.split(":", re.split("\\[(.*?)]", content)[1])[2] + ".000001+" + zoneOffsetStr
        logTime = datetime.strptime(logTimeStr, "%Y%m%d/%H%M%S.%f%z")
        if logTime < self.LastUpdate:
            return
        self.LastUpdate = logTime
        Debug.Log(logTime, "App Exit")
        return LOG_VALID_INFO.APPEXIT

    def CheckLogInfo(self, content:str) -> LOG_VALID_INFO:
        if "[info]" not in content:
            return LOG_VALID_INFO.NONE
        content = re.split("\\[info]", content.strip().strip("\n"))
        result = re.split("\\[(.*?)]", content[0])
        if len(result) < 6:
            return LOG_VALID_INFO.NONE

        logTimeStr = result[5]
        logTime = datetime.strptime(logTimeStr, "%Y-%m-%dT%H:%M:%S.%f%z")
        if logTime < self.LastUpdate:
            return LOG_VALID_INFO.NONE
        self.LastUpdate = logTime
        logInfo = content[1]
        for state in self.LOG_TYPES:
            if state.Key in logInfo:
                state.Method(logTime, logInfo)
                return state.State
        return LOG_VALID_INFO.NONE

    def OnPlay(self, logTime:datetime, logInfo:str):
        DisplayManager.Instance.CurrentSong = str(re.split("_", re.split("\"", logInfo)[1])[0])
        if not self.IsInitializing:
            DisplayManager.Instance.GetLyric()
        if DisplayManager.Instance.PlayState != PLAY_STATE.EXITED:
            DisplayManager.Instance.LastPosition = 0.0
        DisplayManager.Instance.NextLyricTime = 0.0
        # require load and resume next
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.Log(logTime, "Play song:", DisplayManager.Instance.CurrentSong)

    def OnLoadDuration(self, logTime:datetime, logInfo:str):
        DisplayManager.Instance.CurrentSongLength = float(json.loads(
            re.split("\t", logInfo)[0])["duration"])
        Debug.Log(logTime, "Load Duration:", DisplayManager.Instance.CurrentSongLength)

    def OnSetPosition(self, logTime:datetime, logInfo:str):
        DisplayManager.Instance.LastPosition = float(json.loads(logInfo.split("\t")[0])["ratio"]) * DisplayManager.Instance.CurrentSongLength
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastResumeTime = logTime.timestamp()
        Debug.Log(logTime, "Set Position:", DisplayManager.Instance.LastPosition)

    def OnResume(self, logTime:datetime, logInfo:str):
        DisplayManager.Instance.PlayState = PLAY_STATE.PLAYING
        DisplayManager.Instance.LastResumeTime = logTime.timestamp()
        Debug.Log(logTime, "Resume")

    def OnPause(self, logTime:datetime, logInfo:str):
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += logTime.timestamp() - DisplayManager.Instance.LastResumeTime
            self.LastPauseTime = logTime.timestamp()
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED

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
