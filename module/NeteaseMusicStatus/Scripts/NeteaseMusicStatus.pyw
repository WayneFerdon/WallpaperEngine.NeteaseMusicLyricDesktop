# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-08-26 14:44:48
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-22 03:21:18
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\NeteaseMusicStatus.pyw
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# region import
from Debug import Debug
from MainLoop import *
from DisplayManager import *
from ELogMonitor import *
# endregion import

def Main():
    Debug.LogLow("Script Start")
    MainLoop()

    # Init and listen on MainLoop Events by given order
    ELogMonitor()
    DisplayManager()

    MainLoop.Start()

if __name__ == "__main__":
    Main()
