var g_IsMusicRandom = false
var MapRoute = "Content/partical/1.png"

var CustomMapRoute = {}
var effectparticlesSettingsObject = {};
var ParticlesSettings = function (Settings) {
	if (Settings.ShowParticle) {
		if (Settings.ShowParticle.value) {
			g_Wallpaper.particles('startParticles');
		} else {
			g_Wallpaper.particles('clearCanvas')
				.particles('stopParticles');
		}
	}
	if (Settings.ParticleCount) {
		g_Wallpaper.particles('addParticles', Settings.ParticleCount.value);
	}
	if (Settings.ParticleMusicTone) {
		effectparticlesSettingsObject.tone = Settings.ParticleMusicTone.value;
	}
	if (Settings.ParticleOpacity) {
		g_Wallpaper.particles('set', 'opacity', Settings.ParticleOpacity.value / 100);
	}
	if (Settings.ParticleOpacityRandom) {
		g_Wallpaper.particles('set', 'opacityRandom', Settings.ParticleOpacityRandom.value);
	}
	if (Settings.ParticleColor) {
		var color = Settings.ParticleColor.value.split(' ').map(function (c) {
			return Math.ceil(c * 255)
		});
		g_Wallpaper.particles('set', 'color', color);
	}
	if (Settings.ParticleShadowColor) {
		var color = Settings.ParticleShadowColor.value.split(' ').map(function (c) {
			return Math.ceil(c * 255)
		});
		g_Wallpaper.particles('set', 'shadowColor', color);
	}
	if (Settings.ParticleShadowBlur) {
		g_Wallpaper.particles('set', 'shadowBlur', Settings.ParticleShadowBlur.value);
	}
	if (Settings.ParticleImage) {
		CustomMapRoute = Settings.ParticleImage.value
		ShowMap();
	}
	if (Settings.ParticleShapeType) {
		switch (Settings.ParticleShapeType.value) {
			case 1:
				g_Wallpaper.particles('set', 'shapeType', 'circle');
				break;
			case 2:
				g_Wallpaper.particles('set', 'shapeType', 'edge');
				break;
			case 3:
				g_Wallpaper.particles('set', 'shapeType', 'triangle');
				break;
			case 4:
				g_Wallpaper.particles('set', 'shapeType', 'star');
				break;
			case 5:
				g_Wallpaper.particles('set', 'shapeType', 'image');
				ShowMap();
				break;
			default:
				g_Wallpaper.particles('set', 'shapeType', 'circle');
		}
	}
	if (Settings.particles_picdef) {
		MapRoute = 'map/' + Settings.particles_picdef.value + '.png';
		ShowMap();
	}
	if (Settings.ParticleSize) {
		g_Wallpaper.particles('set', 'sizeValue', Settings.ParticleSize.value);
	}
	if (Settings.ParticleSizeRandom) {
		g_Wallpaper.particles('set', 'sizeRandom', Settings.ParticleSizeRandom.value);
	}
	if (Settings.ParticleLinkEnable) {
		g_Wallpaper.particles('set', 'linkEnable', Settings.ParticleLinkEnable.value);
	}
	if (Settings.ParticleLinkDistance) {
		g_Wallpaper.particles('set', 'linkDistance', Settings.ParticleLinkDistance.value);
	}
	if (Settings.ParticleLinkWidth) {
		g_Wallpaper.particles('set', 'linkWidth', Settings.ParticleLinkWidth.value);
	}
	if (Settings.ParticleLinkColor) {
		var color = Settings.ParticleLinkColor.value.split(' ').map(function (c) {
			return Math.ceil(c * 255)
		});
		g_Wallpaper.particles('set', 'linkColor', color);
	}
	if (Settings.ParticleLinkOpacity) {
		g_Wallpaper.particles('set', 'linkOpacity', Settings.ParticleLinkOpacity.value / 100);
	}
	if (Settings.ParticleMove) {
		g_Wallpaper.particles('set', 'isMove', Settings.ParticleMove.value);
	}
	if (Settings.ParticleSpeed) {
		g_Wallpaper.particles('set', 'speed', Settings.ParticleSpeed.value);
	}
	if (Settings.ParticleSpeedRandom) {
		g_Wallpaper.particles('set', 'speedRandom', Settings.ParticleSpeedRandom.value);
	}
	if (Settings.ParticleMusicRandom) {
		g_Wallpaper.particles('set', 'g_IsMusicRandom', Settings.ParticleMusicRandom.value);
		g_IsMusicRandom = Settings.ParticleMusicRandom.value;
	}
	if (Settings.ParticleMusicStrengh) {
		g_Wallpaper.particles('set', 'musicStrengh', Settings.ParticleMusicStrengh.value);
	}
	if (Settings.ParticleMoveX) {
		g_Wallpaper.particles('set', 'directionX', Settings.ParticleMoveX.value);
	}
	if (Settings.ParticleMoveY) {
		g_Wallpaper.particles('set', 'directionY', Settings.ParticleMoveY.value);
	}
	if (Settings.ParticleMoveStraight) {
		g_Wallpaper.particles('set', 'isStraight', Settings.ParticleMoveStraight.value);
	}
	if (Settings.ParticleBounce) {
		g_Wallpaper.particles('set', 'isBounce', Settings.ParticleBounce.value);
	}
	if (Settings.ParticleMoveOutMode) {
		if (Settings.ParticleMoveOutMode.value) {
			g_Wallpaper.particles('set', 'moveOutMode', 'bounce');
		}
		else {
			g_Wallpaper.particles('set', 'moveOutMode', 'out');
		}
	}
}

var ShowMap = function () {
	if (CustomMapRoute) {
		g_Wallpaper.particles('ParticleImage', CustomMapRoute, 'false')
	} else {
		g_Wallpaper.particles('ParticleImage', MapRoute, 'true')
	}
}