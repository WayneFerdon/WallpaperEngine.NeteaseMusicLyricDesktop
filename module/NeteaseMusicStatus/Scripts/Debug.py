# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:43:33
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-11-15 00:22:50
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\Debug.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import ctypes
from PropertyEnum import *
from datetime import datetime
import os

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
    class LEVEL(PropertyEnum):
        LOG = 0
        WARNING = 10
        ERROR = 20
        HIGHEST = 2
        HIGH = 1
        LOW = 5
        LOWEST = -2

        @enumproperty
        def enabled(self) -> bool: ...
        @enumproperty
        def isWarp(self) -> bool: ...
        @enumproperty
        def alias(self) -> str: ...
        @enumproperty
        def isDisplayTime(self) -> str: ...

        @classmethod
        def __init_properties__(cls) -> None:
            for level in Debug.LEVEL.definitions:
                level.enabled = True
                level.isWarp = False
                level.isDisplayTime = True
            return super().__init_properties__()

    @staticmethod
    def Pause():
        os.system("pause")

    @staticmethod
    def OnLog(level:LEVEL, infos:list|str, type:int, logTime:datetime=None, isDisplayTime:None|bool=None) -> str:
        if not ENABLE_ELOG_DISPLAY or not level.enabled:
            return
        if not ENABLE_LOG:
            return
        if isDisplayTime is None:
            isDisplayTime = level.isDisplayTime
        
        logInfo = str()
        for info in infos:
            logInfo += str(info) + " "

        timeZone = str()
        if isDisplayTime:
            levelName = level.alias if level.alias else level.name
            if logTime is None:
                logTime = datetime.now()
                timeZone = GetTimeZone()
            form = "[{}]\t{}{}\n{}"
            if not level.isWarp:
                form = form.replace('\n', '\t')
            logInfo = form.format(levelName, logTime, timeZone, logInfo)

        SetCMDDisplay(type)
        print(logInfo)
        with open(PY_LOG_PATH, "a", encoding= "utf-8") as logFile:
            logFile.write(logInfo + "\n")
        ResetCMDDisplay()
        return logInfo

    @staticmethod
    def Log(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.LOG, info, FOREGROUND_BLUE_LIGHT, logTime, isDisplayTime)

    @staticmethod
    def LogWarning(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.WARNING, info, FOREGROUND_YELLOW, logTime, isDisplayTime)

    @staticmethod
    def LogError(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.ERROR, info, FOREGROUND_RED, logTime, isDisplayTime)

    @staticmethod
    def LogHighest(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.HIGHEST, info, FOREGROUND_GREEN, logTime, isDisplayTime)

    @staticmethod
    def LogHigh(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.HIGH, info, FOREGROUND_CYAN, logTime, isDisplayTime)

    @staticmethod
    def LogLow(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.LOW, info, FOREGROUND_BLUE, logTime, isDisplayTime)

    @staticmethod
    def LogLowest(*info, logTime:datetime=None, isDisplayTime:None|bool=None):
        Debug.OnLog(Debug.LEVEL.LOWEST, info, FOREGROUND_GREY, logTime, isDisplayTime)
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
