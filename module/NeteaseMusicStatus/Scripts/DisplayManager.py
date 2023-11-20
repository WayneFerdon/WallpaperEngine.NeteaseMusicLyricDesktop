# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:00:21
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-11-20 05:57:18
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\DisplayManager.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

from Constants import *
from Singleton import Singleton
from MainLoop import LoopObject
from LyricManager import LyricManager
import json

class DisplayManager(Singleton, LoopObject):
    # region main methods
    def __init__(self):
        super().__init__()
        self.LogCount = 0
        self.PlayState = PLAY_STATE.STOPPED

        self.LastResume = 0.0
        self.LastPosition = 0.0
        self.CurrentState = None
        
    def OnStart(self):
        super().OnStart()
        DisplayManager.WriteOutput(EXIT_STATE_OUTPUT)
        if not LyricManager.Song:
            return
        self.OutputCurrentStateAndLyric()

    def OnFixUpdate(self):
        super().OnFixUpdate()
        self.OutputCurrentStateAndLyric()
    # endregion main methods

    # region Lyric methods
    def OutputCurrentStateAndLyric(self):
        state = json.dumps({
            "state": self.PlayState.value,
            "lastResume": self.LastResume,
            "lastPos": self.LastPosition,
            "song": LyricManager.Song,
            "lastSync": LyricManager.LastCache
        })
        DisplayManager.WriteOutput(state)

    @staticmethod
    def WriteOutput(state:str):
        if DisplayManager.Instance.CurrentState == state:
            return
        DisplayManager.Instance.CurrentState = state
        with open(STATE_OUTPUT, "w", encoding= "utf-8") as outPutFile:
            outPutFile.write(state)
    # endregion Lyric methods