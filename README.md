# wallpaperEngineDesktopWithNeteaseLrcDisplay
---
## Introduction

Python: monitor cloudmusic.log and analyze it to get current lrc and plaing state, then generate html block
 
JavaScript: Insert the generated html block into the wallpaper

## Requirements
1. [Python 3](https://www.python.org/)
2. [pykakasi for Python](https://github.com/miurahr/pykakasi)
  >pip install pykakasi
3. other requirement can see imports in [./module/NeteaseMusicStatus.pyw](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus.pyw)
  ([Line 3](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus.pyw#L3) to [Line 10](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus.pyw#L10))

## Usage
1. Run NeteaseMusicStatus.pyw (defualt by pythonw.exe)
2. Selet this wallpaper in wallpaper engine

## Notes
Inspire by [another similar method on OS X by Jamesits](https://github.com/Jamesits/Netease-music-status)
---
Since the cloudmusic.log file is now changed to the new cloudmusic.elog, as well as using a new and unknow encoding. Currently some relation has been tried and works fine, yet if anyone knows what encoding the new log version is using may comment in [Issue #1](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/issues/1)
