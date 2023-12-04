# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-11 19:55:43
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-12-05 04:11:16
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\LyricManager.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import json
import sqlite3
import traceback
from CharaterMethods import *
from Constants import *
from PropertyEnum import *
from pykakasi import kakasi
from Singleton import Singleton
from MainLoop import LoopObject
from pyncm.apis import track
from Debug import Debug
from collections.abc import Callable

def TryGetValueFromKeys(data:dict,keys:list):
    for key in keys:
        if key not in data.keys():
            continue
        return data[key]

def FormatMultiInfos(infos:list):
    if type(infos) is not list:
        return infos
    if len(infos) == 0:
        return None
    result = infos[0]
    if len(infos) > 1:
        result += "({})".format((",".join(infos[1:])))
    return result

class Lyric(dict[str, str]):
    def __init__(self, lyric:str|tuple|dict, translation:str=None):
        if type(lyric) is tuple:
            if len(tuple(lyric)) > 2:
                raise ValueError("Too much data for lyric")
            if translation:
                raise ValueError("Too much data for lyric")
            lyric, translation = lyric
        if type(lyric) is dict:
            if lyric["Translation"]:
                if translation:
                    raise ValueError("Too much data for lyric")
                translation = lyric["Translation"]
            lyric = lyric["Lyric"]
        self["Lyric"] = lyric
        self["Translation"] = translation
        return super().__init__()
    
    @property
    def lyric(self)->str:
        return self["Lyric"]

    @property
    def translation(self)->str:
        return self["Translation"]
    
    @lyric.setter
    def lyric(self, value:str):
        self["Lyric"] = value

    @translation.setter
    def translation(self, value:str):
        self["Translation"] = value

class SongLyric(dict[float, Lyric]):
    def __init__(self, source:dict=None):
        if source:
            self.update(source)
        return super().__init__()

    def update(self, source:dict):
        for key in source:
            self[key] = source[key]
        return

    def __getitem__(self, __key: float|str) -> Lyric:
        return super().__getitem__(float(__key))

    def __setitem__(self, __key: float|str, __value: Lyric|tuple|dict) -> None:
        if type(__value) in [str, tuple, dict]:
            if type(__value) is str:
                __value = json.loads(__value)
            lyric = Lyric(__value)
        elif type(__value) is Lyric:
            lyric = __value
        else:
            raise TypeError("Trying to set wrong type to Lyric object")
        return super().__setitem__(float(__key), lyric)

class LyricManager(Singleton, LoopObject):
    class LyricSource(PropertyEnum):
        InfoOnly=-1
        Online=0
        Cache=1
        Temp=2
        WebCache=3

        @enumproperty
        def getLyric(self) -> Callable[[], SongLyric]: ...

        @classmethod
        def __init_properties__(cls) -> None:
            outer = LyricManager
            cls.InfoOnly.getLyric = outer.GetInfoOnlyLyric
            cls.Online.getLyric = outer.GetLyricFromDataFunc(outer.GetOnlineLyricData)
            cls.Cache.getLyric = outer.LoadLyricCache
            cls.Temp.getLyric = outer.GetLyricFromDataFunc(outer.GetTempLyricData)
            cls.WebCache.getLyric = outer.GetLyricFromDataFunc(outer.GetCacheWebLyricData)
            return super().__init_properties__()

    def __init__(self) -> None:
        super().__init__()
        LyricManager.Timeline = list[float]()
        LyricManager.Song = None
        LyricManager.Lyric = None
        LyricManager.SongDuration = 0.0
        LyricManager.__LocalMusicInfo__ = None
        LyricManager.__Hanzi2KanjiLib__ = None
        LyricManager.__Kakasi__ = None
        LyricManager.Synced = False
        LyricManager.LastSyncAttemp = None
        LyricManager.LastCache = 0

    def OnStart(self):
        super().OnStart()
        if not self.Song:
            return
        self.PrepareLyric()
        self.LastSyncAttemp = None

    def OnUpdate(self):
        super().OnUpdate()
        if not LyricManager.Song:
            return
        if LyricManager.Synced:
            return
        # try syncing from online if not yet
        interval = 60
        current = datetime.now()
        if LyricManager.LastSyncAttemp:
            if (current - LyricManager.LastSyncAttemp).seconds < interval:
                return
        LyricManager.PrepareLyric(True)
        LyricManager.LastSyncAttemp = current

    # region properties
    @classmethod
    @property
    def Kakasi(cls):
        if not cls.__Kakasi__:
            cls.__Kakasi__ = kakasi()
        return cls.__Kakasi__

    @classmethod
    @property
    def Hanzi2KanjiLib(cls):
        if not cls.__Hanzi2KanjiLib__:
            libJson = str()
            with open(KANJI_LIB, "r") as kanjiLib:
                for data in kanjiLib.readlines():
                    libJson += data
            cls.__Hanzi2KanjiLib__ = dict[str, str](json.loads(libJson))
        return cls.__Hanzi2KanjiLib__

    @classmethod
    @property
    def LocalMusicInfo(cls):
        if not cls.__LocalMusicInfo__:
            cls.__LocalMusicInfo__ = [
                cls.LoadSongDataBaseWeb(),
                cls.LoadSongDataBaseLib()
            ]
        return cls.__LocalMusicInfo__
    # endregion properties

    # region staticmethod
    @staticmethod
    def LoadSongDataBaseLib() -> dict[str, list[str]]:
        cursor = sqlite3.connect(LIB_DATABASE).cursor()
        results = cursor.execute(LIB_DATABASE_CURSER_KEY).fetchall()
        cursor.close()
        songData = dict[str, list[str]]()
        for title, result in results:
            try:
                if not result or result == "":
                    continue
                result = result.removeprefix('music:')
                data = json.loads(result)
                data['name'] = title
            except Exception:
                Debug.LogError(traceback.format_exc())
                continue
            idKeys = ['id', 'musicId']
            id = TryGetValueFromKeys(songData, idKeys)
            songData[str(id)] = data
        return songData
    
    @staticmethod
    def LoadSongDataBaseWeb() -> dict[str, list[str]]:
        cursor = sqlite3.connect(WEB_DATABASE).cursor()
        results = cursor.execute(WEB_DATABASE_CURSER_KEY).fetchall()
        cursor.close()
        songData = dict[str, list[str]]()
        for result in results:
            data = json.loads(result[1])
            id = str(result[0])
            songData[id] = data
        return songData

    @staticmethod
    def SimpleFormat(source:str) -> str:
        if not source:
            return ""
        source = ReplaceAll(source, " 　", "　")
        source = ReplaceAll(source, "　 ", "　")
        source = ReplaceAll(source, "（ ", "（")
        return source.replace("　:", " :").replace(":　", ": ").replace("：　", "：")

    @staticmethod
    def GetLyricWithTimeline(lyrics:str) -> dict[float, str]:
        timeline = dict[float, str]()
        if not lyrics:
            return timeline
        lyrics = re.split("\n", lyrics)
        for lyric in lyrics:
            lyric = re.split("\\[(.*?)]", lyric)
            try:
                if len(lyric) < 2:
                    continue
                time = lyric[1]
                if "by" in time:
                    continue
                lyric = lyric[2]
                if lyric == "":
                    continue
                time = re.split("\\:", time.replace(".", ":"))
                minute, second = int(time[0]), int(time[1])
                millisecond = int(time[2]) if len(time) > 2 else 0
                time = minute * 60000 + second * 1000 + millisecond
                timeline[time] = lyric
            except Exception:
                Debug.LogError(traceback.format_exc())
                pass
        return timeline

    @staticmethod
    def GetFormatedArtists(artists:list[dict]):
        if len(artists) == 0:
            return str(), str()
        nameList = list()
        translationList = list()
        for artist in artists:
            name = artist["name"]
            if "alias" in artist.keys():
                alias = FormatMultiInfos(artist["alias"])
                if alias:
                    name += f"({alias})"
            nameList.append(name)
            if "tns" in artist.keys():
                translation = FormatMultiInfos(artist["tns"])
            else:
                translation = name
            if not translation:
                continue
            translationList.append(translation)
        names = "by: " + " / ".join(nameList)
        translations = "by: " + " / ".join(translationList)
        return names, translations

    @staticmethod
    def FormatInfoOnlyLyric(songInfo:dict, isFull:bool=True) -> SongLyric:
        arKeys = ['artists', 'ar']
        aliasKeys = ['alias']
        tnsKeys = ['translate', 'tns', 'transName', 'transNames']

        songName = songInfo['name']
        trans = TryGetValueFromKeys(songInfo, tnsKeys)
        trans = FormatMultiInfos(trans)
        alias = TryGetValueFromKeys(songInfo, aliasKeys)
        alias = FormatMultiInfos(alias)
        if alias:
            if not trans:
                trans = str()
            trans += f"({alias})"
        
        artists = TryGetValueFromKeys(songInfo, arKeys)
        artists, artistTrans = LyricManager.GetFormatedArtists(artists)

        result = SongLyric()
        if isFull:
            result[0.0] = "无歌词"
            result["-inf"] = songName, trans
            result["inf"] = artists, artistTrans
        else:
            if not trans:
                trans = str()
            result["-inf"] = str(), str()
            result["-1"] = f"{songName}\t{artists}", f"{trans}\t{artistTrans}"
        return result
    
    @staticmethod
    def GetHiragana(orig:str, hira:str, roma:str, isJap:bool):
        # check if the previous split is japanese, then check current
        if not isJap:
            orig = orig.replace("　", " ")
        isJap = not IsOnlyEnglishOrPunctuation(orig)

        if not isJap:
            orig += " "
            return orig, orig, isJap
        if hira == orig:
            return orig, roma, isJap
        
        duplicated = False
        for i in range(min(len(hira), len(orig))):
            if hira[-i-1] == orig[-i-1]:
                duplicated = True
                continue
            if duplicated:
                orig = orig[0:-i] + f"（{hira[0:-i]}）" + hira[-i:]
            else:
                orig += f"（{hira}）"
            break
        return orig, roma, isJap

    @staticmethod
    def FixHiragana(source:str, roma:str, romaSource:str):
        # NOTE: hard fix for several specific situations
        # TODO: Use the given romaLyric to fix the split
        for hardFix in HARD_FIXS:
            fix = HARD_FIXS[hardFix]
            keyName = hardFix
            if keyName not in source:
                continue
            match = fix["romaMatch"]
            if romaSource and match not in romaSource:
                continue
            source = source.replace(keyName, fix["lyricReplace"])
            roma = roma.replace(fix["roma"], fix["romaReplace"])
        # debug test
        roma_test = RemoveAll(roma, ' ')
        roma_test = RemoveAll(roma_test, '?')
        roma_test = RemoveAll(roma_test, '？')
        romaSource = RemoveAll(romaSource, ' ')
        romaSource = RemoveAll(romaSource, '?')
        romaSource = RemoveAll(romaSource, '？')
        if roma_test and romaSource and (roma_test not in romaSource):
            Debug.Log('FixHiragana-----------------------')
            Debug.Log('source, roma:', source, roma)
            Debug.Log('roma_test:', roma_test)
            Debug.Log('romaSource_test:', romaSource)
            Debug.Log('End FixHiragana-----------------------')
        # end debug test
        return source, roma
    
    @staticmethod
    def SplitLyric(lyric:str) -> list[str]:
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
            if not item:
                index -= 1
            else:
                result.insert(0, item)
        return RemoveAll(result, "")

    @staticmethod
    def GetClosetInTimeline(time, maxDelta, timeline:dict[float, object]):
        min, closet = maxDelta, None
        for t in timeline.keys():
            delta = abs(time-t)
            if delta == 0:
                return t
            if delta > min:
                continue
            closet = t
            min = delta
        return closet
    # endregion staticmethod

    # region classmethod
    @classmethod
    def GetInfoOnlyLyric(cls, isFull:bool=True) -> SongLyric:
        # try load from local web data and local library data
        for localInfo in cls.LocalMusicInfo:
            if cls.Song not in localInfo.keys():
                continue
            songInfo = localInfo[cls.Song]
            result = cls.FormatInfoOnlyLyric(songInfo, isFull)
            if not result:
                continue
            return result
        # else try load from online data
        songInfo = track.GetTrackDetail(cls.Song)['songs'][0]
        result = cls.FormatInfoOnlyLyric(songInfo, isFull)
        return result
    
    @classmethod
    def GetHiraganaLyric(cls, orig:str, romaOrig:str) -> dict[str, str]:
        splited = list[str]()
        for split in cls.SplitLyric(orig):
            for each in cls.Kakasi.convert(split):
                for text in SplitAll(each["orig"], "(（.*?）){1}"):
                    splited += cls.Kakasi.convert(text)
        lrcSplits, romaSplits, isJap = list[str](), list[str](), True
        for split in splited:
            orig, hira, roma = split["orig"], split["hira"], split["hepburn"]
            orig, roma, isJap = cls.GetHiragana(orig, hira, roma, isJap)
            if isJap:
                orig, roma = cls.FixHiragana(orig, roma, romaOrig)
            lrcSplits.append(orig)
            romaSplits.append(roma)
        return ''.join(lrcSplits), ' '.join(romaSplits)

    @classmethod
    def FormatLyric(cls, lyric:str, translation:str, roma:str):
        lyric = cls.SimpleFormat(lyric)
        translation = cls.SimpleFormat(translation)

        if IsOnlyEnglishOrPunctuation(lyric):
            lyric = lyric.replace("　", " ")
        if roma and translation:
                translation = "译：" + translation + "\t|\t"
                translation += "音：" + roma
        return ReplaceAll(lyric, "  ", " "), ReplaceAll(translation, "  ", " ")

    @classmethod
    def PreformatJapLyric(cls, lyric:str, roma:str):
        for hanzi in cls.Hanzi2KanjiLib:
            if hanzi not in lyric:
                continue
            kanji = cls.Hanzi2KanjiLib[hanzi][0]
            lyric = ReplaceAll(lyric, hanzi, kanji)
        lyric, romaTemp = cls.GetHiraganaLyric(lyric, roma)
        if not roma:
            roma = romaTemp
        return lyric, roma

    @classmethod
    def GetConvertedLyric(
        cls,
        lrcTimeline:dict[float, str],
        transTimeline:dict[float, str],
        romaTimeline:dict[float, str],
        isJap:bool
    ) -> SongLyric:
        result = SongLyric()
        if not lrcTimeline:
            return result
        for time in lrcTimeline.keys():
            # lyrics
            lyric = lrcTimeline[time]
            # translations
            trans = None
            if time in transTimeline.keys():
                trans = transTimeline[time]
            # roma lyrics
            maxDelta = 1000
            romaTime = cls.GetClosetInTimeline(time, maxDelta, romaTimeline)
            roma = romaTimeline[romaTime] if romaTime else None
            # hiragana for Japanese
            if isJap:
                lyric, roma = cls.PreformatJapLyric(lyric, roma)
            result[time] = cls.FormatLyric(lyric, trans, roma)
        return result

    @classmethod
    def GetLyric(cls, isOnline:bool) -> SongLyric:
        if isOnline:
            sources = [cls.LyricSource.Online]
            Debug.Log("Syncing lyric online")
        else:
            sources = [
                cls.LyricSource.Temp,
                cls.LyricSource.WebCache,
                cls.LyricSource.Cache,
                cls.LyricSource.InfoOnly
            ]
        
        for source in sources:
            result = source.getLyric()
            if not result:
                continue
            if source == cls.LyricSource.InfoOnly:
                return result
            songInfo = cls.GetInfoOnlyLyric(False)
            if source == cls.LyricSource.Online:
                cls.Synced = True
                Debug.Log("Sync lyric online succeed")
            result.update(songInfo)
            result["inf"] = str(), str()
            return result
        if isOnline:
            Debug.Log("Sync lyric online failed")
    
    @classmethod
    def GetLyricFromDataFunc(cls, getter:classmethod):
        def GetLyricFromData(getter:classmethod) -> SongLyric:
            try:
                data = getter()
                if not data:
                    return None
                lyric, trans, roma, isJap = cls.GetLyricTimelines(data)
                return cls.GetConvertedLyric(lyric, trans, roma, isJap)
            except Exception:
                Debug.LogError(traceback.format_exc())
                return None
        
        return lambda : GetLyricFromData(getter)

    @classmethod
    def GetCacheWebLyricData(cls):
        try:
            webData = WEB_DATA_DIR + cls.Song
            if not os.path.isfile(webData):
                return None
            with open(webData,'r',encoding='utf-8') as f:
                data = json.loads(f.read())
            return data
        except Exception:
            Debug.LogError(traceback.format_exc())
            return None
    
    @classmethod
    def GetOnlineLyricData(cls):
        try:
            return dict[str, str](track.GetTrackLyrics(cls.Song))
        except Exception:
            Debug.LogError(traceback.format_exc())
            return None
    
    @classmethod
    def GetTempLyricData(cls):
        try:
            cursor = sqlite3.connect(TEMP_DATABASE).cursor()
            results = cursor.execute(TEMP_DATABASE_CURSER_KEY).fetchall()
            cursor.close()
            for result in results:
                match result[1]:
                    case 'image/jpg':
                        continue
                with open(result[0],'r',encoding='utf-8') as f:
                    data = json.loads(f.read())
                splited = str(data['klyric']['lyric']).split('song?id=')
                if len(splited) < 2:
                    return None
                splited = splited[1].split(']')
                id = int(splited[0])
                if id == cls.Song:
                    return data
        except Exception:
            Debug.LogError(traceback.format_exc())
            return None
    
    @classmethod
    def GetLyricTimelines(cls, data:dict[str, str]):
        if "nolyric" in data.keys():
            return None
        
        try:
            lyric = str(data["lrc"]["lyric"])
        except KeyError:
            return None

        try:
            translation = str(data["tlyric"]["lyric"])
        except KeyError:
            translation = None
        
        try:
            roma = str(data['romalrc']["lyric"])
        except KeyError:
            roma = None
        lyricTimeline = cls.GetLyricWithTimeline(lyric)
        translationTimeline = cls.GetLyricWithTimeline(translation)
        romaTimeline = cls.GetLyricWithTimeline(roma)
        isJap = IsContainJapanese(lyric)
        return lyricTimeline, translationTimeline, romaTimeline, isJap

    @classmethod
    def CacheLyric(cls):
        if not os.path.isdir(CACHE_DIR):
            os.makedirs(CACHE_DIR)
        cache = f'{CACHE_DIR}{cls.Song}.json'
        dump = json.dumps(dict(cls.Lyric), sort_keys=True)
        if os.path.isfile(cache):
            with open(cache,'r',encoding='utf-8') as f:
                if f.readable() and f.read() == dump:
                    return
        with open(cache,'w',encoding='utf-8') as f:
            f.write(dump)
        LyricManager.LastCache = datetime.now().timestamp()
    
    @classmethod
    def LoadLyricCache(cls) -> SongLyric:
        if not os.path.isdir(CACHE_DIR):
            return
        cacheFile = f'{CACHE_DIR}{cls.Song}.json'
        if not os.path.isfile(cacheFile):
            return
        with open(cacheFile,'r',encoding='utf-8') as f:
            data = json.loads(f.read())
        lyrics = SongLyric(data)
        return lyrics

    @classmethod
    def PrepareLyric(cls, isOnline:bool=False):
        lyric = cls.GetLyric(isOnline)
        if not lyric:
            return
        cls.Lyric = lyric
        cls.CacheLyric()
        cls.Timeline = list(cls.Lyric.keys())
        cls.Timeline.sort()
    # endregion classmethod
