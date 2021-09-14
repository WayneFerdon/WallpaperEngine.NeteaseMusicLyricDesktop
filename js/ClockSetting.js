var ClockSettingsObject = {};
var ClockSettings = function (Settings) {
    if (Settings.ShowTime) {
        ClockSettingsObject.Show = Settings.ShowTime.value;
        if (!ClockSettingsObject.Show) {
            SetShowClock(false);
        }
        else {
            SetShowClock(true);
        }
    }
    if (Settings.TimeAlignment) {
        ClockSettingsObject.Align = Settings.TimeAlignment.value;
        Clock.style.textAlign = ClockSettingsObject.Align;
        if (Settings.TimeAlignment.value == 'left') {
            ClockSettingsObject.AlignPX = 40;
        }
        else if (Settings.TimeAlignment.value == 'right') {
            ClockSettingsObject.AlignPX = -40;
        }
        else {
            ClockSettingsObject.AlignPX = 0;
        }
        Clock.style.left = TimePositionX - 50 + ClockSettingsObject.AlignPX + '%';
    }
    if (Settings.TimeFont) {
        if (isNaN(Settings.TimeFont.value) && Settings.TimeFont.value) {
            SetFont(Settings.TimeFont.value);
            Clock.style.fontFamily = Settings.TimeFont.value.replace(/:/g, ' ') + ", sans-serif";
        }
        else {
            SetOldFont(Clock, Settings.TimeFont.value);
        }
    }
    if (Settings.TimeFontDir) {
        if (Settings.TimeFontDir.value) {
            Clock.style.fontFamily = "'Custom-eV', sans-serif";
            SetFontCustom(Settings.TimeFontDir.value, 'Custom-eV');
        }
    }
    if (Settings.TimeShowSencends) {
        TimeShowSencends = Settings.TimeShowSencends.value;
    }
    if (Settings.TimeSize) {
        var s = Settings.TimeSize.value;
        Clock.style.fontSize = Math.floor(g_Height / 300 * s) + 'px';
        document.body.style.setProperty('--digit_size3', (s / 5) + 'vmin');
        document.body.style.setProperty('--digit_size2', (s / 2.5) + 'vmin');
        document.body.style.setProperty('--digit_size', (s / 100) + 'vmax');
        document.body.style.setProperty('--digit_size1', (s / 50) + 'vmax');
        document.body.style.setProperty('--slide_size', MathMap(s, 0, 50, 10, 100) + 'px');
    }
    if (Settings.TimeColor) {
        var c = Settings.TimeColor.value.split(' ').map(
            function (c) {
                return Math.ceil(c * 255);
            }
        );
        Clock.style.color = TimeColor = 'rgb(' + c + ')';
        document.body.style.setProperty('--glith_color', TimeColor);
        document.body.style.setProperty('--digit_color', TimeColor);
    }
    if (Settings.TimeBlurColor) {
        var c = Settings.TimeBlurColor.value.split(' ').map(
            function (c) {
                return Math.ceil(c * 255);
            }
        );
        Clock.style.textShadow = TimeBlurColor = '0 0 20px rgb(' + c + ')';
        ClockSettingsObject.Blur = 'rgb(' + c + ')';
        document.body.style.setProperty('--digit_blur', ClockSettingsObject.Blur);
    }
    if (Settings.TimeStyle) {
        TimeStyle = Settings.TimeStyle.value;
        GetTime();
    }
    if (Settings.TimePositionX) {
        TimePositionX = Settings.TimePositionX.value;
        Clock.style.left = TimePositionX - 50 + ClockSettingsObject.AlignPX + '%';
        document.body.style.setProperty(
            '--glith_pos',
            TimePositionX + (TimePositionX * (((window.innerWidth / 64) / 100) * 2)) - (window.innerWidth / 64) + '% ' + (TimePositionY - (TimePositionY * 0.04) + 2) + '%'
        );
    }
    if (Settings.TimePositionY) {
        TimePositionY = Settings.TimePositionY.value;
        Clock.style.top = TimePositionY - 50 + '%';
        document.body.style.setProperty(
            '--glith_pos',
            TimePositionX + (TimePositionX * (((window.innerWidth / 64) / 100) * 2)) - (window.innerWidth / 64) + '% ' + (TimePositionY - (TimePositionY * 0.04) + 2) + '%'
        );
    }
    if (Settings.TimeOpacity) {
        TimeOpacity = Settings.TimeOpacity.value / 100;
        Clock.style.opacity = TimeOpacity;
    }
    if (Settings.TimeShowSencends) {
        TimeShowSencends = Settings.TimeShowSencends.value;
    }
}

function SetShowClock(IsShow) {
    if (IsShow) {
        Clock.style.display = 'block';
    }
    else {
        Clock.style.display = 'none';
    }
}

function MathMap(Value, FromLow, FromHigh, ToLow, ToHigh) {
    var FromRange = FromHigh - FromLow
    var ToRange = ToHigh - ToLow
    var ScaleFactor = ToRange / FromRange
    var TempValue = Value - FromLow
    TempValue *= ScaleFactor
    return TempValue + ToLow
}