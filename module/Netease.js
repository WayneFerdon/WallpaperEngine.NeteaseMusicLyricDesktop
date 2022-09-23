/*
 * @Author: wayneferdon wayneferdon@hotmail.com
 * @Date: 2021-08-17 01:45:21
 * @LastEditors: wayneferdon wayneferdon@hotmail.com
 * @LastEditTime: 2022-08-25 12:38:27
 * @FilePath: \bg\module\Netease.js
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

function LyricInit() {
    Lyric.style.width = g_Width + 'px';
    Lyric.style.height = g_Height + 'px';
    document.body.style.setProperty(
        '--lyric_size',
        g_Width + 'px ' + g_Height + 'px'
    );
}

function LyricUpdate() {
    $('#Netease').load('module/NeteaseMusicStatus/OutPut.html');
}

LyricInit();
setInterval(LyricUpdate, 1)