# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:50:50
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-12 01:55:09
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
CLOUD_MUSIC = os.path.expanduser(APPDATA + "/Netease/CloudMusic/")
LOGPATH = os.path.join(CLOUD_MUSIC, "cloudmusic.elog")

WEB_DATABASE = os.path.join(CLOUD_MUSIC, "Library/webdb.dat")
WEB_DATABASE_CURSER_KEY = "SELECT tid, track FROM web_track"

LIB_DATABASE = os.path.join(CLOUD_MUSIC, "Library/library.dat")
LIB_DATABASE_CURSER_KEY = "SELECT title, track FROM track"


WEB_DATA_DIR = os.path.join(CLOUD_MUSIC, "webdata/lyric/")
TEMP_DIR = os.path.join(CLOUD_MUSIC, "Temp/")
TEMP_DATABASE = os.path.join(TEMP_DIR, "index.dat")
TEMP_DATABASE_CURSER_KEY = "SELECT path, type FROM cache"

CACHE_DIR = '../cache/'
OUTPUT = "../Output.html"
KANJI_LIB = "Hanzi2Kanji.json"
ZERO_DATETIME = datetime.strptime("0001-01-01T00:00:00.000000+00:00", "%Y-%m-%dT%H:%M:%S.%f%z")

EMPTY_LYRIC = {"Lyric": "", "Translation": ""}
NULL_LYRIC = {0.0 :{"Lyric": "无歌词", "Translation": ""}}
RELOAD_ATTEMPT = 10
INITIAL_SELF_LAST_LOG = "INITIAL_SELF_LAST_LOG"

HARD_FIXS = {
    '君（くん）':{
        'romaMatch':'ki mi',
        'lyricReplace': '君（きみ）',
        'roma': 'kun',
        'romaReplace':'kimi',
    }
}
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
