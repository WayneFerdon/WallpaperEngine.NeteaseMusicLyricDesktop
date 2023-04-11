<!--
 * @Author: wayneferdon wayneferdon@hotmail.com
 * @Date: 2021-08-17 01:45:17
 * @LastEditors: wayneferdon wayneferdon@hotmail.com
 * @LastEditTime: 2022-08-25 13:49:28
 * @FilePath: \undefinede:\SteamLibrary\steamapps\common\wallpaper_engine\projects\myprojects\bg\README.md
 * ----------------------------------------------------------------
 * Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
 * Licensed to the .NET Foundation under one or more agreements.
 * The .NET Foundation licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
-->
# wallpaperEngineDesktopWithNeteaseLrcDisplay

---

## Introduction

Python: monitor cloudmusic.log and analyze it to get current lrc and plaing state, then generate html block

JavaScript: Insert the generated html block into the wallpaper

## Requirements

1. [Python 3](https://www.python.org/)

## Usage

1. Run StartNeteaseMusicStatus.bat
2. Selet the wallpaper in Wallpaper Engine

## Build

1. Install [requirements](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus/Scripts/requirements):

    [Python 3](https://www.python.org/)

    [pykakasi for Python](https://github.com/miurahr/pykakasi)

    [pyinstaller for Python](https://github.com/pyinstaller/pyinstaller)

    [pyncm](https://github.com/mos9527/pyncm)

2. make sure hook file for pykakasi exist:

    > Python3.x.x/Lib/site-packages/_pyinstaller_hooks_contrib/hooks/hook-pykakasi.py

    if not exist, copy it from
    > ./module/NeteaseMusicStatus/Scripts/hook-pykakasi.py
3. Run ./module/NeteaseMusicStatus/Complie.bat

## Notes

Since the cloudmusic.log file is now changed to the new cloudmusic.elog, as well as using a new and unknow encoding. Currently some relation has been tried and works fine, yet if anyone knows what encoding the new log version is using may comment in [Issue #1](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/issues/1)

---
Inspire by [another similar method on OS X by Jamesits](https://github.com/Jamesits/Netease-music-status)
