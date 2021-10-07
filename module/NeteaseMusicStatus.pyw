import datetime
import json
import re
import os
from os.path import expanduser
import requests
import time
import sqlite3
from enum import Enum
from pykakasi import kakasi


APPDATA = os.getenv("LOCALAPPDATA")
LOGPATH = expanduser(APPDATA + "/Netease/CloudMusic/cloudmusic.log")
DATABASE = expanduser(APPDATA + "/Netease/CloudMusic/Library/webdb.dat")
OUTPUT = 'OutPut.html'
HEADERS = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64;\x64)\
            AppleWebKit/537.36 (KHTML,like Gecko)\
            Chrome/80.0.3987.87 Safari/537.36'
}


class PlayState(Enum):
    STOPPED = 0
    PLAYING = 1
    EXITED = 2


class LogValidInfo(Enum):
    NONE = 0
    APPEXIT = 1
    PLAY = 2
    LOAD = 3
    SETPOS = 4
    RESUME = 5
    PAUSE = 6


class NeteaseMusicStatus:
    def __init__(self):
        self.PlayState = PlayState.STOPPED
        self.CurrentSong = False
        self.CurrentSongLrc = dict()
        self.CurrentSongLength = 0
        self.LastUpdate = 0
        self.kakasi = kakasi()

        self.LastResumeTime = 0
        self.LastPauseTime = 0
        self.LastPosition = 0
        self.CurrentLrc = [
            {'Lrc': '', 'Translation': ''},
            {'Lrc': '', 'Translation': ''},
            {'Lrc': '', 'Translation': ''}
        ]
        self.NextLrcTime = 0

        self.SongLrcKeyTime = list()
        self.OutPutHtml = str()
        self.LocalMusicInfo = LoadSongDataBase()

        with open("./Hanzi2Kanji.json", "r") as KanjiLib:
            self.Hanzi2KanjiLib = KanjiLib.readlines()
        LibJson = ""
        for line in self.Hanzi2KanjiLib:
            LibJson += line
        self.Hanzi2KanjiLib = json.loads(LibJson)

        try:
            self.LogFile = open(LOGPATH, 'r', encoding='utf-8')
            self.FileSize = os.path.getsize(LOGPATH)
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
        with open(OUTPUT, 'w', encoding='utf-8') as OutPutFile:
            OutPutFile.write('')

        if self.CurrentSong:
            CurrentTimePosition = self.LastPosition
            if self.PlayState == PlayState.PLAYING:
                CurrentTimePosition += time.time() - self.LastResumeTime
            self.GetLrc()
            self.SetCurrentLrc(CurrentTimePosition)
            self.OutPutCurrentLrc()

    def GetLastLines(self, Length):
        FilePath = LOGPATH
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
                    0: {'Lrc': '无歌词', 'Translation': ''},
                    1: {'Lrc': SongName, 'Translation': ''},
                    float("inf"): {'Lrc': SongArtist, 'Translation': ''}
                }
            except KeyError:
                pass
        if not Result:
            Url = 'https://music.163.com/api/song/detail/' \
                  '?id=' + str(self.CurrentSong) + \
                  '&ids=[' + str(self.CurrentSong) + ']'
            JsonDate = json.loads(requests.get(Url, headers=HEADERS).text)
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
                    0: {'Lrc': '无歌词', 'Translation': ''},
                    1: {'Lrc': SongName, 'Translation': ''},
                    float("inf"): {'Lrc': SongArtist, 'Translation': ''}
                }
            else:
                Result[0] = {'Lrc': '无歌词', 'Translation': ''}
        return Result

    def ReloadMonitorPath(self):
        try:
            self.LogFile.close()
        except Exception:
            pass
        try:
            self.LogFile.close()
            self.LogFile = open(LOGPATH, "rb")
            self.FileSize = os.path.getsize(LOGPATH)
            self.LogFile.seek(0, 1)
            return True
        except Exception:
            return False

    def CallbackLog(self, Content, Initializing=False):
        ValidInfo = LogValidInfo.NONE
        LogTime = 0

        if 'App exit' in Content:
            if self.PlayState == PlayState.PLAYING:
                self.LastPosition += time.time() - self.LastResumeTime
            self.PlayState = PlayState.EXITED
            LogTime = time.time()
            ValidInfo = LogValidInfo.APPEXIT

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
                if self.PlayState != PlayState.EXITED:
                    self.LastPosition = 0

                # require load and resume
                self.PlayState = PlayState.STOPPED
                ValidInfo = LogValidInfo.PLAY
            elif '__onAudioPlayerLoad' in LogInfo:
                self.CurrentSongLength = json.loads(
                    re.split('\t', LogInfo)[0])['duration']
                ValidInfo = LogValidInfo.LOAD
            elif '_$setPosition' in LogInfo:
                self.LastPosition = json.loads(re.split('\t', LogInfo)[0])[
                    'ratio'] * self.CurrentSongLength
                ValidInfo = LogValidInfo.SETPOS
                if self.PlayState == PlayState.PLAYING:
                    if Initializing:
                        self.LastResumeTime = LogTime
                    else:
                        self.LastResumeTime = time.time()
            elif 'player._$resume do' in LogInfo:
                self.PlayState = PlayState.PLAYING
                self.LastResumeTime = LogTime
                ValidInfo = LogValidInfo.RESUME
            elif 'player._$pause do' in LogInfo:
                ValidInfo = LogValidInfo.PAUSE
                if self.PlayState == PlayState.PLAYING:
                    self.PlayState = PlayState.STOPPED
                    self.LastPosition += LogTime - self.LastResumeTime
                    self.LastPauseTime = LogTime
        if ValidInfo == LogValidInfo.NONE:
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
        if ValidInfo in [LogValidInfo.SETPOS, LogValidInfo.RESUME]:
            self.SetCurrentLrc(self.LastPosition)
            self.OutPutCurrentLrc()
        if ValidInfo == LogValidInfo.APPEXIT:
            with open(OUTPUT, 'w', encoding='utf-8') as OutPutFile:
                OutPutFile.write('')
        return True

    def Start(self, Interval=0.001):
        LogFile = LOGPATH
        while True:
            FileSize = os.path.getsize(LogFile)
            if FileSize < self.FileSize:
                TryCount = 0
                while TryCount < 10:
                    if not self.ReloadMonitorPath():
                        TryCount += 1
                    else:
                        TryCount = 0
                        self.FileSize = os.path.getsize(LogFile)
                        break
                    time.sleep(0.1)

                if TryCount == 10:
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
            if self.PlayState == PlayState.PLAYING:
                self.SetCurrentLrc()
                self.OutPutCurrentLrc()

    def OutPutCurrentLrc(self):
        NewOutPut = GetOutPut(self.CurrentLrc)
        if NewOutPut == self.OutPutHtml:
            return
        with open(OUTPUT, 'w', encoding='utf-8') as OutPutFile:
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

    def GetHiraganaLrc(self, Lrc):
        LrcSplit = list()
        for Split in Lrc:
            for each in self.kakasi.convert(Split):
                for Item in SplitAll(each['orig'], "(（.*?）){1}"):
                    LrcSplit += self.kakasi.convert(Item)
        LrcConverted = ""
        LrcRomajinn = ""
        PriorHira = ""
        IsPreJP = True

        for Split in LrcSplit:
            orig = Split['orig']
            hira = Split['hira']
            roma = Split['hepburn']
            if not IsPreJP:
                orig = orig.replace("　", " ")
            if IsOnlyEnglishOrPunctuation(orig):
                LrcConverted += orig + " "
                LrcRomajinn += orig + " "
                PriorHira = ""
                IsPreJP = False
                continue
            IsPreJP = True
            if hira == "":
                KanjiLrc = ""
                for EachStr in orig:
                    if EachStr in self.Hanzi2KanjiLib.keys():
                        KanjiLrc += self.Hanzi2KanjiLib[EachStr][0]
                    else:
                        KanjiLrc += EachStr
                orig = KanjiLrc
                hira = ""
                roma = ""
                for newEach in kakasi().convert(orig):
                    hira += newEach['hira']
                    roma += newEach['hepburn']
            if hira == orig:
                if hira == PriorHira:
                    orig = ""
                    roma = ""
                PriorHira = ""
            else:
                PriorHira = "（" + hira + "）"
            LrcConverted += orig + PriorHira
            LrcRomajinn += roma + " "

        return {
            "Lrc": LrcConverted,
            "Roma": LrcRomajinn
        }

    def SplitLrc(self, Lrc):
        Lrc = Lrc\
            .replace("(", "（")\
            .replace(")", "）")\
            .replace(" ", "　")\
            .replace("　", "//split//　//split//")\
            .replace("、", "//split//、//split//")\
            .replace("。", "//split//、//split//")
        Lrc = re.split("//split//", Lrc)
        LrcSplit = list()
        Index = -1
        while Index >= -len(Lrc):
            Item = Lrc[Index]
            if(Item is None):
                Index -= 2
            else:
                Index -= 1
                LrcSplit.append(Item)
        LrcSplit.reverse()
        Lrc = RemoveAll(LrcSplit, "")
        return Lrc

    def FormatLrc(self, Lrc, Translation):
        def SimpleFormat(Source):
            Source = ReplaceAll(Source, " 　", "　")
            Source = ReplaceAll(Source, "　 ", "　")
            Source = ReplaceAll(Source, "（ ", "（")
            return Source.replace("　:", " :").replace(":　", ": ")

        Roma = SimpleFormat(Lrc['Roma'])
        Lrc = SimpleFormat(Lrc['Lrc'])
        if IsOnlyEnglishOrPunctuation(Lrc):
            Lrc = Lrc.replace("　", " ")
        if Translation != "":
            Translation += " / "
        Translation += Roma

        return {
            "Lrc": ReplaceAll(Lrc, "  ", " "),
            "Translation": ReplaceAll(Translation, "  ", " ")
        }

    def GetConvertedLrc(self, SplitTimeLrc, SplitTimeTranslation, IsJapanese):
        Result = dict()
        for TimeItem in SplitTimeLrc.keys():
            Lrc = SplitTimeLrc[TimeItem]
            if TimeItem in SplitTimeTranslation.keys():
                Translation = SplitTimeTranslation[TimeItem]
            else:
                Translation = ""
            Result[TimeItem] = {
                "Lrc": Lrc,
                "Translation": Translation
            }
            if not IsJapanese:
                Result[TimeItem] = {
                    "Lrc": Lrc,
                    "Translation": Translation
                }
                continue
            Lrc = self.SplitLrc(Lrc)
            Lrc = self.GetHiraganaLrc(Lrc)
            Lrc = self.FormatLrc(Lrc, Translation)

            # Testing : Unavailable
            # Duplicate = re.compile("（.*?）（.*?）")\
            #     .findall(Lrc["Lrc"])
            # DuplicateList = list()
            # for Pair in Duplicate:
            #     DuplicateList.append(
            #         re.compile("）.*?（）.*?（").findall(Pair[::-1])[0][::-1]
            #     )
            #     print(DuplicateList[-1])
            # End Testing

            Result[TimeItem] = Lrc
        return Result

    def GetLrc(self):
        self.CurrentLrc = [
            {'Lrc': '', 'Translation': ''},
            {'Lrc': '', 'Translation': ''},
            {'Lrc': '', 'Translation': ''}
        ]
        Url = "http://music.163.com/api/song/lyric?" +\
            "id=" + str(self.CurrentSong) + "&lv=1&kv=1&tv=-1"
        JsonDate = json.loads(requests.get(Url, headers=HEADERS).text)
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
                    or self.PlayState != PlayState.PLAYING
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
                except Exception as e:
                    # print(e)
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
            except Exception as e:
                # print(e)
                pass


def RemoveAll(Source, Target):
    while Target in Source:
        Source.remove(Target)
    return Source


def ReplaceAll(Source, Target, New):
    while Target in Source:
        Source = Source.replace(Target, New)
    return Source


def SplitAll(Source, Target, Retainterget=True):
    FindResult = re.compile(Target).findall(Source)
    NewList = list()
    if FindResult:
        FindResult = FindResult[0]
        if isinstance(FindResult, tuple):
            FindResult = FindResult[0]
        Source = Source.split(FindResult)
        for Key in range(len(Source)):
            Result = SplitAll(Source[Key], Target)
            if Result:
                NewList += Result
            else:
                NewList.append(Source[Key])
            if(Retainterget and Key != len(Source)-1):
                NewList.append(FindResult)
        RemoveAll(NewList, "")
        return NewList
    NewList.append(Source)
    RemoveAll(NewList, "")
    return NewList


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
    cursor = sqlite3.connect(DATABASE).cursor()
    CursorResults = cursor.execute(
        'SELECT tid, track '
        'FROM web_track'
    ).fetchall()
    cursor.close()
    SongData = dict()
    for Result in CursorResults:
        SongData[str(Result[0])] = Result[1]
    return SongData


def IsContainJapanese(Source):
    SearchRanges = [
        '[\u3040-\u3090]',  # hiragana
        '[\u30a0-\u30ff]'   # katakana
    ]
    for Range in SearchRanges:
        if RemoveAll(re.compile(Range).findall(Source), '一'):
            return True
    return False


def IsContainChinese(Source):
    return RemoveAll(re.compile('[\u4e00-\u9fa5]').findall(Source), '一')


def IsOnlyEnglishOrPunctuation(Source):
    SearchRanges = [
        '[\u0000-\u007f]',
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
        except Exception as e:
            # print(e)
            MainProgress = NeteaseMusicStatus()
            pass
