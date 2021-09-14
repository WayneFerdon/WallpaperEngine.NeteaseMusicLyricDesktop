var g_SlideList = [];
var g_BackgroundSettingsObject = {};
g_BackgroundSettingsObject.Video = document.querySelector(".VideoBackground");
g_BackgroundSettingsObject.BackgroundRoute = "url('Content/imgs/1.png')";
g_BackgroundSettingsObject.VideoRoute = "video/test.webm";
g_BackgroundSettingsObject.CusvideoRoute = "";
g_BackgroundSettingsObject.Random = false;
g_BackgroundSettingsObject.CurrentImg = "";
g_BackgroundSettingsObject.WallpaperMode = 1;
g_BackgroundSettingsObject.Speed = 1;
g_BackgroundSettingsObject.Custom = {};
g_BackgroundSettingsObject.BgStyle = 0;

var BackgroundSettings = function (Settings) {
	if (Settings.WallpaperMode) {
		g_BackgroundSettingsObject.WallpaperMode = Settings.WallpaperMode.value;
		ChangeBackground();
	}
	if (Settings.DefaultWallpaper) {
		g_BackgroundSettingsObject.BackgroundRoute = "url('Content/imgs/" + Settings.DefaultWallpaper.value + ".png')";
		ShowBackground();
	}
	if (Settings.CustomDirectory) {
		ChangeBackground();
	}
	if (Settings.BackgroundColor) {
		document.body.style.setProperty('--bg-color', 'rgb(' + Settings.BackgroundColor.value.split(' ').map(function (c) { return Math.ceil(c * 255) }) + ')');
	}
	if (Settings.Image) {
		g_BackgroundSettingsObject.Custom = Settings.Image.value;
		ShowBackground();
	}
	if (Settings.Foreground) {
		document.body.style.setProperty('--fg-img', "url('" + 'file:///' + Settings.Foreground.value + "')");
	}
	if (Settings.SelectVideo) {
		if (g_BackgroundSettingsObject.WallpaperMode == 3) {
			SelectVideo = Settings.SelectVideo.value;
			if (SelectVideo) {
				g_BackgroundSettingsObject.CusvideoRoute = 'file:///' + SelectVideo;
			}
			else {
				g_BackgroundSettingsObject.CusvideoRoute = "";
			}
			ChangeVideoModel();
		}
	}
	if (Settings.Random) {
		g_BackgroundSettingsObject.Random = Settings.Random.value;
	}
	if (Settings.ImageSwitchInterval) {
		g_BackgroundSettingsObject.Speed = Settings.ImageSwitchInterval.value;
	}
	if (Settings.ImageDisplayStlye) {
		g_BackgroundSettingsObject.BgStyle = Settings.ImageDisplayStlye.value;
		ShowBackground();
	}
	if (Settings.ForegroundDisplayStlye) {
		switch (Settings.ForegroundDisplayStlye.value) {
			case 1:
				{
					document.body.style.setProperty('--fg-repeat', "no-repeat");
					document.body.style.setProperty('--fg-size', "cover");
					break;
				}
			case 2:
				{
					document.body.style.setProperty('--fg-repeat', "no-repeat");
					document.body.style.setProperty('--fg-size', "100% 100%");
					break;
				}
			case 3:
				{
					document.body.style.setProperty('--fg-repeat', "no-repeat");
					document.body.style.setProperty('--fg-size', "contain");
					break;
				}
			case 4:
				{
					document.body.style.setProperty('--fg-repeat', "repeat");
					document.body.style.setProperty('--fg-size', "auto");
					break;
				}
			case 5:
				{
					document.body.style.setProperty('--fg-repeat', "no-repeat");
					document.body.style.setProperty('--fg-size', "auto");
					break;
				}
			default:
				{
					break;
				}
		}
	}
	if (Settings.VideoVolume) {
		g_BackgroundSettingsObject.Video.volume = Settings.VideoVolume.value / 100;
	}
}

function SetBackgroundStyle() {
	switch (g_BackgroundSettingsObject.BgStyle) {
		case 1:
			{
				document.body.style.setProperty('--bg-repeat', "no-repeat");
				document.body.style.setProperty('--bg-size', "cover");
				break;
			}
		case 2:
			{
				document.body.style.setProperty('--bg-repeat', "no-repeat");
				document.body.style.setProperty('--bg-size', "100% 100%");
				break;
			}
		case 3:
			{
				document.body.style.setProperty('--bg-repeat', "no-repeat");
				document.body.style.setProperty('--bg-size', "contain");
				break;
			}
		case 4:
			{
				document.body.style.setProperty('--bg-repeat', "repeat");
				document.body.style.setProperty('--bg-size', "auto");
				break;
			}
		case 5:
			{
				document.body.style.setProperty('--bg-repeat', "no-repeat");
				document.body.style.setProperty('--bg-size', "auto");
				break;
			}
		default:
			{
				break;
			}
	}
}

function ShowBackground() {
	switch (g_BackgroundSettingsObject.WallpaperMode) {
		case 1:
			{
				$.backstretch("destroy", false);
				g_BackgroundSettingsObject.Video.src = null;
				if (g_BackgroundSettingsObject.Custom) {
					document.body.style.setProperty('--bg-img', "url('" + 'file:///' + g_BackgroundSettingsObject.Custom + "')");
				}
				else {
					document.body.style.setProperty('--bg-img', g_BackgroundSettingsObject.BackgroundRoute);
				}
				SetBackgroundStyle();
				break;
			}
		case 2:
			{
				g_BackgroundSettingsObject.Video.src = null;
				document.body.style.setProperty('--bg-img', " ");
				document.body.style.setProperty('--bg-color', '#0000');
				if (g_SlideList.length) {
					$.backstretch('file:///' + g_BackgroundSettingsObject.CurrentImg, { fade: 1000 });
				} else {
					$.backstretch("destroy", false);
				}
				break;
			}
		case 3:
			{
				$.backstretch("destroy", false);
				document.body.style.setProperty('--bg-img', " ");
				document.body.style.setProperty('--bg-color', '#0000');
				ChangeVideoModel();
				break;
			}
		case 4:
			{
				$.backstretch("destroy", false);
				g_BackgroundSettingsObject.Video.src = null;
				document.body.style.setProperty('--bg-img', " ");
				break;
			}
		default:
			{
				break;
			}
	}
}

function ChangeBackground() {
	if (g_BackgroundSettingsObject.WallpaperMode == 2) {
		if (g_SlideList.length) {
			nextImage(g_BackgroundSettingsObject.Random);
		} else {
			ShowBackground();
		}
		setTimeout(ChangeBackground, g_BackgroundSettingsObject.Speed * 60 * 1000);
	}
	else {
		ShowBackground();
	}
}

function ChangeVideoModel() {
	if (g_BackgroundSettingsObject.CusvideoRoute != "") {
		g_BackgroundSettingsObject.Video.src = g_BackgroundSettingsObject.CusvideoRoute;
	}
	else {
		g_BackgroundSettingsObject.Video.src = g_BackgroundSettingsObject.VideoRoute;
	}
	g_BackgroundSettingsObject.Video.play();
}


function updateFileList(currentFiles) {
	for (let i = 0; i < currentFiles.length; ++i) {
		if (g_SlideList.indexOf(currentFiles[i]) === -1) {
			g_SlideList.push(currentFiles[i]);
		}
	}
}

function nextImage(rands) {
	let index = -1;
	let indexNow = -1;
	if (g_BackgroundSettingsObject.CurrentImg) {
		indexNow = g_SlideList.indexOf(g_BackgroundSettingsObject.CurrentImg);
		index = indexNow;
	}
	if (rands) {
		while (index == indexNow) {
			index = Math.floor(Math.random() * (g_SlideList.length));
		}
		g_BackgroundSettingsObject.CurrentImg = g_SlideList[index];
	} else {
		if (index + 1 == g_SlideList.length) {
			g_BackgroundSettingsObject.CurrentImg = g_SlideList[0];
		}
		else {
			g_BackgroundSettingsObject.CurrentImg = g_SlideList[index + 1];
		}
	}
	ShowBackground();
}
