# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:50:50
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-22 00:50:52
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\Constants.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os
from enum import Enum
from datetime import datetime

# region constants
# region paths and default values
APPDATA = os.getenv("LOCALAPPDATA")
LOGPATH = os.path.expanduser(APPDATA + "/Netease/CloudMusic/cloudmusic.elog")
DATABASE = os.path.expanduser(APPDATA + "/Netease/CloudMusic/Library/webdb.dat")
DATABASE_CURSER_KEY = "SELECT tid, track FROM web_track"
OUTPUT = "../OutPut.html"
KANJI_LIB = "Hanzi2Kanji.json"
HEADERS = {
    "user-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64;\x64)\
            AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/80.0.3987.87 Safari/537.36"
}
ZERO_DATETIME = datetime.strptime("0001-01-01T00:00:00.000000+00:00", "%Y-%m-%dT%H:%M:%S.%f%z")

EMPTY_LYRIC = {"Lyric": "", "Translation": ""}
NULL_LYRIC = {0.0 :{"Lyric": "无歌词", "Translation": ""}}
RELOAD_ATTEMPT = 10
INITIAL_SELF_LAST_LOG = "INITIAL_SELF_LAST_LOG"
# endregion paths and default values
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
