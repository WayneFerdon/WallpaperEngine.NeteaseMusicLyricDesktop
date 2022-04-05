# wallpaperEngineDesktopWithNeteaseLrcDisplay

## !!!! Version higher than 2.9.2.199190 (not included) is current now **not supported**

Since the cloudmusic.log file is now changed to the new cloudmusic.elog, as well as using a new and unknow encoding.

To download history Versions, use : https://<span>d1.music.126.net/dmusic/cloudmusicsetup.[Version].[Build].exe

For Example, the latest supported version : https://d1.music.126.net/dmusic/cloudmusicsetup2.9.2.199190.exe

If anyone knows what encoding the new log version is using, you may comment in [Issue #1](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/issues/1)


**Introduction:**
python: monitor cloudmusic.log and analyze it to get current lrc and plaing state, then generate html block
javascript: insert html block in to the wallpaper

**Requirements:** 
1. python3
2. other requirement can see imports in [./module/NeteaseMusicStatus.pyw](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus.pyw)
  ([Line 1](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus.pyw#L1) to [Line 12](https://github.com/wayneferdon/WallpaperEngine.NeteaseMusicLyricDesktop/blob/master/module/NeteaseMusicStatus.pyw#L12))

**Usage:**
1. run NeteaseMusicStatus.pyw (defualt by pythonw.exe)
2. Selet this wallpaper in wallpaper engine

Inspire by [another similar method on OS X by Jamesits](https://github.com/Jamesits/Netease-music-status)
