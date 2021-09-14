import datetime
import json
import re
import os
from os.path import expanduser
from typing import DefaultDict, List
import requests
import time
import sqlite3
from enum import Enum

from pykakasi import kakasi, wakati

localAppData = os.getenv("LOCALAPPDATA")
LogPath = expanduser(localAppData + r"\Netease\CloudMusic\cloudmusic.log")
MusicDataPath = expanduser(
    localAppData + r"\Netease\CloudMusic\Library\webdb.dat")


class PlayState(Enum):
    Stopped = 0
    Playing = 1
    Exited = 2


class LogValidInfo(Enum):
    NotValid = 0
    AppExit = 1
    Play = 2
    Load = 3
    SetPosition = 4
    Resume = 5
    Pause = 6


class NeteaseMusicStatus:
    def __init__(self):
        self.MonitorPath = LogPath
        self.OutPutPath = r'.\OutPut.html'
        self.PlayState = PlayState.Stopped

        self.Headers = {
            'user-agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64;\x64)\
            AppleWebKit/537.36 (KHTML,like Gecko)\
            Chrome/80.0.3987.87 Safari/537.36'
        }
        self.CurrentSong = False
        self.CurrentSongLrc = dict()
        self.CurrentSongLength = 0
        self.LastUpdate = 0

        self.LastResumeTime = 0
        self.LastPauseTime = 0
        self.LastPosition = 0

        self.TryCount = 0
        self.CurrentLrc = [
            {'Lrc': '', 'Translation': ''},
            {'Lrc': '', 'Translation': ''},
            {'Lrc': '', 'Translation': ''}
        ]
        self.NextLrcTime = 0

        self.SongLrcKeyTime = list()
        self.OutPutHtml = str()
        self.Kakasi = kakasi()
        self.Wakati = wakati().getConverter()
        self.LocalMusicInfo = LoadSongDataBase()

        with open("./Hanzi2Kanji.json", "r") as KanjiLib:
            self.Hanzi2KanjiLib = KanjiLib.readlines()
        LibJson = ""
        for line in self.Hanzi2KanjiLib:
            LibJson += line
        self.Hanzi2KanjiLib = json.loads(LibJson)

        try:
            self.LogFile = open(self.MonitorPath, 'r', encoding='utf-8')
            self.FileSize = os.path.getsize(self.MonitorPath)
            self.LogFile.seek(0, 2)
        except Exception:
            raise

        LineList = self.GetLastLines(1000000)
        if LineList is not None:
            LineIndex = -1
            while True:
                try:
                    LineIndex += 1
                    LineData = LineList[LineIndex].decode('utf-8')
                    try:
                        self.CallbackLog(LineData, True)
                    except Exception:
                        pass
                except IndexError:
                    break
        with open(self.OutPutPath, 'w', encoding='utf-8') as OutPutFile:
            OutPutFile.write('')

        if self.CurrentSong:
            CurrentTimePosition = self.LastPosition
            if self.PlayState == PlayState.Playing:
                CurrentTimePosition += time.time() - self.LastResumeTime
            self.GetLrc()
            self.SetCurrentLrc(CurrentTimePosition)
            self.OutPutCurrentLrc()

    def GetKakasiConvert(self, Source, Mode):
        # Hiragana to ascii, default: no conversion
        self.Kakasi.setMode("H", Mode)
        # Katakana to ascii, default: no conversion
        self.Kakasi.setMode("K", Mode)
        # Japanese to ascii, default: no conversion
        self.Kakasi.setMode("J", Mode)
        self.Kakasi.setMode("s", True)  # add space, default: no separator
        self.Kakasi.setMode("C", True)  # capitalize, default: no capitalize
        return self.Kakasi.getConverter().do(Source)

    def GetLastLines(self, Length):
        FilePath = self.MonitorPath
        try:
            FileSize = os.path.getsize(FilePath)
            if FileSize == 0:
                return None
            else:
                # to use seek from end, must use mode 'rb'
                with open(FilePath, 'rb') as TargetFile:
                    Offset = -Length  # initialize offset
                    while -Offset < FileSize:  # offset cannot exceed file size
                        # read offset chars from eof(represent by number'2')
                        TargetFile.seek(Offset, 2)
                        Lines = TargetFile.readlines()  # read from fp to eof
                        if len(Lines) >= 2:  # if contains at least 2 lines
                            return Lines  # then last line is totally included
                        else:
                            Offset *= 2  # enlarge offset
                    TargetFile.seek(0)
                    return TargetFile.readlines()
        except FileNotFoundError:
            return None, False

    def GetSongNameAndArtists(self):
        Result = dict()
        if str(self.CurrentSong) in self.LocalMusicInfo.keys():
            try:
                JsonDate = json.loads(
                    self.LocalMusicInfo[str(self.CurrentSong)])
                SongName = JsonDate["album"]["name"]
                Artists = JsonDate['artists']
                SongArtist = 'by: '
                for Artist in Artists:
                    if SongArtist != 'by: ':
                        SongArtist += ' / '
                    SongArtist += Artist['name']
                Result = {
                    0: {'Lrc': SongName, 'Translation': ''},
                    float("inf"): {'Lrc': SongArtist, 'Translation': ''}
                }
            except KeyError:
                pass
        if not Result:
            Url = 'https://music.163.com/api/song/detail/' \
                  '?id=' + str(self.CurrentSong) + \
                  '&ids=[' + str(self.CurrentSong) + ']'
            JsonDate = json.loads(requests.get(Url, headers=self.Headers).text)
            JsonDate = JsonDate['songs'][0]
            SongName = JsonDate['name']
            Artists = JsonDate['artists']
            SongArtist = 'by: '
            for Artist in Artists:
                if SongArtist != 'by: ':
                    SongArtist += ' / '
                SongArtist += Artist['name']
            if SongArtist != 'by: ':
                Result = {
                    0: {'Lrc': SongName, 'Translation': ''},
                    float("inf"): {'Lrc': SongArtist, 'Translation': ''}
                }
            else:
                Result[0] = {'Lrc': '无歌词', 'Translation': ''}
        return Result

    def ReloadMonitorPath(self):
        try:
            self.LogFile = open(self.MonitorPath, "rb")
            self.FileSize = os.path.getsize(self.MonitorPath)
            self.LogFile.seek(0, 1)
            return True
        except Exception:
            return False

    def CallbackLog(self, Content, Initializing=False):
        ValidInfo = LogValidInfo.NotValid
        LogTime = 0

        if 'App exit' in Content:
            if self.PlayState == PlayState.Playing:
                self.LastPosition += time.time() - self.LastResumeTime
            self.PlayState = PlayState.Exited
            LogTime = time.time()
            ValidInfo = LogValidInfo.AppExit

        elif "[info]" in Content:
            Content = Content.strip().strip('\n')
            Result = re.split('\\[info]', Content)
            LogInfo = Result[1]
            LogTime = re.split('\\[(.*?)]', Result[0])
            LogTime = time.mktime(
                datetime.datetime.fromisoformat(LogTime[3]).timetuple())

            if 'player._$play' in LogInfo:
                self.CurrentSong = re.split('_', re.split('"', LogInfo)[1])[0]
                if not Initializing:
                    self.GetLrc()
                if self.PlayState != PlayState.Exited:
                    self.LastPosition = 0

                # require load and resume
                self.PlayState = PlayState.Stopped
                ValidInfo = LogValidInfo.Play
            elif '__onAudioPlayerLoad' in LogInfo:
                self.CurrentSongLength = json.loads(
                    re.split('\t', LogInfo)[0])['duration']
                ValidInfo = LogValidInfo.Load
            elif '_$setPosition' in LogInfo:
                self.LastPosition = json.loads(re.split('\t', LogInfo)[0])[
                    'ratio'] * self.CurrentSongLength
                ValidInfo = LogValidInfo.SetPosition
                if self.PlayState == PlayState.Playing:
                    if Initializing:
                        self.LastResumeTime = LogTime
                    else:
                        self.LastResumeTime = time.time()
            elif 'player._$resume do' in LogInfo:
                self.PlayState = PlayState.Playing
                self.LastResumeTime = LogTime
                ValidInfo = LogValidInfo.Resume
            elif 'player._$pause do' in LogInfo:
                ValidInfo = LogValidInfo.Pause
                if self.PlayState == PlayState.Playing:
                    self.PlayState = PlayState.Stopped
                    self.LastPosition += LogTime - self.LastResumeTime
                    self.LastPauseTime = LogTime
        if ValidInfo == LogValidInfo.NotValid:
            return False
        if Initializing:
            if (
                self.CurrentSong
                and self.CurrentSongLength
                and self.LastPosition
            ):
                return True
            self.LastUpdate = LogTime
            return False
        if ValidInfo in [LogValidInfo.SetPosition, LogValidInfo.Resume]:
            self.SetCurrentLrc(self.LastPosition)
            self.OutPutCurrentLrc()
        if ValidInfo == LogValidInfo.AppExit:
            with open(self.OutPutPath, 'w', encoding='utf-8') as OutPutFile:
                OutPutFile.write('')
        return True

    def Start(self, Interval=0.001):
        LogFile = self.MonitorPath
        while True:
            FileSize = os.path.getsize(LogFile)
            if FileSize < self.FileSize:
                while self.TryCount < 10:
                    if not self.ReloadMonitorPath():
                        self.TryCount += 1
                    else:
                        self.TryCount = 0
                        self.FileSize = os.path.getsize(LogFile)
                        break
                    time.sleep(0.1)

                if self.TryCount == 10:
                    raise Exception("Open %s failed after try 10 times"
                                    % LogFile)
            else:
                self.FileSize = FileSize
            CurrentPosition = self.LogFile.tell()
            Line = self.LogFile.readline()
            if not Line:
                self.LogFile.seek(CurrentPosition)
            elif not Line.endswith("\n"):
                self.LogFile.seed(CurrentPosition)
            else:
                self.CallbackLog(Line)
            time.sleep(Interval)
            if self.PlayState == PlayState.Playing:
                self.SetCurrentLrc()
                self.OutPutCurrentLrc()

    def OutPutCurrentLrc(self):
        NewOutPut = GetOutPut(self.CurrentLrc)
        if NewOutPut == self.OutPutHtml:
            return
        with open(self.OutPutPath, 'w', encoding='utf-8') as OutPutFile:
            OutPutFile.write(NewOutPut)
        self.OutPutHtml = NewOutPut

    @staticmethod
    def GetSplitTimeLrc(LrcList):
        NewList = dict()
        if LrcList:
            LrcList = re.split('\n', LrcList)
        for LrcItem in LrcList:
            LrcItem = re.split('\\[(.*?)]', LrcItem)
            try:
                LrcTime = LrcItem[1]
                if 'by' in LrcTime:
                    continue
                LrcItem = LrcItem[2]
                if LrcItem == '':
                    continue
                LrcTime = re.split('\\:', LrcTime.replace(".", ":"))
                Minute = int(LrcTime[0])
                Second = int(LrcTime[1])
                try:
                    Millisecond = int(LrcTime[2])
                except IndexError:
                    Millisecond = 0
                LrcTime = Minute * 60000 + Second * 1000 + Millisecond
                NewList[LrcTime] = LrcItem
            except Exception:
                pass
        return NewList

    def GetHiraganaLrc(self, Lrc, IsPreviousJapanese):
        if not IsPreviousJapanese or IsOnlyEnglishOrPunctuation(Lrc):
            Lrc = Lrc.replace("　", " ")
            IsPreviousJapanese = not IsOnlyEnglishOrPunctuation(Lrc)
        if not IsPreviousJapanese:
            LrcHiragana = " " + Lrc
        else:
            LrcHiragana = self.GetKakasiConvert(Lrc, "H")   # .replace(" ", "")
            if IsContainChinese(LrcHiragana):
                KanjiLrc = ""
                for each in Lrc:
                    if each in self.Hanzi2KanjiLib.keys():
                        each = self.Hanzi2KanjiLib[each][0]
                    KanjiLrc += each
                Lrc = KanjiLrc
                LrcHiragana = self.GetKakasiConvert(
                    Lrc, "H")  # .replace(" ", "")
            if LrcHiragana != Lrc:
                ListedLrcHiragana = list(LrcHiragana)
                ListedLrc = list(Lrc)
                LrcEnd = list()
                for Index in range(len(ListedLrc)):
                    LrcIndex = -Index - 1
                    if ListedLrcHiragana[LrcIndex] == ListedLrc[LrcIndex]:
                        LrcEnd.append(ListedLrc[LrcIndex])
                        ListedLrcHiragana[LrcIndex] = ""
                        ListedLrc[LrcIndex] = ""
                    else:
                        break
                RemoveAll(ListedLrc, "")
                RemoveAll(ListedLrcHiragana, "")
                LrcHiragana = ""
                for String in ListedLrc:
                    LrcHiragana += String

                LrcHiragana += "("
                for String in ListedLrcHiragana:
                    LrcHiragana += String
                LrcHiragana += ")"

                for String in LrcEnd:
                    LrcHiragana += String
        LrcRomanjinn = self.GetKakasiConvert(Lrc, "a") + " "
        return IsPreviousJapanese, LrcHiragana, LrcRomanjinn

    def GetConvertedLrc(self, SplitTimeLrc, SplitTimeTranslation, IsJapanese):
        Result = dict()
        for TimeItem in SplitTimeLrc.keys():
            Lrc = SplitTimeLrc[TimeItem]
            if TimeItem in SplitTimeTranslation.keys():
                Translation = SplitTimeTranslation[TimeItem]
            else:
                Translation = ""
            if IsJapanese:
                LrcConverted = ""
                LrcSplitList = self.Wakati.do(Lrc.replace(" ", "　"))
                LrcSplitList = LrcSplitList.split(" ")
            else:
                LrcConverted = Lrc
                LrcSplitList = list()

            IsPreviousJapanese = False
            LrcRomajinn = ""
            for Split in LrcSplitList:
                if "　" in Split:
                    Split = Split.replace("　", "//Split//　//Split//")
                    Split = Split.split("//Split//")
                if isinstance(Split, list):
                    for Item in Split:
                        IsPreviousJapanese, ItemHiragana, ItemRomajinn = \
                            self.GetHiraganaLrc(Item, IsPreviousJapanese)
                        LrcConverted += " " + ItemHiragana
                        LrcRomajinn += ItemRomajinn
                    continue
                IsPreviousJapanese, SplitHiragana, SplitRomajinn = \
                    self.GetHiraganaLrc(Split, IsPreviousJapanese)
                LrcConverted += " " + SplitHiragana
                LrcRomajinn += SplitRomajinn
            LrcConverted = ReplaceAll(LrcConverted, " 　", "　")
            LrcConverted = ReplaceAll(LrcConverted, "　 ", "　")

            LrcRomajinn = ReplaceAll(LrcRomajinn, " 　", "　")
            LrcRomajinn = ReplaceAll(LrcRomajinn, "　 ", "　")

            if not IsContainJapanese(LrcConverted):
                LrcConverted = LrcConverted.replace("　", " ")
                if IsJapanese:
                    if Translation != "":
                        Translation += " / "
                    Translation += LrcConverted
            else:
                LrcConverted = LrcConverted.replace("　:　", " : ")
                if Translation != "":
                    Translation += " / "
                Translation += LrcRomajinn
            Translation = Translation.replace("　:　", " : ")

            LrcConverted = ReplaceAll(LrcConverted, "  ", " ")
            Translation = ReplaceAll(Translation, "  ", " ")
            Result[TimeItem] = {
                'Lrc': LrcConverted,
                'Translation': Translation
            }
        return Result

    def GetLrc(self):
        Url = "http://music.163.com/api/song/lyric?" + \
              "id=" + str(self.CurrentSong) + "&lv=1&kv=1&tv=-1"
        JsonDate = json.loads(requests.get(Url, headers=self.Headers).text)
        if 'nolyric' in JsonDate.keys():
            Result = self.GetSongNameAndArtists()
        else:
            LyricData = str()
            TranslationData = str()
            try:
                LyricData = JsonDate['lrc']['lyric']
            except KeyError:
                pass
            try:
                TranslationData = JsonDate['tlyric']['lyric']
            except KeyError:
                pass

            SplitTimeLrc = self.GetSplitTimeLrc(LyricData)
            SplitTimeTranslation = self.GetSplitTimeLrc(TranslationData)

            if not SplitTimeLrc:
                Result = self.GetSongNameAndArtists()
            else:
                Result = self.GetConvertedLrc(
                    SplitTimeLrc,
                    SplitTimeTranslation,
                    IsContainJapanese(LyricData)
                )
        self.CurrentSongLrc = Result

        self.SongLrcKeyTime = list(Result.keys())
        self.SongLrcKeyTime.sort()

    def SetCurrentLrc(self, TargetTime=None):
        if TargetTime is None:
            CurrentTime = time.time() - self.LastResumeTime + self.LastPosition
            if self.NextLrcTime is None:
                pass
            else:
                if (
                    CurrentTime * 1000 - 500 < self.NextLrcTime
                    or self.PlayState != PlayState.Playing
                ):
                    return
                try:
                    self.CurrentLrc[0] = self.CurrentLrc[1]
                    self.CurrentLrc[1] = self.CurrentLrc[2]

                    CurrentLrcIndex = self.SongLrcKeyTime.index(
                        self.NextLrcTime)
                    CurrentLrcTime = self.SongLrcKeyTime[CurrentLrcIndex]
                    if (len(self.SongLrcKeyTime) - 1) <= CurrentLrcIndex:
                        self.NextLrcTime = None
                        self.CurrentLrc[2] = {'Lrc': '', 'Translation': ''}
                        return
                    self.NextLrcTime = self.SongLrcKeyTime[CurrentLrcIndex + 1]
                    self.CurrentLrc[2] = self.CurrentSongLrc[self.NextLrcTime]
                except Exception:
                    pass
        else:
            KeyTime = None
            for KeyTime in self.SongLrcKeyTime:
                if KeyTime >= TargetTime * 1000:
                    break
            try:
                TimeIndex = self.SongLrcKeyTime.index(KeyTime)
                CurrentLrcTime = self.SongLrcKeyTime[TimeIndex - 1]
                if len(self.SongLrcKeyTime) > 1:
                    self.NextLrcTime = self.SongLrcKeyTime[TimeIndex]
                    self.CurrentLrc[2] = self.CurrentSongLrc[self.NextLrcTime]
                else:
                    self.NextLrcTime = None
                    self.CurrentLrc[2] = {'Lrc': '', 'Translation': ''}
                self.CurrentLrc[1] = self.CurrentSongLrc[CurrentLrcTime]
            except Exception:
                pass


def RemoveAll(Source, Target):
    while Target in Source:
        Source.remove(Target)
    return Source


def ReplaceAll(Source, Target, New):
    while Target in Source:
        Source = Source.replace(Target, New)
    return Source


def GetOutPut(CurrentLrc):
    OutPut = ""
    for i in range(3):
        for key in CurrentLrc[i]:
            Lrc = CurrentLrc[i][key]
            if Lrc is None:
                Lrc = ""
            OutPut += '<div class="' + key + str(i) + '">' + Lrc + '</div>'
            OutPut += '\n'
    return OutPut


def LoadSongDataBase():
    cursor = sqlite3.connect(MusicDataPath).cursor()
    CursorResults = cursor.execute(
        'SELECT tid, track '
        'FROM web_track'
    ).fetchall()
    cursor.close()
    SongData = dict()
    for each in CursorResults:
        SongData[str(each[0])] = each[1]
    return SongData


def IsContainJapanese(Source):
    SearchRanges = [
        '[\u30a0-\u30ff]',  # Japanese katakana
        '[\u3040-\u3090]',  # Japanese hiragana
    ]
    for Range in SearchRanges:
        if RemoveAll(re.compile(Range).findall(Source), '一'):
            return True
    return False


def IsContainChinese(Source):
    return RemoveAll(re.compile('[\u4e00-\u9fa5]').findall(Source), '一')


def IsOnlyEnglishOrPunctuation(Source):
    SearchRanges = [
        # Num
        '[\u0030-\u0039]',

        # Eng
        '[\u0041-\u005a]',
        '[\u0061-\u0074]',

        # Punctuation
        '[\u3000-\u303f]',
        '[\ufb00-\ufffd]'
    ]
    if Source == " " or Source == "":
        return True
    if IsContainJapanese(Source) or IsContainChinese(Source):
        return False
    for Range in SearchRanges:
        if RemoveAll(re.compile(Range).findall(Source), '一'):
            return True
    return False


if __name__ == '__main__':
    MainProgress = NeteaseMusicStatus()
    while True:
        try:
            MainProgress.Start()
        except Exception:
            MainProgress = NeteaseMusicStatus()
            pass
