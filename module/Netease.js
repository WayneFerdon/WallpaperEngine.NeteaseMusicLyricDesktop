/*
 * @Author: wayneferdon wayneferdon@hotmail.com
 * @Date: 2021-08-17 01:45:21
 * @LastEditors: WayneFerdon wayneferdon@hotmail.com
 * @LastEditTime: 2023-11-15 04:29:39
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
var Lyric = document.getElementById("Netease");
var LastState = 0

function LyricInit() {
    Lyric.style.width = g_Width + 'px';
    Lyric.style.height = g_Height + 'px';
    document.body.style.setProperty(
        '--lyric_size',
        g_Width + 'px ' + g_Height + 'px'
    );
}

function LyricUpdate() {
    $('#NeteaseState').load('module/NeteaseMusicStatus/CurrentState.html');
    current = JSON.parse($('#NeteaseState').html())
    if (LastState == current) {
        return
    }
    LastState = current
    switch (current["state"]) {
        case 0:
            // $('#NeteaseDebug').html("paused")
            break;
        case 1:
            // $('#NeteaseDebug').html("playing")
            break;
        case 2:
            // $('#NeteaseDebug').html("exited")
            return
        default:
            break;
    }
    UpdateLyric(current)
}

function UpdateLyric(current) {
    var state = current["state"]
    var lastResume = current["lastResume"] * 1000
    var lastPos = current["lastPos"] * 1000
    var song = current["song"]
    var currentTime = lastPos

    $('#NeteaseLyric').load("module/NeteaseMusicStatus/cache/" + song + ".json");
    var lyric = JSON.parse($('#NeteaseLyric').html())
    switch (state) {
        case 0:
            break;
        case 1:
            currentTime += Date.parse(new Date()) - lastResume
        default:
            break;
    }
    const EMPTY_LYRIC = { "Lyric": null, "Translation": null }
    var keyTimes = [null, null, null]
    for (var key in lyric) {
        if (key > currentTime) {
            if (key == 0) {
                keyTimes[0] = null
                keyTimes[1] = key
                continue
            }
            else {
                keyTimes[2] = key
                break
            }
        }
        keyTimes[0] = keyTimes[1]
        keyTimes[1] = key
    }

    currentLyric = [EMPTY_LYRIC, EMPTY_LYRIC, EMPTY_LYRIC]
    for (var i in keyTimes) {
        time = keyTimes[i]
        if (time != null) {
            currentLyric[i] = lyric[time]
        }
    }
    $("#NeteaseDebug").html(JSON.stringify(currentLyric))
    var display = ""
    for (var i in currentLyric) {
        for (var key in currentLyric[i]) {
            line = currentLyric[i][key]
            if (line == null | line == "") {
                line = "<div class=\"LyricEmpty\">\n...</div > "
            }
            display += "<div class= " + key + i + ">" + line + "</div>"
            display += "\n"
        }
    }
    $('#NeteaseDisplay').html(display)
}

LyricInit();
setInterval(LyricUpdate, 1)