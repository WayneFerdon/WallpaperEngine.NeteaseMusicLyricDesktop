# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:50:50
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-11-20 06:00:18
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
import json

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
STATE_OUTPUT = "../CurrentState.json"
KANJI_LIB = "Hanzi2Kanji.json"

EMPTY_LYRIC = {"Lyric": "", "Translation": ""}
RELOAD_ATTEMPT = 10
EXIT_STATE_OUTPUT = json.dumps({"state":2})

HARD_FIXS = {
    '君（くん）':{
        'roma': 'kun',
        'romaMatch': 'ki mi',
        'lyricReplace': '君（きみ）',
    },
    '人（にん）':{
        'roma': 'nin',
        'romaMatch': 'hi to',
        'lyricReplace': '人（ひと）',
    },
    '失（う）':{
        'roma': 'u',
        'romaMatch': 'u shi na',
        'lyricReplace': '失（うしな）',
    },
    '泡沫（ほうまつ）':{
        'roma': 'houmotsu',
        'romaMatch': 'u ta ka ta',
        'lyricReplace': '泡沫（うたかた）',
    },
    '齣（こま）':{
        'roma': 'koma',
        'romaMatch': 'de',
        'lyricReplace': '齣（で）',
    },
    '日（にち）':{
        'roma': 'nichi',
        'romaMatch': 'hi',
        'lyricReplace': '日（ひ）',
    },
    '士（さむらい）':{
        'roma': 'samurai',
        'romaMatch': 'shi',
        'lyricReplace': '士（し）',
    },
    '落ち着（おちつ）':{
        'roma': 'ochitsu',
        'romaMatch': 'o chi tsu',
        'lyricReplace': '落（お）ち着（つ）',
    },
    '時（とき）':{
        'roma': 'toki',
        'romaMatch': 'ji',
        'lyricReplace': '時（じ）',
    },
    '今日（こんにち）':{
        'roma': 'konnnichi',
        'romaMatch': 'kyo',
        'lyricReplace': '今日（きょ）',
    },
    '今年（こんねん）':{
        'roma': 'konnnenn',
        'romaMatch': 'ko to shi',
        'lyricReplace': '今年（ことし）',
    },
    '経（へ）':{
        'roma': 'he',
        'romaMatch': 'ta',
        'lyricReplace': '経（た）',
    },
    '点（てん）':{
        'roma': 'tenn',
        'romaMatch': 'tsu',
        'lyricReplace': '点（つ）',
    },
    'LYRIC_TO_BE_FIXED':{
        'roma': 'ROMA_TO_BE_FIXED',
        'romaMatch': 'FIX_IF_MATCH_IN_ROMA_SOURCE',
        'lyricReplace': 'FIX_USING_THIS_REPLACEMENT',
    },
}
# endregion paths and default values
# endregion constants

# region enums
class PLAY_STATE(Enum):
    STOPPED = 0
    PLAYING = 1
    EXITED = 2

