/*
 * @Author: wayneferdon wayneferdon@hotmail.com
 * @Date: 2021-08-17 01:45:21
 * @LastEditors: WayneFerdon wayneferdon@hotmail.com
 * @LastEditTime: 2023-11-20 10:38:16
 * @FilePath: \NeteaseMusic\module\Netease.js
 * ----------------------------------------------------------------
 * Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
 * Licensed to the .NET Foundation under one or more agreements.
 * The .NET Foundation licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
 */
var LyricOpacity = 0.8
var LyricPositionX = 50
var LyricPositionY = 50
var LyricShowSencends = true
var LyricColor
var LyricBlurColor
var LyricObject = document.getElementById("Netease");
var LastSong = -1
var LastSync = -1
var TimeKeys = []

function LyricInit() {
    LyricObject.style.width = g_Width + 'px';
    LyricObject.style.height = g_Height + 'px';
    document.body.style.setProperty(
        '--lyric_size',
        g_Width + 'px ' + g_Height + 'px'
    );
}

function LyricUpdate() {
    $('#NeteaseState').load('module/NeteaseMusicStatus/CurrentState.json');
    current = JSON.parse($('#NeteaseState').html())
    UpdateLyric(current)
}

function Debug(info) {
    $('#Debug').html(info)
}

function Log(log) {
    $('#Debug').html($('#Debug').html() + "<div id=\"Debug\">" + log + "</div>")
}

function UpdateLyric(current) {
    var currentTime = current["lastPos"] * 1000
    const EMPTY_LYRIC = { "Lyric": null, "Translation": null }
    var currentLyric = [EMPTY_LYRIC, EMPTY_LYRIC, EMPTY_LYRIC]
    switch (current["state"]) {
        case 0: // paused
            break;
        case 1: // playing
            currentTime += Math.max(0, new Date() - current["lastResume"] * 1000)
            break
        case 2: // app exit
            DisplayLyric(currentLyric)
            return
        default:
            break;
    }

    var song = current["song"]
    if (song != LastSong | current["lastSync"] != LastSync) {
        $('#NeteaseLyric').load("module/NeteaseMusicStatus/cache/" + song + ".json");
        LastSong = song
        LastSync = current["lastSync"]
    }
    var SongLyric = JSON.parse($('#NeteaseLyric').html())
    var TimeKeys = []
    i = 0
    for (var key in SongLyric) {
        TimeKeys[i] = key;
        i += 1;
    }
    TimeKeys = TimeKeys.sort(function (a, b) {
        return a - b
    })

    keyTimes = [-Infinity, -1, 0]
    for (var key in TimeKeys) {
        if (TimeKeys[key] >= currentTime) {
            keyTimes[0] = TimeKeys[key - 2]
            keyTimes[1] = TimeKeys[key - 1]
            keyTimes[2] = TimeKeys[key]
            break
        }
    }
    for (var i in keyTimes) {
        time = keyTimes[i]
        if (time == null) {
            continue
        }
        currentLyric[i] = SongLyric[time]
    }
    DisplayLyric(currentLyric)
}

function DisplayLyric(currentLyric) {
    var display = ""
    for (var i in currentLyric) {
        for (var key in currentLyric[i]) {
            line = currentLyric[i][key]
            if (line == null | line == "") {
                line = "<div class=\"LyricEmpty\">...</div > "
            }
            display += "<div class= " + key + i + ">" + line + "</div>"
            // display += "\n"
        }
    }
    $('#NeteaseDisplay').html(display)
}

LyricInit();
setInterval(LyricUpdate, 1)