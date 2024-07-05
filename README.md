<!--
 * @Author: wayneferdon wayneferdon@hotmail.com
 * @Date: 2021-08-17 01:45:17
 * @LastEditors: WayneFerdon wayneferdon@hotmail.com
 * @LastEditTime: 2023-11-14 08:47:10
 * @FilePath: \undefinede:\SteamLibrary\steamapps\common\wallpaper_engine\projects\myprojects\NeteaseMusic\README.md
 * ----------------------------------------------------------------
 * Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
 * Licensed to the .NET Foundation under one or more agreements.
 * The .NET Foundation licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
-->
# WallpaperEngineDesktopWithNeteaseLrcDisplay | WallpaperEngine 网易云歌词桌面



## Introduction | 介绍

Python: 
    
    monitor cloudmusic.elog and analyze it to get current lrc and playing state, which will be cached into module/NeteaseMusicStatus/cache and module/NeteaseMusicStatus/CurrentState.json
    
    监控并分析 cloudmusic.elog 以获取当前歌词及播放状态，并将歌词和状态分别缓存到module/NeteaseMusicStatus/cache 及 module/NeteaseMusicStatus/CurrentState.json 中

JavaScript: 
    
    Update lyric into the wallpaper
    
    将歌词更新到壁纸


## Requirements | 需求

1. [Python 3](https://www.python.org/)

## Usage | 使用方式

1. Run StartNeteaseMusicStatus.bat | 运行 StartNeteaseMusicStatus.bat
2. Selet the wallpaper in Wallpaper Engine | 在 Wallpaper Engine 中选择该壁纸

## Build | 编译

1. Install [requirements](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus/Scripts/requirements) | 安装 [需求文件](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus/Scripts/requirements):

    [Python 3](https://www.python.org/)

    [pykakasi for Python](https://github.com/miurahr/pykakasi)

    [pyinstaller for Python](https://github.com/pyinstaller/pyinstaller)

    [pyncm](https://github.com/mos9527/pyncm)

2. make sure hook file for pykakasi exist | 确保pykakasi的hook文件存在:

    > Python3.x.x/Lib/site-packages/_pyinstaller_hooks_contrib/hooks/hook-pykakasi.py

    if not exist, copy it from | 若不存在，可从下方文件中复制过去
    > ./module/NeteaseMusicStatus/Scripts/hook-pykakasi.py
3. Run ./module/NeteaseMusicStatus/Complie.bat | 运行 ./module/NeteaseMusicStatus/Complie.bat 进行编译

---
Inspire by [another similar method on OS X by Jamesits](https://github.com/Jamesits/Netease-music-status)

受启发于 [来自Jamesits的在OS X上的另一个相似的方式](https://github.com/Jamesits/Netease-music-status)