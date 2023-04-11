# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:11:09
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-12 05:43:42
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
from Singleton import Singleton

class LoopObject:
    def __init__(self) -> None:
        MainLoop.Register(self)
    
    def OnStart(self):
        return

    def OnUpdate(self):
        return

    def OnFixUpdate(self):
        return

class MainLoop(Singleton):
    def __init__(self):
        super().__init__()
        self.CoroutineFixUpdate = MainLoop.FixUpdate()
        self.CoroutineUpdate = MainLoop.Update()
        self.FixUpdateLoop = asyncio.new_event_loop()
        self.UpdateLoop = asyncio.new_event_loop()
        self.ThreadFixUpdate = threading.Thread(target=MainLoop.StartLoop, args=(self.FixUpdateLoop, ))
        self.ThreadUpdate = threading.Thread(target=MainLoop.StartLoop, args=(self.UpdateLoop, ))
        self.LoopObjects = list[LoopObject]()

    @staticmethod
    def StartLoop(loop:asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    @classmethod
    def Register(cls, loopObject:LoopObject):
        if loopObject not in cls.Instance.LoopObjects:
            cls.Instance.LoopObjects.append(loopObject)
    
    @classmethod
    def Start(cls):
        try:
            for each in cls.Instance.LoopObjects:
                each.OnStart()
            cls.Instance.ThreadFixUpdate.start()
            cls.Instance.ThreadUpdate.start()
            asyncio.run_coroutine_threadsafe(cls.Instance.CoroutineFixUpdate, cls.Instance.FixUpdateLoop)
            asyncio.run_coroutine_threadsafe(cls.Instance.CoroutineUpdate, cls.Instance.UpdateLoop)
        except Exception as e:
            Debug.LogError(e, "\n", traceback.format_exc())

    @classmethod
    def OnFixUpdate(cls, interval):
        latestTime = time.time()
        # sleep to prevent Thread lock and conflict with self.Update()
        for each in MainLoop.Instance.LoopObjects:
            each.OnFixUpdate()
        time.sleep(max(0.001, latestTime + interval - time.time()))
    
    @classmethod
    def OnUpdate(cls):
            time.sleep(0.01)
            for each in cls.Instance.LoopObjects:
                each.OnUpdate()

    @classmethod
    async def FixUpdate(cls, interval = 0.01):
        await asyncio.sleep(0)
        while True:
            cls.OnFixUpdate(interval)
    
    @classmethod
    async def Update(cls):
        await asyncio.sleep(0)
        while True:
            cls.OnUpdate()