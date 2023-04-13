# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:00:21
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-13 02:35:37
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\DisplayManager.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import time
import traceback
from Constants import *
from Debug import Debug
from Singleton import Singleton
from MainLoop import LoopObject
from LyricManager import LyricManager

class DisplayManager(Singleton, LoopObject):
    # region main methods
    def __init__(self):
        super().__init__()
        self.LogCount = 0
        self.PlayState = PLAY_STATE.STOPPED

        self.LastResume = 0.0
        self.LastPause = 0.0
        self.LastPosition = 0.0
        self.CurrentLyric = None
        
        self.NextLyricTime = 0.0
        self.OutputHtml = ""
    
    def OnStart(self):
        super().OnStart()
        self.CurrentLyric = [EMPTY_LYRIC] * 3
        DisplayManager.WriteOutput("")
        if not LyricManager.Song:
            return
        LyricManager.PrepareLyric()
        LyricManager.LastSyncAttemp = None
        self.OutputCurrentLyric(True)

    def OnFixUpdate(self):
        super().OnFixUpdate()
        self.OutputCurrentLyric()
    
    # def OnUpdate(self):
    #     super().OnUpdate()
    # endregion main methods

    # region Lyric methods
    def OutputCurrentLyric(self, isSetPos:bool=False):
        if not isSetPos:
            if not self.AutoUpdateCurrentLyric():
                return
        else:
            targetTime = self.LastPosition
            if self.PlayState == PLAY_STATE.PLAYING:
                targetTime += time.time() - self.LastResume
            if not self.SetCurrentLyric(targetTime):
                return
        output = self.GetOutput()
        if output == self.OutputHtml:
            return
        self.OutputHtml = output
        DisplayManager.WriteOutput(self.OutputHtml)

    def AutoUpdateCurrentLyric(self):
        if self.PlayState != PLAY_STATE.PLAYING:
            return False
        if self.NextLyricTime is None:
            return False
        currentTime = time.time() - self.LastResume + self.LastPosition
        if (currentTime * 1000 < self.NextLyricTime):
            return False
        try:
            self.CurrentLyric[0] = self.CurrentLyric[1]
            self.CurrentLyric[1] = self.CurrentLyric[2]
            songMGR = LyricManager
            index = songMGR.Timeline.index(self.NextLyricTime)
            if len(songMGR.Timeline) <= index + 1:
                self.NextLyricTime = None
                self.CurrentLyric[2] = EMPTY_LYRIC
                return True
            self.NextLyricTime = songMGR.Timeline[index + 1]
            self.CurrentLyric[2] = songMGR.Lyric[self.NextLyricTime]
            return True
        except IndexError as e:
            pass
        except Exception as e:
            Debug.LogError(e, "\n", traceback.format_exc())
        finally:
            return True

    def SetCurrentLyric(self, targetTime:float):
        keyTime = None
        songMGR = LyricManager
        for keyTime in songMGR.Timeline:
            if keyTime >= targetTime * 1000:
                break
        try:
            index = songMGR.Timeline.index(keyTime)

            currLrcT = songMGR.Timeline[index - 1]

            self.NextLyricTime = None
            self.CurrentLyric = [EMPTY_LYRIC] * 3

            self.CurrentLyric[1] = songMGR.Lyric[currLrcT]
            if len(songMGR.Timeline) > 1:
                if index > 1:
                    prevLrcT = songMGR.Timeline[index - 2]
                    self.CurrentLyric[0] = songMGR.Lyric[prevLrcT]
                self.NextLyricTime = songMGR.Timeline[index]
                self.CurrentLyric[2] = songMGR.Lyric[self.NextLyricTime]
            return True
        except Exception as e:
            Debug.LogError(e, "\n", traceback.format_exc())
            return False

    def GetOutput(self):
        outPut = ""
        for i in range(3):
            for key in self.CurrentLyric[i]:
                lyric = self.CurrentLyric[i][key]
                if not lyric:
                    lyric = ""
                outPut += "<div class= " + key + str(i) + ">" + lyric + "</div>"
                outPut += "\n"
        return outPut

    @staticmethod
    def WriteOutput(data:str):
        with open(OUTPUT, "w", encoding= "utf-8") as outPutFile:
            outPutFile.write(data)
    # endregion Lyric methods