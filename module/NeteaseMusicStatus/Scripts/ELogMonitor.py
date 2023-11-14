# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:30:29
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-11-14 09:20:38
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
# from ELogEncoding import *
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
        cls.AppExit.key = "App exit."
        cls.Play.key = "\"setPlaying\""
        # cls.Load.key = "Load:" # now being handled in LogType.Play
        cls.SeekPos.key = "OnSeek"
        cls.Resume.key = "|resume|"
        cls.Pause.key = "|pause|"

        cls.AppExit.method = ELogMonitor.Instance.OnAppExit
        cls.Play.method = ELogMonitor.Instance.OnPlay
        # cls.Load.method = ELogMonitor.Instance.OnLoadDuration
        cls.SeekPos.method = ELogMonitor.Instance.OnSeekPosition
        cls.Resume.method = ELogMonitor.Instance.OnResume
        cls.Pause.method = ELogMonitor.Instance.OnPause
        return super().__init_properties__()

class ELogMonitor(Singleton, LoopObject):
    def OnStart(self):
        super().OnStart()
        Debug.Log('ELogMonitor.OnStart')
        self.InitializeLog()
        Debug.Log('ELogMonitor.OnStartEnd')

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
            if LyricManager.Song and LyricManager.SongDuration:
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
            if self.LastestLog != '' and line == self.LastestLog:
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
        decoded = self.Decode(lines)
        decoded = decoded.split("\n")
        return decoded
        # decoded, newEncode = self.Decode(lines)
        # decoded = RemoveAll(decoded.split("\n"), "")
        # if len(newEncode) == 0:
        #     return decoded
        # # if self.IsInitializing:
        # #     return decoded
        # Debug.LogWarning('------------------------------------------------------')
        # Debug.LogWarning('UNKNOW ENCODES FOUND----------------------------------')
        # Debug.LogWarning('new encodes: ', newEncode)
        # Debug.LogWarning('------------------------------------------------------')
        # for line in decoded:
        #     for code in decoded:
        #         if str(code) not in line:
        #             continue
        #         print(line)
        #         break
        # Debug.LogWarning('END UNKNOW ENCODES FOUND------------------------------')
        # return decoded

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
            DisplayManager.Instance.OutputCurrentStateAndLyric()
        # clear output
        if logType == LogType.AppExit:
            DisplayManager.WriteOutput(EXIT_STATE_OUTPUT)

    def GetLogInfoWithTime(self, content:str):
        year = str(self.LastUpdate.year)
        splited = re.split(":", content.strip().strip("\n"))
        # unknow_1, unknow_2, dateAndTime, floatsecond(9digit), "INFO", *info
        _, _, time, ms, _ = splited[:5]
        info = ":".join(splited[5:])
        if "INFO" not in splited:
            ms = "000001"
            Debug.LogError(splited)
        time = "{}-{}-{}:{}:{}.{}".format(year, time[:2], time[2:7],time[7:9],time[9:], ms[:-3])
        time = datetime.strptime(time, "%Y-%m-%d/%H:%M:%S.%f").astimezone()
        return time, info

    def OnAppExit(self, content:str) -> LogType:
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += tm.time() - DisplayManager.Instance.LastResume
        DisplayManager.Instance.PlayState = PLAY_STATE.EXITED
        time, _ = self.GetLogInfoWithTime(content)
        if time < self.LastUpdate:
            return False
        self.LastUpdate = time
        Debug.LogHighest("App Exit", logTime=time)
        return True


    def OnSeekPosition(self, content:str):
        time, _ = self.GetLogInfoWithTime(content)
        DisplayManager.Instance.LastPosition = float(content.split('OnSeek pos:')[1])
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastResume = time.timestamp()
        Debug.LogHighest("Seek Position:", DisplayManager.Instance.LastPosition, logTime=time)
        return True

    def CheckLogType(self, content:str) -> LogType:
        for state in LogType:
            if not state.key:
                continue
            if state.key not in content:
                continue
            Debug.LogHigh(content)
            if state.method(content):
                return state
        if not self.IsInitializing:
            if "INFO:audio_player.cpp" in  content or "INFO:audioplayer.cpp" in  content:
                Debug.LogLow(content)
            else:
                Debug.LogLowest(content)
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
        songJson = info.split(",\"setPlaying\",")[1]
        dic = json.loads(songJson)
        LyricManager.Song = dic["trackIn"]["trackId"]
        LyricManager.SongDuration = dic["trackIn"]["track"]["duration"]
        if not self.IsInitializing:
            LyricManager.PrepareLyric()
            LyricManager.LastSyncAttemp = None
        if DisplayManager.Instance.PlayState != PLAY_STATE.EXITED:
            DisplayManager.Instance.LastPosition = 0.0
        DisplayManager.Instance.NextLyricTime = 0.0
        # require load and resume next
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.LogHighest("Play song:", LyricManager.Song, logTime=time)
        Debug.LogHighest("Song Suration:", LyricManager.SongDuration, logTime=time)
        return True

    # now can load in OnPlay()"
    # def OnLoadDuration(self, content:str):
    #     time, info  = self.GetInfoLog(content)
    #     if not info:
    #         return False
    #     Debug.LogHighest("Load Duration of {}:".format(LyricManager.Song), LyricManager.SongDuration, logTime=time)
    #     if not LyricManager.Song:
    #         return False
    #     LyricManager.SongDuration = float(json.loads(
    #         re.split("\t", info)[0])["duration"])
    #     return True

    def OnResume(self, content:str):
        time, info = self.GetInfoLog(content)
        if not info:
            return False
        
        DisplayManager.Instance.PlayState = PLAY_STATE.PLAYING
        DisplayManager.Instance.LastResume = time.timestamp()
        Debug.LogHighest("Resume", logTime=time)
        return True

    def OnPause(self, content:str):
        time, info = self.GetInfoLog(content)
        if not info:
            return False
        
        if DisplayManager.Instance.PlayState == PLAY_STATE.PLAYING:
            DisplayManager.Instance.LastPosition += time.timestamp() - DisplayManager.Instance.LastResume
            self.LastPauseTime = time.timestamp()
        DisplayManager.Instance.PlayState = PLAY_STATE.STOPPED
        Debug.LogHighest("Pause", DisplayManager.Instance.LastPosition, logTime=time)
        return True

    @staticmethod
    def Decode(datas:list[bytes]) -> list[str]:
        # decode data from .elog file encoding to utf-8
        decoded = bytes()
        for data in datas:
            onesDigit = 4*(int(int(data/16)/4)+1)-(int(int(data/16) % 4))-1
            b_2 = (1-(int(onesDigit)%2))*(int(data)%2)*2
            b_4 = (1-(int(onesDigit/2)%2))*((int(data/2)%2))*4
            b_8 = ((int(onesDigit/4)%2))*((int(data/4)%2))*8
            hexsDigit = ((((int(data/16)+8)%16+(data%16))%16)-b_2-b_4-b_8)%16
            byte = hexsDigit*16+onesDigit
            decoded += int(byte).to_bytes()
        return decoded.decode(encoding="utf-8")
        # newCodes, exclusiveNew = list[bytes](), list[bytes]()
        # strings = list[str]()
        # keys = ENCODING.keys()
        # Debug.LogError(newDatas)
        #     # b = 
        # encode, inLong = SPCEncode.UNKNOW, list[str]()
        # for data in datas:
        #     # encode special encode
        #     if encode.size + 2 > len(inLong):
        #         inLong.append(str(data))
        #         if encode.size + 2 == len(inLong):
        #             encoded = "【{}】".format('_'.join(inLong))
        #             if encode.known and encoded in encode.known.keys():
        #                 encoded = encode.known[encoded]
        #             elif encoded not in newCodes:
        #                 newCodes.append(encoded)
        #             strings.append(encoded)
        #         continue
        #     # check if it's special encode
        #     encode = SPCEncode.GetByCode(data)
        #     if encode is not SPCEncode.UNKNOW:
        #         inLong = [encode.name, str(data)]
        #         continue
        #     # known encodes
        #     if data in keys:
        #         strings.append(ENCODING[data])
        #         continue
        #     # unknown encodes
        #     strings.append("【" + str(data) + "】")
        #     if data in newCodes:
        #         continue
        #     if data in exclusiveNew:
        #         continue
        #     newCodes.append(data)
        # return "".join(strings), newCodes
