# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-11-22 00:48:47
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-11-22 00:48:47
# FilePath: \NeteaseMusic\module\NeteaseMusicStatus\Scripts\CharaterMethods.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import re

def RemoveAll(source:list[str]|str, target:str) -> list[str]|str:
    while target in source:
        source.remove(target)
    return source

def ReplaceAll(source:str, target:str, replacement:str):
    while target in source:
        source = source.replace(target, replacement)
    return source

def SplitAll(source:str, target:str, retainterget= True) -> list[str]:
    findResult = re.compile(target).findall(source)
    newList = list()
    if findResult:
        findResult = findResult[0]
        if isinstance(findResult, tuple):
            findResult = findResult[0]
        source = source.split(findResult)
        for key in range(len(source)):
            result = SplitAll(source[key], target)
            if result:
                newList += result
            else:
                newList.append(source[key])
            if(retainterget and key != len(source)-1):
                newList.append(findResult)
        RemoveAll(newList, "")
        return newList
    newList.append(source)
    RemoveAll(newList, "")
    return newList
# endregion common string methods

# region common charater methods
def IsContainJapanese(source:str) -> bool:
    searchRanges = [
        "[\u3040-\u3090]", # hiragana
        "[\u30a0-\u30ff]"   # katakana
    ]
    for range in searchRanges:
        if RemoveAll(re.compile(range).findall(source), "一"):
            return True
    return False

def IsContainChinese(source:str) -> bool:
    if RemoveAll(re.compile("[\u4e00-\u9fa5]").findall(source), "一"):
        return True
    return False

def IsOnlyEnglishOrPunctuation(source):
    searchRanges = [
        "[\u0000-\u007f]", 
        "[\u3000-\u303f]", 
        "[\ufb00-\ufffd]"
    ]
    if source == " " or source == "":
        return True
    if IsContainJapanese(source) or IsContainChinese(source):
        return False
    for range in searchRanges:
        if RemoveAll(re.compile(range).findall(source), "一"):
            return True
    return False