/*
 * @Author: wayneferdon wayneferdon@hotmail.com
 * @Date: 2022-08-06 15:13:29
 * @LastEditors: wayneferdon wayneferdon@hotmail.com
 * @LastEditLyric: 2022-08-06 15:13:51
 * @FilePath: \bg\js\LyricSetting.js
 * ----------------------------------------------------------------
 * Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
 * Licensed to the .NET Foundation under one or more agreements.
 * The .NET Foundation licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
 */

var LyricSettingsObject = {};
var LyricSettings = function (Settings) {
    if (Settings.ShowLyric) {
        LyricSettingsObject.Show = Settings.ShowLyric.value;
        if (!LyricSettingsObject.Show) {
            SetShowLyric(false);
        }
        else {
            SetShowLyric(true);
        }
    }
    if (Settings.LyricAlignment) {
        LyricSettingsObject.Align = Settings.LyricAlignment.value;
        Lyric.style.textAlign = LyricSettingsObject.Align;
        if (Settings.LyricAlignment.value == 'left') {
            LyricSettingsObject.AlignPX = 40;
        }
        else if (Settings.LyricAlignment.value == 'right') {
            LyricSettingsObject.AlignPX = -40;
        }
        else {
            LyricSettingsObject.AlignPX = 0;
        }
        Lyric.style.left = LyricPositionX - 50 + LyricSettingsObject.AlignPX + '%';
    }
    if (Settings.LyricFont) {
        if (isNaN(Settings.LyricFont.value) && Settings.LyricFont.value) {
            SetFont(Settings.LyricFont.value);
            Lyric.style.fontFamily = Settings.LyricFont.value.replace(/:/g, ' ') + ", sans-serif";
        }
        else {
            SetOldFont(Lyric, Settings.LyricFont.value);
        }
    }
    if (Settings.LyricFontDir) {
        if (Settings.LyricFontDir.value) {
            Lyric.style.fontFamily = "'Custom-eV', sans-serif";
            SetFontCustom(Settings.LyricFontDir.value, 'Custom-eV');
        }
    }
    if (Settings.LyricShowSencends) {
        LyricShowSencends = Settings.LyricShowSencends.value;
    }
    if (Settings.LyricSize) {
        var s = Settings.LyricSize.value;
        Lyric.style.fontSize = Math.floor(g_Height / 500 * s) + 'px';
        document.body.style.setProperty('--lyric_size', (s / 100) + 'vmax');
    }
    if (Settings.LyricColor) {
        var c = Settings.LyricColor.value.split(' ').map(
            function (c) {
                return Math.ceil(c * 255);
            }
        );
        Lyric.style.color = LyricColor = 'rgb(' + c + ')';
        document.body.style.setProperty('--lyric_color', LyricColor);
    }
    if (Settings.LyricBlurColor) {
        var c = Settings.LyricBlurColor.value.split(' ').map(
            function (c) {
                return Math.ceil(c * 255);
            }
        );
        Lyric.style.textShadow = LyricBlurColor = '0 0 20px rgb(' + c + ')';
        LyricSettingsObject.Blur = 'rgb(' + c + ')';
        document.body.style.setProperty('--lyric_blur', LyricSettingsObject.Blur);
    }
    if (Settings.LyricPositionX) {
        LyricPositionX = Settings.LyricPositionX.value;
        Lyric.style.left = LyricPositionX - 50 + LyricSettingsObject.AlignPX + '%';
        document.body.style.setProperty(
            '--lyric_pos',
            LyricPositionX + (LyricPositionX * (((window.innerWidth / 64) / 100) * 2)) - (window.innerWidth / 64) + '% ' + (LyricPositionY - (LyricPositionY * 0.04) + 2) + '%'
        );
    }
    if (Settings.LyricPositionY) {
        LyricPositionY = Settings.LyricPositionY.value;
        Lyric.style.top = LyricPositionY - 50 + '%';
        document.body.style.setProperty(
            '--lyric_pos',
            LyricPositionX + (LyricPositionX * (((window.innerWidth / 64) / 100) * 2)) - (window.innerWidth / 64) + '% ' + (LyricPositionY - (LyricPositionY * 0.04) + 2) + '%'
        );
    }
    if (Settings.LyricOpacity) {
        LyricOpacity = Settings.LyricOpacity.value / 100;
        Lyric.style.opacity = LyricOpacity;
    }
}

function SetShowLyric(IsShow) {
    if (IsShow) {
        Lyric.style.display = 'block';
    }
    else {
        Lyric.style.display = 'none';
    }
}