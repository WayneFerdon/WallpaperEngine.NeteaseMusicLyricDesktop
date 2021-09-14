
var g_CanvasZ = document.getElementById("Monstercat");
g_CanvasZ.style.display = 'block';
var CtxZ = g_CanvasZ.getContext("2d");

var Bars = [];
var BarsLength = 128;
var PeakValue = 1;
var SmoothingFactor = 2;
var g_MonsterCat = {
    BarWidth: 20,
    BarPadding: 5,
    Color: "#fff",
    SmoothingFactor: 5,
    Equalize: true,
    FPS: 120,
    Reverse: false,
    Double: false
};

var PinkNoise = [
    1.1760367470305, 0.85207379418243, 0.68842437227852, 0.63767902570829,
    0.5452348949654, 0.50723325864167, 0.4677726234682, 0.44204182748767,
    0.41956517802157, 0.41517375040002, 0.41312118577934, 0.40618363960446,
    0.39913707474975, 0.38207008614508, 0.38329789106488, 0.37472136606245,
    0.36586428412968, 0.37603017335105, 0.39762590761573, 0.39391828858591,
    0.37930603769622, 0.39433365764563, 0.38511504613859, 0.39082579241834,
    0.3811852720504, 0.40231453727161, 0.40244151133175, 0.39965366884521,
    0.39761103827545, 0.51136400422212, 0.66151212038954, 0.66312205226679,
    0.7416276690995, 0.74614971301133, 0.84797007577483, 0.8573583910469,
    0.96382997811663, 0.99819377577185, 1.0628692615814, 1.1059083969751,
    1.1819808497335, 1.257092297208, 1.3226521464753, 1.3735992532905,
    1.4953223705889, 1.5310064942373, 1.6193923584808, 1.7094805527135,
    1.7706604552218, 1.8491987941428, 1.9238418849406, 2.0141596921333,
    2.0786429508827, 2.1575522518646, 2.2196355526005, 2.2660112509705,
    2.320762171749, 2.3574848254513, 2.3986127976537, 2.4043566176474,
    2.4280476777842, 2.3917477397336, 2.4032522546622, 2.3614180150678
];

var Last = performance.now() / 1000;
var FPSThreshold = 0;

onload();

function monstercateq(AudioData) {
    var Max = 0;
    var Data = [];
    for (i = 0; i < 64; i++) {
        Data.push((AudioData[i] + AudioData[i + 64]) / 2)
        if (g_MonsterCat.Equalize) {
            Data[i] /= PinkNoise[i];
        }
        if (Data[i] > Max) {
            Max = Data[i];
        }
    }

    PeakValue = PeakValue * 0.99 + Max * 0.01;
    for (i = 0; i < Data.length; i++) {
        Data[i] /= PeakValue;
        if (Data[i] > 1.1) {
            Data[i] = 1.1;
        }
    }
    var NewAudio = [];
    var Average = 0;
    if (g_MonsterCat.Double) {
        for (var i = 0; i < 64; i++) {
            if (i == 0 || i == 63) {
                NewAudio[i] = Data[i];
                NewAudio[127 - i] = Data[i];
            } else {
                NewAudio[i] = (Data[i - 1] * 2 + Data[i] * 3 + Data[i + 1] * 2) / 7;
                NewAudio[127 - i] = (Data[i - 1] * 2 + Data[i] * 3 + Data[i + 1] * 2) / 7;
            }
            if (g_MonsterCat.Reverse) {
                NewAudio[i] *= -1;
                NewAudio[127 - i] *= -1;
            }
            Average += NewAudio[i];
        }
    }
    else {
        for (var i = 0; i < 128; i++) {
            if (i == 32 || i == 94) {
                NewAudio[i] = Data[i - 32];
            }
            else if (i < 32 || i > 94) {
                NewAudio[i] = 0;
            }
            else {
                NewAudio[i] = (Data[i - 33] * 2 + Data[i - 32] * 3 + Data[i - 31] * 2) / 7;
            }
            if (g_MonsterCat.Reverse) {
                NewAudio[i] *= -1;
            }
            Average += NewAudio[i];
        }
    }

    Average /= 64;
    for (var i = 0; i < Bars.length; i++) {
        Bars[i].DesiredPos = NewAudio[i] * g_CanvasZ.height / 3;
    }
};

function UpdateSize() {
    for (var i = 0; i < Bars.length; i++) {
        Bars[i].X = g_CanvasZ.width / 2 - (BarsLength * (g_MonsterCat.BarWidth + g_MonsterCat.BarPadding) - g_MonsterCat.BarPadding) / 2 + i * (g_MonsterCat.BarWidth + g_MonsterCat.BarPadding);
        Bars[i].Y = g_CanvasZ.height / 2 - 25;
        Bars[i].Width = g_MonsterCat.BarWidth;
        Bars[i].Height = 0;
    }
}

function Resize() {
    g_CanvasZ.width = window.innerWidth;
    g_CanvasZ.height = window.innerHeight;
    g_CanvasZ.style.width = window.innerWidth + "px";
    g_CanvasZ.style.height = window.innerHeight + "px";
}

function Bar(X, Y, Width, Height) {
    this.X = X;
    this.Y = Y;
    this.Width = Width;
    this.Height = Height;
    this.DesiredPos = this.Height;
    this.Draw = function () {
        CtxZ.fillRect(this.X, this.Y, this.Width, this.Height);
    }
    this.Update = function () {
        if (this.Height < this.DesiredPos) {
            this.Height += (this.DesiredPos - this.Height) / g_MonsterCat.SmoothingFactor;
        } else if (this.Height > this.DesiredPos) {
            this.Height -= (this.Height - this.DesiredPos) / g_MonsterCat.SmoothingFactor;
        }
        this.Y = g_CanvasZ.height / 2 - this.Height;
    }
}

function onload() {
    Resize();
    for (var i = 0; i < BarsLength; i++) {
        Bars.push(
            new Bar(
                g_CanvasZ.width / 2 - (BarsLength * (g_MonsterCat.BarWidth + g_MonsterCat.BarPadding)) / 2 + i * (g_MonsterCat.BarWidth + g_MonsterCat.BarPadding), g_CanvasZ.height / 2 - 25,
                g_MonsterCat.BarWidth,
                25
            )
        );
    }
    window.requestAnimationFrame(Draw);
}

function Draw() {
    window.requestAnimationFrame(Draw);
    var Now = performance.now() / 1000;
    var dt = Math.min(Now - Last, 1);
    Last = Now;

    if (g_MonsterCat.FPS > 0) {
        FPSThreshold += dt;
        if (FPSThreshold < 1.0 / g_MonsterCat.FPS) {
            return;
        }
        FPSThreshold -= 1.0 / g_MonsterCat.FPS;
    }

    CtxZ.clearRect(0, 0, g_CanvasZ.width, g_CanvasZ.height);
    CtxZ.fillStyle = g_MonsterCat.Color;
    for (var i = 0; i < Bars.length; i++) {
        Bars[i].Draw();
        Bars[i].Update();
    }
}
