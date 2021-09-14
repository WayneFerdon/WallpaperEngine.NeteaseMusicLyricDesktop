var g_Width = window.innerWidth
var g_Height = window.innerHeight
var g_Wallpaper = $('body').particles({}).audiovisualizer({})

var CTX = Can.getContext("2d");
var CTXLine = CanLine.getContext("2d");
var IsFristLoad = true
var Files = {}

function WallpaperAudioListener(arr) {
	if (g_IsMusicRandom) {
		g_Wallpaper.particles('drawCanvas', arr);
	}
	g_Wallpaper.audiovisualizer('clearCanvas');
	CTXLine.clearRect(0, 0, g_Width, g_Height);
	CTX.clearRect(0, 0, g_Width, g_Height);
	monstercateq(arr);
}

window.wallpaperPropertyListener = {
	applyUserProperties: function (Properties) {
		BackgroundSettings(Properties);
		ParticlesSettings(Properties);
		DateSettings(Properties);
		ClockSettings(Properties);
		VisualizerSettings(Properties);
		IsFristLoad = false;
	},
	setPaused: function (IsPaused) {
		if (IsPaused) {
			g_BackgroundSettingsObject.Video.pause();
		}
		else {
			if (g_BackgroundSettingsObject.Video.paused) {
				g_BackgroundSettingsObject.Video.play();
			}
		}
	},
	userDirectoryFilesAddedOrChanged: function (PropertyName, ChangedFiles) {
		if (!Files.hasOwnProperty(PropertyName)) {
			Files[PropertyName] = ChangedFiles;
		} else {
			Files[PropertyName] = Files[PropertyName].concat(ChangedFiles);
		}
		updateFileList(Files[PropertyName])
	},
	userDirectoryFilesRemoved: function (PropertyName, RemovedFiles) {
		for (var i = 0; i < RemovedFiles.length; ++i) {
			var FileIndex = Files[PropertyName].indexOf(RemovedFiles[i]);
			var SlideIndex = g_SlideList.indexOf(RemovedFiles[i]);
			if (FileIndex >= 0) {
				Files[PropertyName].splice(FileIndex, 1);
			}
			if (SlideIndex >= 0) {
				g_SlideList.splice(SlideIndex, 1);
			}
		}
		updateFileList(Files[PropertyName]);
	},
}

window.wallpaperRegisterAudioListener(WallpaperAudioListener);