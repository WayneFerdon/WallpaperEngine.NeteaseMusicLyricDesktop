# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:11:09
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-22 03:25:04
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\MainLoop.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import asyncio
import traceback
import threading
import time
from Debug import Debug
from Constants import *

import cProfile

class LoopObject:
    def __init__(self) -> None:
        MainLoop.Register(self)
        return
    
    def OnStart(self):
        return

    def OnUpdate(self):
        return

    def OnFixUpdate(self):
        return

class MainLoop():
    # 静态变量
    Instance=None
    _flag=False
    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance=super().__new__(cls)
        return cls.Instance
    def __init__(self):
        if MainLoop._flag:
            return
        MainLoop._flag=True

        self.CoroutineFixUpdate = self.FixUpdate()
        self.CoroutineUpdate = self.Update()
        self.FixUpdateLoop = asyncio.new_event_loop()
        self.UpdateLoop = asyncio.new_event_loop()
        self.ThreadFixUpdate = threading.Thread(target=self.StartLoop, args=(self.FixUpdateLoop, ))
        self.ThreadUpdate = threading.Thread(target=self.StartLoop, args=(self.UpdateLoop, ))
        self.LoopObjects = list[LoopObject]()

    @staticmethod
    def Register (loopObject:LoopObject):
        if loopObject not in MainLoop.Instance.LoopObjects:
            MainLoop.Instance.LoopObjects.append(loopObject)
    
    @staticmethod
    def StartLoop(loop:asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        loop.run_forever()
    
    @staticmethod
    def Start():
        try:
            for each in MainLoop.Instance.LoopObjects:
                each.OnStart()
            MainLoop.Instance.ThreadFixUpdate.start()
            MainLoop.Instance.ThreadUpdate.start()
            asyncio.run_coroutine_threadsafe(MainLoop.Instance.CoroutineFixUpdate, MainLoop.Instance.FixUpdateLoop)
            asyncio.run_coroutine_threadsafe(MainLoop.Instance.CoroutineUpdate, MainLoop.Instance.UpdateLoop)
        except Exception as e:
            Debug.LogError(e, "\n", traceback.format_exc())
            # MainLoop.Instance.Start()

    @staticmethod
    def OnFixUpdate(interval):
        latestTime = time.time()
        # sleep to prevent Thread lock and conflict with self.Update()
        # time.sleep(0.1)
        for each in MainLoop.Instance.LoopObjects:
            each.OnFixUpdate()
        time.sleep(max(0.001, latestTime + interval - time.time()))
    
    @staticmethod
    def OnUpdate():
            time.sleep(0.001)
            for each in MainLoop.Instance.LoopObjects:
                each.OnUpdate()

    @staticmethod
    async def FixUpdate(interval = 0.01):
        await asyncio.sleep(0)
        while True:
            MainLoop.OnFixUpdate(interval)
    
    @staticmethod
    async def Update():
        await asyncio.sleep(0)
        while True:
            MainLoop.OnUpdate()
            # cProfile.run("OnUpdate()".format())