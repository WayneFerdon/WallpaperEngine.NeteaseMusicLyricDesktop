var VisualizerSettings = function (Settings) {
    if (Settings.AudioVisualizeMonstercatColor) {
        g_MonsterCat.CustomColor = Settings.AudioVisualizeMonstercatColor.value
        if (g_MonsterCat.CustomColor) {
            var Color = Settings.AudioVisualizeMonstercatColor.value.split(' ');
            for (var i = 0; i < Color.length; i++) {
                Color[i] = (Color[i] * 255).toString(16);
                if (Color[i].length == 1) {
                    Color[i] = "0" + Color[i];
                }
            }
            Color = Color.join("");
            Color = "#" + Color;
            g_MonsterCat.Color = Color;
        }
    }
    if (Settings.AudioVisualizeMonstercatSmoothing) {
        g_MonsterCat.SmoothingFactor = Settings.AudioVisualizeMonstercatSmoothing.value;
    }
    if (Settings.AudioVisualizeMonstercatBarWidth) {
        g_MonsterCat.BarWidth = Settings.AudioVisualizeMonstercatBarWidth.value;
        UpdateSize();
    }
    if (Settings.AudioVisualizeMonstercatBarPadding) {
        g_MonsterCat.BarPadding = Settings.AudioVisualizeMonstercatBarPadding.value;
        UpdateSize();
    }
    if (Settings.AudioVisualizeMonstercatOpacity) {
        g_CanvasZ.style.opacity = Settings.AudioVisualizeMonstercatOpacity.value / 100;
        UpdateSize();
    }
    if (Settings.AudioVisualizeMonstercatPositionX) {
        VisualizerSettings.xPos = Settings.AudioVisualizeMonstercatPositionX.value;
        g_CanvasZ.style.left = VisualizerSettings.xPos - 50 + '%';
    }
    if (Settings.AudioVisualizeMonstercatPositionY) {
        VisualizerSettings.yPos = Settings.AudioVisualizeMonstercatPositionY.value;
        g_CanvasZ.style.top = VisualizerSettings.yPos - 50 + '%';
    }
    if (Settings.AudioVisualizeMonstercatDouble) {
        g_MonsterCat.Double = Settings.AudioVisualizeMonstercatDouble.value;
    }
    if (Settings.AudioVisualizeMonstercatReverse) {
        g_MonsterCat.Reverse = Settings.AudioVisualizeMonstercatReverse.value;
    }
}