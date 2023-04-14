# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 02:30:29
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-14 02:12:26
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\PropertyEnum.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

from enum import Enum
from Debug import *
from abc import abstractclassmethod

class PropertyEnum(Enum):
    __definitions__ = None

    @classmethod
    @property
    def definitions(cls):
        if not cls.__definitions__:
            cls.__definitions__ = dict[cls,dict]()
            for each in cls:
                cls.__definitions__[each] = dict()
            cls.__init_properties__()
        return cls.__definitions__
    
    @abstractclassmethod
    def __init_properties__(cls) -> None:
        return

class enumproperty(property):
    def __set__(self, instance:PropertyEnum, value):
        type(instance).__definitions__[instance][self] = value
    
    def __get__(self, instance:PropertyEnum, cls:type[PropertyEnum]):
        try:
            return cls.definitions[instance][self]
        except KeyError:
            return None