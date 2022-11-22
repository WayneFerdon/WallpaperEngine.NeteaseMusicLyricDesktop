# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:00:21
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-22 02:59:41
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\DisplayManager.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import json
import requests
import sqlite3
from pykakasi import kakasi
from CharaterMethods import *
from Constants import *
from MainLoop import *

class DisplayManager(LoopObject):
    # 静态变量
    Instance=None
    _flag=False
    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance=super().__new__(cls)
        return cls.Instance
    def __init__(self):
        if DisplayManager._flag:
            return
        DisplayManager._flag=True
        super().__init__()
        Debug.LogLow("Initialization Start")
        self.__InitializeVariables__()
        self.__InitializeHanzi2KanjiLib__()
        Debug.LogLow("Initialization End")
    
    def OnStart(self):
        super().OnStart()
        self.WriteOutPut("")
        if self.CurrentSong:
            currentTimePosition = self.LastPosition
            if self.PlayState == PLAY_STATE.PLAYING:
                currentTimePosition += time.time() - self.LastResumeTime
            self.GetLyric()
            self.OutPutCurrentLyric(currentTimePosition)

    def OnFixUpdate(self):
        self.OutPutCurrentLyric()
    
    # def OnUpdate(self):
    #     super().OnUpdate()

    def __InitializeVariables__(self) :
        self.LogCount = 0
        self.PlayState = PLAY_STATE.STOPPED
        self.CurrentSong = None
        self.CurrentSongLyric = dict()
        self.CurrentSongLength = 0.0
        self.Kakasi = kakasi()

        self.LastResumeTime = 0.0
        self.LastPauseTime = 0.0
        self.LastPosition = 0.0
        self.CurrentLyric = [EMPTY_LYRIC] * 3
        
        self.NextLyricTime = 0.0
        self.SongLyricTimes = list[float]()
        self.OutPutHtml = ""
        self.LocalMusicInfo = self.LoadSongDataBase()

    def __InitializeHanzi2KanjiLib__(self) :
        libJson = ""
        with open(KANJI_LIB, "r") as kanjiLib:
            for data in kanjiLib.readlines():
                libJson += data
        self.Hanzi2KanjiLib = dict[str, str](json.loads(libJson))
    # endregion main methods

    # region Lyric methods
    def GetSongNameAndArtists(self) -> dict[float, dict[float, float]]:
        def FormatOutPut(jsonDate:dict) -> dict[float, dict[float, float]]:
            try:
                songName = str(jsonDate["name"])
                artists = list[str](jsonDate["artists"])
                if len(artists) == 0:
                    return NULL_LYRIC
                songArtist = "by: "
                for artist in artists:
                    if songArtist != "by: ":
                        songArtist += " / "
                    songArtist += artist["name"]
            except KeyError:
                return NULL_LYRIC
            result = NULL_LYRIC
            result[1.0] = {"Lyric": songName, "Translation": ""}, 
            result[float("inf")] = {"Lyric": songArtist, "Translation": ""}
            return result
        
        result = dict[float, dict[float, float]]()
        if self.CurrentSong in self.LocalMusicInfo.keys():
            jsonDate = dict(
                json.loads(self.LocalMusicInfo[self.CurrentSong])
            )
            result = FormatOutPut(jsonDate)
        if result == NULL_LYRIC:
            url = "https://music.163.com/api/song/detail/" \
                  "?id=" + self.CurrentSong + \
                  "&ids=[" + self.CurrentSong + "]"
            jsonDate = dict(
                json.loads(requests.get(url, headers=HEADERS).text)["songs"][0]
            )
            result = FormatOutPut(jsonDate)
        return result

    def OutPutCurrentLyric(self, targetTime:float= None):
        if targetTime is None:
            if not self.TryAutoUpdateLyric():
                return
        else:
            if not self.TrySetCurrentLyric(targetTime):
                return
        newOutPut = self.GetOutPut()
        if newOutPut == self.OutPutHtml:
            return
        self.OutPutHtml = newOutPut
        self.WriteOutPut(self.OutPutHtml)

    def GetHiraganaLyric(self, lyric:list[str]) -> dict[str, str]:
        lyricSplit = list[str]()
        for split in lyric:
            for each in self.Kakasi.convert(split):
                for text in SplitAll(each["orig"], "(（.*?）){1}"):
                    lyricSplit += self.Kakasi.convert(text)
        lyricConverted, lyricRomajinn, priorHira = "", "", ""
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

    def SplitLyric(self, lyric:str) -> list[str]:
        lyric = lyric\
            .replace("(", "（")\
            .replace(")", "）")\
            .replace(" ", "　")\
            .replace("　", "//split//　//split//")\
            .replace("、", "//split//、//split//")\
            .replace("。", "//split//、//split//")
        lyricSplited = re.split("//split//", lyric)
        result = list[str]()
        index = -1
        while index >= -len(lyricSplited):
            item = lyricSplited[index]
            index -= 1
            if item is None:
                index -= 1
            else:
                result.insert(0, item)
        return RemoveAll(result, "")

    def FormatLyric(self, lyric:dict[str, str], translation:str):
        def SimpleFormat(source:str) -> str:
            source = ReplaceAll(source, " 　", "　")
            source = ReplaceAll(source, "　 ", "　")
            source = ReplaceAll(source, "（ ", "（")
            return source.replace("　:", " :").replace(":　", ": ").replace("：　", "：")

        roma = SimpleFormat(lyric["Roma"])
        lyricFormated = SimpleFormat(lyric["Lyric"])
        if IsOnlyEnglishOrPunctuation(lyricFormated):
            lyricFormated = lyricFormated.replace("　", " ")
        if translation != "":
            translation = "译：" + translation + "\t|\t"
        translation += "音：" + roma
        translation = SimpleFormat(translation)

        return {
            "Lyric": ReplaceAll(lyricFormated, "  ", " "), 
            "Translation": ReplaceAll(translation, "  ", " ")
        }

    def GetConvertedLyric(self, splitTimeLyric:dict[float, str], splitTimeTranslation:dict[float, str], isJapanese:bool) -> dict[float, dict[str, str]]:
        result = dict[float, dict[str, str]]()
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
            lyricItem = self.GetHiraganaLyric(self.SplitLyric(lyric))
            result[timeItem] = self.FormatLyric(lyricItem, translation)
        return result

    def GetLyric(self):
        self.CurrentLyric = [
            EMPTY_LYRIC, 
            EMPTY_LYRIC, 
            EMPTY_LYRIC
        ]
        url = "http://music.163.com/api/song/lyric?" + \
            "id= " + str(self.CurrentSong) + "&lv= 1&kv= 1&tv= -1"
        text = requests.get(url, headers=HEADERS).text
        jsonDate = dict(json.loads(requests.get(url, headers=HEADERS).text))
        if text != None and "nolyric" in jsonDate.keys():
            result = self.GetSongNameAndArtists()
        else:
            lyricData, translationData, translationData = "", "", ""
            try:
                lyricData = str(jsonDate["lrc"]["lyric"])
            except KeyError:
                pass
            try:
                translationData = str(jsonDate["tlyric"]["lyric"])
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
            Debug.LogError(e, "\n", traceback.format_exc())
        finally:
            return True

    def TrySetCurrentLyric(self, targetTime:float):
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
            Debug.LogError(e, "\n", traceback.format_exc())
        finally:
            return False

    def GetOutPut(self):
        outPut = ""
        for i in range(3):
            for key in self.CurrentLyric[i]:
                lyric = self.CurrentLyric[i][key]
                if lyric is None:
                    lyric = ""
                outPut += "<div class= " + key + str(i) + ">" + lyric + "</div>"
                outPut += "\n"
        return outPut

    @staticmethod
    def GetSplitTimeLyric(lyric:str) -> dict[float, str]:
        newList = dict[float, str]()
        if lyric is None:
            return newList
        splited = re.split("\n", lyric)
        for lyricItem in splited:
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
    # endregion Lyric methods

    @staticmethod
    def LoadSongDataBase() -> dict[str, list[str]]:
        cursor = sqlite3.connect(DATABASE).cursor()
        results = cursor.execute(DATABASE_CURSER_KEY).fetchall()
        cursor.close()
        songData = dict[str, list[str]]()
        for result in results:
            songData[str(result[0])] = result[1]
        return songData
    
    @staticmethod
    def WriteOutPut(data:str):
        with open(OUTPUT, "w", encoding= "utf-8") as outPutFile:
            outPutFile.write(data)

    @staticmethod
    def WriteOutPut(data:str):
        with open(OUTPUT, "w", encoding= "utf-8") as outPutFile:
            outPutFile.write(data)
