# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-12 05:18:18
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-14 02:30:17
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\Singleton.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

class Singleton():
    __Instance__=None
    __flag__=False

    def __new__(cls, *args, **kwargs):
        if not cls.__Instance__:
            cls.__Instance__=super().__new__(cls)
        return cls.__Instance__

    def __init__(self):
        if type(self).__flag__:
            return
        type(self).__flag__ = True
        super().__init__()

    @classmethod
    @property
    def Instance(cls):
        if cls.__Instance__:
            return cls.__Instance__
        cls.__Instance__ = cls.__new__()
        return cls.__Instance__
