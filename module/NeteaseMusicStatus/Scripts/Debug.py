# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:43:33
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-13 07:49:47
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\Debug.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import ctypes
from enum import Enum
from datetime import datetime

# region log display switch
ENABLE_ELOG_DISPLAY = True
ENABLE_LOG = True
PY_LOG_PATH = "../PyLog.log"
# endregion log display switch

# region print color
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
# text colors
FOREGROUND_BLUE = 0x01  # blue.
FOREGROUND_GREY = 0x08  # grey.
FOREGROUND_BLUE_LIGHT = 0x09  # blue light.
FOREGROUND_GREEN = 0x0a  # green.
FOREGROUND_CYAN = 0x0b  # cyan.
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

# region class Log
class Debug():
    class LEVEL(Enum):
        LOG = 0
        LOW = 1
        ALERT = 2
        ERROR = 3
        ELOG = 4
        ELOG_PLAYER = 5
        ELOG_LOW = 6

        __all__ = None

        @classmethod
        @property
        def all(cls):
            if not cls.__all__:
                cls.__all__ = {
                    cls.LOG: {
                        cls.enabled:True,
                        cls.isWarp:False
                    },
                    cls.LOW: {
                        cls.enabled:True,
                        cls.isWarp:False
                    },
                    cls.ALERT: {
                        cls.enabled:True,
                        cls.isWarp:False
                    },
                    cls.ERROR: {
                        cls.enabled:True,
                        cls.isWarp:False
                    },
                    cls.ELOG: {
                        cls.enabled:True,
                        cls.isWarp:True
                    },
                    cls.ELOG_PLAYER: {
                        cls.enabled:True,
                        cls.isWarp:True
                    },
                    cls.ELOG_LOW: {
                        cls.enabled:False,
                        cls.enabled:True,
                        cls.isWarp:True,
                    },
                }
            return cls.__all__
    
        @property
        def enabled(self):
            return Debug.LEVEL.all[self][Debug.LEVEL.enabled]
        
        @property
        def isWarp(self):
            return Debug.LEVEL.all[self][Debug.LEVEL.isWarp]

    @classmethod
    def OnLog(cls, level:LEVEL, infos:str, type:int, time:datetime= None) -> str:
        if not ENABLE_ELOG_DISPLAY or not level.enabled:
            return
        timeZone = ""
        if time is None:
            time = datetime.now()
            timeZone = GetTimeZone()
        if not ENABLE_LOG:
            return
        logInfo = ""
        for each in infos:
            logInfo += str(each) + " "
        form = "[{}]\t{}{}\n{}"
        if not level.isWarp:
            form = form.replace('\n', '\t')
        logInfo = form.format(level.name, time, timeZone, logInfo)
        SetCMDDisplay(type)
        print(logInfo)
        with open(PY_LOG_PATH, "a", encoding= "utf-8") as logFile:
            logFile.write(logInfo + "\n")
        ResetCMDDisplay()
        return logInfo

    @staticmethod
    def Log(time:datetime, *info):
        Debug.OnLog(Debug.LEVEL.LOG, info, FOREGROUND_GREEN, time)

    @staticmethod
    def LogLow(*info):
        Debug.OnLog(Debug.LEVEL.LOW, info, FOREGROUND_BLUE_LIGHT)

    @staticmethod
    def LogAlert(*info):
        Debug.OnLog(Debug.LEVEL.ALERT, info, FOREGROUND_YELLOW)

    @staticmethod
    def LogError(*info):
        Debug.OnLog(Debug.LEVEL.ERROR, info, FOREGROUND_RED)

    @staticmethod
    def LogElog(*info):
        Debug.OnLog(Debug.LEVEL.ELOG, info, FOREGROUND_CYAN)

    @staticmethod
    def LogElogPlayer(*info):
        Debug.OnLog(Debug.LEVEL.ELOG, info, FOREGROUND_BLUE)

    @staticmethod
    def LogElogLow(*info):
        Debug.OnLog(Debug.LEVEL.ELOG_LOW, info, FOREGROUND_GREY)
# endregion class Log

# region common time methods
def GetTimeZone() -> str:
    zone = int((datetime.now() - datetime.utcnow()).seconds/3600)
    if zone >= 0:
        sign = "+"
    else:
        sign = "-"
        zone = -zone
    timeZone = str(zone)
    if zone < 10:
        timeZone = "0" + timeZone
    timeZone = "{}:00".format(sign + timeZone)
    return timeZone
# endregion common time methods

# region print color methods
def SetCMDDisplay(type:int):
    ctypes.windll.kernel32.SetConsoleTextAttribute(STD_OUT_HANDLE, type)

def ResetCMDDisplay():
    SetCMDDisplay(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE_LIGHT)
# endregion constants
