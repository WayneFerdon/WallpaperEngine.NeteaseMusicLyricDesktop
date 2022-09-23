# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2021-09-10 17:43:13
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-08-25 13:17:07
# FilePath: \undefinede:\SteamLibrary\steamapps\common\wallpaper_engine\projects\myprojects\bg\module\NeteaseMusicStatus\Scripts\NeteaseMusicStatus.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# region import
import json
import asyncio
import re
import os
import traceback
import requests
import threading
import time
import sqlite3
import ctypes
from enum import Enum
from datetime import datetime
from pykakasi import kakasi
# endregion import

# region constants
# region log display switch
ENABLE_ELOG_DISPLAY = True
ENABLE_LOG = True
# endregion log display switch

# region paths and default values
PY_LOG_PATH = "../PyLog.log"
APPDATA = os.getenv("LOCALAPPDATA")
LOGPATH = os.path.expanduser(APPDATA + "/Netease/CloudMusic/cloudmusic.elog")
DATABASE = os.path.expanduser(APPDATA + "/Netease/CloudMusic/Library/webdb.dat")
DATABASE_CURSER_KEY = "SELECT tid, track FROM web_track"
OUTPUT = "../OutPut.html"
KANJI_LIB = "Hanzi2Kanji.json"
HEADERS = {
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64;\x64)\
            AppleWebKit/537.36 (KHTML,like Gecko)\
            Chrome/80.0.3987.87 Safari/537.36"
}
ZERO_DATETIME = datetime.strptime("0001-01-01T00:00:00.000000+00:00", "%Y-%m-%dT%H:%M:%S.%f%z")

EMPTY_LYRIC = {"Lyric": "", "Translation": ""}
NULL_LYRIC = {"Lyric": "无歌词", "Translation": ""}
RELOAD_ATTEMPT = 10
INITIAL_SELF_LAST_LOG = "INITIAL_SELF_LAST_LOG"

ENCODING = {
        11:"3",
        12:"C",
        13:"S",
        14:"c",
        15:"s",
        25:"[STX]",
        26:"2",
        27:"\"",
        28:"R",
        29:"B",
        30:"r",
        31:"b",
        40:"!",
        41:"1",
        44:"a",
        45:"q",
        46:"A",
        56:"0",
        57:"",
        60:"p",
        62:"P",
        69:"E",
        72:"G",
        73:"_w",
        74:"g",
        75:"w",
        79:"7",
        88:"V",
        89:"F",
        90:"v",
        91:"f",
        94:"6",
        104:"e",
        105:"u",
        106:"E",
        107:"U",
        108:"G",
        109:"5",
        110:"L",
        120:"t",
        121:"d",
        122:"T",
        123:"D",
        124:"4",
        125:"$",
        130:"+",
        131:" ",
        132:"K",
        133:"[",
        134:"k",
        135:"{",
        145:"\n",
        146:":",
        148:"Y",
        149:"J",
        150:"z",
        151:"j",
        160:")",
        161:"9",
        162:"\t",
        164:"i",
        165:"y",
        166:"I",
        167:"Y",
        176:"8",
        177:"(",
        180:"x",
        181:"h",
        183:"H",
        192:"O",
        193:"_",
        194:"o",
        198:"/",
        199:"?",
        209:"N",
        211:"n",
        215:".",
        224:"m",
        225:"}",
        226:"M",
        227:"]",
        228:"-",
        229:"=",
        240:"|",
        241:"l",
        242:"",
        243:"L",
        245:",",
}
# endregion paths and default values

# region print color
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
# text colors
FOREGROUND_GREY = 0x08  # grey.
FOREGROUND_BLUE = 0x09  # blue.
FOREGROUND_GREEN = 0x0a  # green.
FOREGROUND_RED = 0x0c  # red.
FOREGROUND_YELLOW = 0x0e  # yellow.
# background colors
BACKGROUND_BLUE = 0x90  # yellow.
BACKGROUND_GREEN = 0xa0  # yellow.
BACKGROUND_RED = 0xc0  # yellow.
BACKGROUND_YELLOW = 0xe0  # yellow.
# get handle
STD_OUT_HANDLE = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
# endregion print color
# endregion constants

# region enums
class PLAY_STATE(Enum):
    STOPPED = 0
    PLAYING = 1
    EXITED = 2

class LOG_VALID_INFO(Enum):
    NONE = 0
    APPEXIT = 1
    PLAY = 2
    LOAD = 3
    SETPOS = 4
    RESUME = 5
    PAUSE = 6
# endregion enums

# region class NeteaseMusicStatus:
class NeteaseMusicStatus:
    # region main methods
    def __init__(self):
        LogMain("Initialization Start")
        self.__InitializeVariables__()
        self.__InitializeHanzi2KanjiLib__()
        self.__InitializeExistingElogInfos__()
        self.__InitializeExistingLyricOutput__()
        self.IsInitializing = False
        LogMain("Initialization End")
    
    def __InitializeVariables__(self) :
        self.LogCount = 0
        self.PlayState = PLAY_STATE.STOPPED
        self.CurrentSong = False
        self.CurrentSongLyric = dict()
        self.CurrentSongLength = 0
        self.LastUpdate = ZERO_DATETIME
        self.kakasi = kakasi()
        self.LastestLog = INITIAL_SELF_LAST_LOG

        self.LastResumeTime = 0
        self.LastPauseTime = 0
        self.LastPosition = 0
        self.CurrentLyric = [EMPTY_LYRIC] * 3

        self.LOG_TYPE = {
            "player._$play":{
                "Method": self.OnPlay,
                "State": LOG_VALID_INFO.PLAY,
            },
            "???__onAudioPlayerLoad":{
                "Method": self.OnLoadDuration,
                "State": LOG_VALID_INFO.LOAD,
            },
            "???_$setPosition":{
                "Method": self.OnSetPosition,
                "State": LOG_VALID_INFO.SETPOS,
            },
            "player._$resumedo":{
                "Method": self.OnResume,
                "State": LOG_VALID_INFO.RESUME,
            },
            "player._$pausedo":{
                "Method": self.OnPause,
                "State": LOG_VALID_INFO.PAUSE,
            },
        }

        self.NextLyricTime = 0
        self.SongLyricTimes = list()
        self.OutPutHtml = ""
        self.LocalMusicInfo = self.LoadSongDataBase()
        self.IsInitializing = True

        self.CoroutineFixUpdate = self.FixUpdate()
        self.CoroutineUpdate = self.Update()
        self.FixUpdateLoop = asyncio.new_event_loop()
        self.UpdateLoop = asyncio.new_event_loop()
        self.ThreadFixUpdate = threading.Thread(target=self.StartLoop, args=(self.FixUpdateLoop,))
        self.ThreadUpdate = threading.Thread(target=self.StartLoop, args=(self.UpdateLoop,))

    def __InitializeHanzi2KanjiLib__(self) :
        with open(KANJI_LIB, "r") as kanjiLib:
            self.Hanzi2KanjiLib = kanjiLib.readlines()
        libJson = ""
        for data in self.Hanzi2KanjiLib:
            libJson += data
        self.Hanzi2KanjiLib = json.loads(libJson)

    def __InitializeExistingElogInfos__(self) :
        self.LogFile = open(LOGPATH, "rb")
        self.FileSize = os.path.getsize(LOGPATH)
        self.latestOffset = self.FileSize
        self.InitializeSeekPosition()
        self.Analysis()

    def InitializeSeekPosition(self):
        self.LogFile.seek(max(self.latestOffset-200000,0), 0)

    def __InitializeExistingLyricOutput__(self):
        self.WriteOutPut("")
        if self.CurrentSong:
            currentTimePosition = self.LastPosition
            if self.PlayState == PLAY_STATE.PLAYING:
                currentTimePosition += time.time() - self.LastResumeTime
            self.GetLyric()
            self.OutPutCurrentLyric(currentTimePosition)

    def StartLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
    
    def Start(self):
        try:
            self.ModifiedTime = 0
            self.ThreadFixUpdate.start()
            self.ThreadUpdate.start()
            asyncio.run_coroutine_threadsafe(self.CoroutineFixUpdate,self.FixUpdateLoop)
            asyncio.run_coroutine_threadsafe(self.CoroutineUpdate,self.UpdateLoop)
        except Exception as e:
            with open(PY_LOG_PATH, "a", encoding="utf-8") as logFile:
                logFile.write(LogError(e,"\n",traceback.format_exc()))
            self.Start()

    async def FixUpdate(self):
        await asyncio.sleep(0)
        while True:
            # sleep to prevent Thread lock and conflict with self.Update()
            time.sleep(0.001)
            self.OutPutCurrentLyric()
    
    async def Update(self):
        await asyncio.sleep(0)
        while True:
            time.sleep(0.001)
            modifiedTime = os.path.getmtime(LOGPATH)
            if self.ModifiedTime >= modifiedTime:
                continue
            self.ModifiedTime = modifiedTime
            self.CheckFileSize()
            self.Analysis()
    # endregion main methods

    # region Read File and Analysis Logs
    def Analysis(self):
        lines = self.GetDecodedLastestLines()
        if self.LastestLog == INITIAL_SELF_LAST_LOG:
            newLines = lines
        else:
            lines.reverse()
            newLines = list()
            for line in lines:
                if line == self.LastestLog:
                    break
                newLines.insert(0, line)
        for line in newLines:
            self.AnalysisLog(line)
        if len(newLines)>0:
            self.LastestLog = newLines[-1]
    
    def GetDecodedLastestLines(self):
        lines = self.GetLastLines()
        result = list()
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
            if self.latestOffset <= self.FileSize:
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

    def AnalysisLog(self, content):
        if ENABLE_ELOG_DISPLAY and not self.IsInitializing:
            LogElog(content)
        try:
            validInfo = self.CheckAppExit(content)
            if validInfo == LOG_VALID_INFO.NONE:
                validInfo = self.CheckLogInfo(content, self.IsInitializing)
            if validInfo == LOG_VALID_INFO.NONE or self.IsInitializing:
                return
        except Exception as e:
            exceptionInfo = traceback.format_exc()
            LogError(e,"\n",exceptionInfo)
            return
        if validInfo in [LOG_VALID_INFO.SETPOS, LOG_VALID_INFO.RESUME]:
            self.OutPutCurrentLyric(self.LastPosition)
        if validInfo == LOG_VALID_INFO.APPEXIT:
            self.WriteOutPut("")

    def CheckAppExit(self, content):
        if "Appexit." not in content:
            return LOG_VALID_INFO.NONE
        if self.PlayState == PLAY_STATE.PLAYING:
            self.LastPosition += time.time() - self.LastResumeTime
        self.PlayState = PLAY_STATE.EXITED

        if self.LastUpdate == ZERO_DATETIME:
            year = datetime.fromtimestamp(os.path.getctime(LOGPATH)).year
        else:
            year = self.LastUpdate.year
        
        zoneOffset = (datetime.now()-datetime.now().utcnow()).seconds/3600
        zoneOffsetStr = str(int(zoneOffset)) + ":00"
        if zoneOffset < 10:
            zoneOffsetStr = "0" + zoneOffsetStr
        
        logTimeStr = str(year) + re.split(":",re.split("\\[(.*?)]", content)[1])[2] + ".000001+" + zoneOffsetStr
        logTime = datetime.strptime(logTimeStr, "%Y%m%d/%H%M%S.%f%z")
        if logTime < self.LastUpdate:
            return
        self.LastUpdate = logTime
        LogInfo(logTime, "App Exit")
        return LOG_VALID_INFO.APPEXIT

    def CheckLogInfo(self, content, isInitializing):
        if "[info]" not in content:
            return LOG_VALID_INFO.NONE
        result = re.split("\\[info]", content.strip().strip("\n"))
        logTimeStr = re.split("\\[(.*?)]", result[0])[5]
        logTime = datetime.strptime(logTimeStr, "%Y-%m-%dT%H:%M:%S.%f%z")
        if logTime < self.LastUpdate:
            return LOG_VALID_INFO.NONE
        self.LastUpdate = logTime
        logInfo = result[1]
        for each in self.LOG_TYPE:
            if each in logInfo:
                self.LOG_TYPE[each]["Method"](logTime, logInfo, isInitializing)
                return self.LOG_TYPE[each]["State"]
        return LOG_VALID_INFO.NONE

    def OnPlay(self, logTime, logInfo, isInitializing):
        self.CurrentSong = re.split("_", re.split("\"", logInfo)[1])[0]
        if not isInitializing:
            self.GetLyric()
        if self.PlayState != PLAY_STATE.EXITED:
            self.LastPosition = 0
        self.NextLyricTime = 0
        # require load and resume next
        self.PlayState = PLAY_STATE.STOPPED
        LogInfo(logTime, "Play song:", self.CurrentSong)

    def OnLoadDuration(self, logTime, logInfo, isInitializing):
        self.CurrentSongLength = json.loads(
            re.split("\t", logInfo)[0])["duration"]
        LogInfo(logTime, "Load Duration:", self.CurrentSongLength)

    def OnSetPosition(self, logTime, logInfo, isInitializing):
        self.LastPosition = json.loads(logInfo.split("\t")[0])["ratio"] * self.CurrentSongLength
        if self.PlayState == PLAY_STATE.PLAYING:
            self.LastResumeTime = logTime.timestamp()
        LogInfo(logTime, "Set Position:", self.LastPosition)

    def OnResume(self, logTime, logInfo, isInitializing):
        self.PlayState = PLAY_STATE.PLAYING
        self.LastResumeTime = logTime.timestamp()
        LogInfo(logTime, "Resume")

    def OnPause(self, logTime, logInfo, isInitializing):
        if self.PlayState == PLAY_STATE.PLAYING:
            self.LastPosition += logTime.timestamp() - self.LastResumeTime
            self.LastPauseTime = logTime.timestamp()
        self.PlayState = PLAY_STATE.STOPPED

    @staticmethod
    def Decode(datas):
        stringList = list()
        keys = ENCODING.keys()
        for data in datas:
            isFound = data in keys
            if isFound:
                stringList.append(ENCODING[data])
            else:
                stringList.append("【" + str(data) +"】")
            continue
        resultList = list()
        for each in "".join(stringList).split("\n"):
            if each != "":
                resultList.append(each)
        return resultList
    # endregion Read File and Analysis Logs
    
    # region Lyric methods
    def GetSongNameAndArtists(self):
        def FormatOutPut(songName, songArtist):
            return {
                    0: NULL_LYRIC,
                    1: {"Lyric": songName, "Translation": ""},
                    float("inf"): {"Lyric": songArtist, "Translation": ""}
            }

        result = dict()
        if str(self.CurrentSong) in self.LocalMusicInfo.keys():
            try:
                jsonDate = json.loads(
                    self.LocalMusicInfo[str(self.CurrentSong)])
                songName = jsonDate["album"]["name"]
                artists = jsonDate["artists"]
                songArtist = "by: "
                for artist in artists:
                    if songArtist != "by: ":
                        songArtist += " / "
                    songArtist += artist["name"]
                result = FormatOutPut(songName, songArtist)
            except KeyError:
                pass
        if not result:
            url = "https://music.163.com/api/song/detail/" \
                  "?id=" + str(self.CurrentSong) + \
                  "&ids=[" + str(self.CurrentSong) + "]"
            jsonDate = json.loads(requests.get(url, headers=HEADERS).text)
            jsonDate = jsonDate["songs"][0]
            songName = jsonDate["name"]
            artists = jsonDate["artists"]
            songArtist = "by: "
            for artist in artists:
                if songArtist != "by: ":
                    songArtist += " / "
                songArtist += artist["name"]
            if songArtist != "by: ":
                result = FormatOutPut(songName, songArtist)
            else:
                result[0] = NULL_LYRIC
        return result

    def OutPutCurrentLyric(self, targetTime=None):
        if targetTime is None:
            if not self.TryAutoUpdateLyric():
                return
        else:
            if not self.TrySetCurrentLyric(targetTime):
                return
        
        newOutPut = self.GetOutPut()
        if newOutPut == self.OutPutHtml:
            return
        self.WriteOutPut(newOutPut)
        self.OutPutHtml = newOutPut

    def GetHiraganaLyric(self, lyric):
        lyricSplit = list()
        for split in lyric:
            for each in self.kakasi.convert(split):
                for Item in SplitAll(each["orig"], "(（.*?）){1}"):
                    lyricSplit += self.kakasi.convert(Item)
        lyricConverted, lyricRomajinn, priorHira = "","",""
        isJapanese = True

        for split in lyricSplit:
            orig, hira, roma = split["orig"], split["hira"], split["hepburn"]
            # check if the previous split is japanese, then check current
            if not isJapanese:
                orig = orig.replace("　", " ")
            isJapanese = not IsOnlyEnglishOrPunctuation(orig)
            if not isJapanese:
                lyricConverted += orig + " "
                lyricRomajinn += orig + " "
                priorHira = ""
                continue
            if hira == "":
                kanjiLyric = ""
                for each in orig:
                    if each in self.Hanzi2KanjiLib.keys():
                        kanjiLyric += self.Hanzi2KanjiLib[each][0]
                    else:
                        kanjiLyric += each
                orig, roma = kanjiLyric, ""
                for each in kakasi().convert(orig):
                    hira += each["hira"]
                    roma += each["hepburn"]
            if hira == orig:
                if hira == priorHira:
                    orig, roma = "", ""
                priorHira = ""
            else:
                isDuplicated = False
                for i in range(min(len(hira), len(orig))):
                    if hira[-i-1] == orig[-i-1]:
                        isDuplicated = True
                        continue
                    if isDuplicated:
                        orig = orig[0:-i] + "（" + hira[0:-i] + "）" + hira[-i:] + hira[-1]
                        priorHira = ""
                    break
                if not isDuplicated:
                    priorHira = "（" + hira + "）"
            lyricConverted += orig + priorHira
            lyricRomajinn += roma + " "

        return {
            "Lyric": lyricConverted,
            "Roma": lyricRomajinn
        }

    def SplitLyric(self, lyric):
        lyric = lyric\
            .replace("(", "（")\
            .replace(")", "）")\
            .replace(" ", "　")\
            .replace("　", "//split//　//split//")\
            .replace("、", "//split//、//split//")\
            .replace("。", "//split//、//split//")
        lyric = re.split("//split//", lyric)
        lyricSplit = list()
        index = -1
        while index >= -len(lyric):
            Item = lyric[index]
            if Item is None:
                index -= 2
            else:
                index -= 1
                lyricSplit.insert(0, Item)
        lyric = RemoveAll(lyricSplit, "")
        return lyric

    def FormatLyric(self, lyric, translation):
        def SimpleFormat(source):
            source = ReplaceAll(source, " 　", "　")
            source = ReplaceAll(source, "　 ", "　")
            source = ReplaceAll(source, "（ ", "（")
            return source.replace("　:", " :").replace(":　", ": ").replace("：　","：")

        roma = SimpleFormat(lyric["Roma"])
        lyric = SimpleFormat(lyric["Lyric"])
        if IsOnlyEnglishOrPunctuation(lyric):
            lyric = lyric.replace("　", " ")
        if translation != "":
            translation = "译：" + translation + "\t|\t"
        translation += "音：" + roma
        translation = SimpleFormat(translation)

        return {
            "Lyric": ReplaceAll(lyric, "  ", " "),
            "Translation": ReplaceAll(translation, "  ", " ")
        }

    def GetConvertedLyric(self, splitTimeLyric, splitTimeTranslation, isJapanese):
        result = dict()
        for timeItem in splitTimeLyric.keys():
            lyric = splitTimeLyric[timeItem]
            if timeItem in splitTimeTranslation.keys():
                translation = splitTimeTranslation[timeItem]
            else:
                translation = ""
            result[timeItem] = {
                "Lyric": lyric,
                "Translation": translation
            }
            if not isJapanese:
                result[timeItem] = {
                    "Lyric": lyric,
                    "Translation": translation
                }
                continue
            lyric = self.SplitLyric(lyric)
            lyric = self.GetHiraganaLyric(lyric)
            lyric = self.FormatLyric(lyric, translation)
            result[timeItem] = lyric
        return result

    def GetLyric(self):
        self.CurrentLyric = [
            EMPTY_LYRIC,
            EMPTY_LYRIC,
            EMPTY_LYRIC
        ]
        url = "http://music.163.com/api/song/lyric?" +\
            "id=" + str(self.CurrentSong) + "&lv=1&kv=1&tv=-1"
        text = requests.get(url, headers=HEADERS).text
        jsonDate = json.loads(requests.get(url, headers=HEADERS).text)
        if text != None and "nolyric" in jsonDate.keys():
            result = self.GetSongNameAndArtists()
        else:
            lyricData, translationData, translationData = "", "", ""
            try:
                lyricData = jsonDate["lrc"]["lyric"]
            except KeyError:
                pass
            try:
                translationData = jsonDate["tlyric"]["lyric"]
            except KeyError:
                pass

            splitTimeLyric = self.GetSplitTimeLyric(lyricData)
            splitTimeTranslation = self.GetSplitTimeLyric(translationData)

            if not splitTimeLyric:
                result = self.GetSongNameAndArtists()
            else:
                result = self.GetConvertedLyric(
                    splitTimeLyric,
                    splitTimeTranslation,
                    IsContainJapanese(lyricData)
                )
        self.CurrentSongLyric = result
        self.SongLyricTimes = list(result.keys())
        self.SongLyricTimes.sort()

    def TryAutoUpdateLyric(self):
        if self.PlayState != PLAY_STATE.PLAYING or self.NextLyricTime is None:
            return False
        currentTime = time.time() - self.LastResumeTime + self.LastPosition
        if (currentTime * 1000 < self.NextLyricTime):
            return False
        try:
            self.CurrentLyric[0] = self.CurrentLyric[1]
            self.CurrentLyric[1] = self.CurrentLyric[2]

            index = self.SongLyricTimes.index(self.NextLyricTime)
            if len(self.SongLyricTimes) <= index + 1:
                self.NextLyricTime = None
                self.CurrentLyric[2] = EMPTY_LYRIC
                return True
            self.NextLyricTime = self.SongLyricTimes[index + 1]
            self.CurrentLyric[2] = self.CurrentSongLyric[self.NextLyricTime]
            return True
        except IndexError as e:
            pass
        except Exception as e:
            exceptionInfo = traceback.format_exc()
            LogError(e,"\n",exceptionInfo)

    def TrySetCurrentLyric(self, targetTime):
        keyTime = None
        for keyTime in self.SongLyricTimes:
            if keyTime >= targetTime * 1000:
                break
        try:
            timeIndex = self.SongLyricTimes.index(keyTime)
            currentLyricTime = self.SongLyricTimes[timeIndex - 1]
            if len(self.SongLyricTimes) > 1:
                self.NextLyricTime = self.SongLyricTimes[timeIndex]
                self.CurrentLyric[2] = self.CurrentSongLyric[self.NextLyricTime]
                if timeIndex > 1:
                    previousLyricTime = self.SongLyricTimes[timeIndex - 2]
                    self.CurrentLyric[0] = self.CurrentSongLyric[previousLyricTime]
                else:
                    self.CurrentLyric[0] = ""
            else:
                self.NextLyricTime = None
                self.CurrentLyric[2] = EMPTY_LYRIC
            self.CurrentLyric[1] = self.CurrentSongLyric[currentLyricTime]
            return True
        except Exception as e:
            exceptionInfo = traceback.format_exc()
            LogError(e,"\n",exceptionInfo)

    def GetOutPut(self):
        outPut = ""
        for i in range(3):
            for key in self.CurrentLyric[i]:
                lyric = self.CurrentLyric[i][key]
                if lyric is None:
                    lyric = ""
                outPut += "<div class=" + key + str(i) + ">" + lyric + "</div>"
                outPut += "\n"
        return outPut

    @staticmethod
    def WriteOutPut(data):
        with open(OUTPUT, "w", encoding="utf-8") as outPutFile:
            outPutFile.write(data)

    @staticmethod
    def LoadSongDataBase():
        cursor = sqlite3.connect(DATABASE).cursor()
        results = cursor.execute(DATABASE_CURSER_KEY).fetchall()
        cursor.close()
        songData = dict()
        for result in results:
            songData[str(result[0])] = result[1]
        return songData

    @staticmethod
    def GetSplitTimeLyric(lyricList):
        newList = dict()
        if lyricList:
            lyricList = re.split("\n", lyricList)
        for lyricItem in lyricList:
            lyricItem = re.split("\\[(.*?)]", lyricItem)
            try:
                lyricTime = lyricItem[1]
                if "by" in lyricTime:
                    continue
                lyricItem = lyricItem[2]
                if lyricItem == "":
                    continue
                lyricTime = re.split("\\:", lyricTime.replace(".", ":"))
                minute = int(lyricTime[0])
                second = int(lyricTime[1])
                try:
                    millisecond = int(lyricTime[2])
                except IndexError:
                    millisecond = 0
                lyricTime = minute * 60000 + second * 1000 + millisecond
                newList[lyricTime] = lyricItem
            except Exception:
                pass
        return newList
    # endregion Get Lyric
# endregion class NeteaseMusicStatus:

# region common methods
# region common string methods

def RemoveAll(source, target):
    while target in source:
        source.remove(target)
    return source

def ReplaceAll(source, target, replacement):
    while target in source:
        source = source.replace(target, replacement)
    return source

def SplitAll(source, target, retainterget=True):
    findResult = re.compile(target).findall(source)
    newList = list()
    if findResult:
        findResult = findResult[0]
        if isinstance(findResult, tuple):
            findResult = findResult[0]
        source = source.split(findResult)
        for key in range(len(source)):
            result = SplitAll(source[key], target)
            if result:
                newList += result
            else:
                newList.append(source[key])
            if(retainterget and key != len(source)-1):
                newList.append(findResult)
        RemoveAll(newList, "")
        return newList
    newList.append(source)
    RemoveAll(newList, "")
    return newList
# endregion common string methods

# region print color methods
def SetCMDDisplay(type):
    ctypes.windll.kernel32.SetConsoleTextAttribute(STD_OUT_HANDLE, type)

def ResetCMDDisplay():
    SetCMDDisplay(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
# endregion constants

# region common charater methods
def IsContainJapanese(source):
    searchRanges = [
        "[\u3040-\u3090]",  # hiragana
        "[\u30a0-\u30ff]"   # katakana
    ]
    for range in searchRanges:
        if RemoveAll(re.compile(range).findall(source), "一"):
            return True
    return False

def IsContainChinese(source):
    return RemoveAll(re.compile("[\u4e00-\u9fa5]").findall(source), "一")

def IsOnlyEnglishOrPunctuation(source):
    searchRanges = [
        "[\u0000-\u007f]",
        "[\u3000-\u303f]",
        "[\ufb00-\ufffd]"
    ]
    if source == " " or source == "":
        return True
    if IsContainJapanese(source) or IsContainChinese(source):
        return False
    for range in searchRanges:
        if RemoveAll(re.compile(range).findall(source), "一"):
            return True
    return False
# endregion common charater methods

# region log methods
def Log(level, infos, type, time=None):
    if time is None:
        time = datetime.now()
    if not ENABLE_LOG:
        return
    logInfo = ""
    for each in infos:
        logInfo += str(each) + " "
    logInfo = level + "\t" + str(time) + "\t" + logInfo
    SetCMDDisplay(type)
    print(logInfo)
    ResetCMDDisplay()
    return logInfo + "\n"

def LogElog(*info):
    return Log("[ELOG]", info, FOREGROUND_GREY)

def LogMain(*info):
    return Log("[MAIN]", info, FOREGROUND_BLUE)

def LogInfo(time, *info):
    return Log("[LOG]", info, FOREGROUND_GREEN, time)

def LogError(*info):
    return Log("[ERROR]", info, FOREGROUND_RED)
# endregion main methods
# endregion common methods

# region main methods
if __name__ == "__main__":
    with open(PY_LOG_PATH, "a", encoding="utf-8") as logFile:
        logFile.write(LogMain("Script Start"))
    mainProgress = NeteaseMusicStatus()
    # while True:
    mainProgress.Start()

# endregion main methods