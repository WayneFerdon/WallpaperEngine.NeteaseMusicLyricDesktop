var CurrentDate = new DateM('#Date');

var DateSettings = function (Settings) {
	if (Settings.ShowDate) {
		CurrentDate.LoadEx(!Settings.ShowDate.value);
		CurrentDate.GetStyle().display = Settings.ShowDate.value ? 'block' : 'none';
	}
	if (Settings.DateFont) {
		if (isNaN(Settings.DateFont.value) && Settings.DateFont.value) {
			SetFont(Settings.DateFont.value);
			CurrentDate.GetStyle().fontFamily = Settings.DateFont.value.replace(/:/g, ' ');
		}
		else {
			SetOldFont(CurrentDate, Settings.DateFont.value);
		}
	}
	if (Settings.DateFontDir) {
		if (Settings.DateFontDir.value) {
			CurrentDate.GetStyle().fontFamily = "'Custom-i8', sans-serif";
			SetFontCustom(Settings.DateFontDir.value, 'Custom-i8');
		}
	}
	if (Settings.DateSize) {
		CurrentDate.GetStyle().fontSize = Math.floor(g_Height / 600 * Settings.DateSize.value) + 'px';
	}
	if (Settings.DateAlignment) {
		CurrentDate.SetAlignment(Settings.DateAlignment.value);
	}
	if (Settings.DateX) {
		CurrentDate.SetX(Settings.DateX.value);
	}
	if (Settings.DateY) {
		CurrentDate.SetY(Settings.DateY.value);
	}
	if (Settings.DateFormat) {
		CurrentDate.SetFormat(Settings.DateFormat.value);
	}
	if (Settings.DateColorRhythm) {
		CurrentDate.SetVar('colorRythm', Settings.DateColorRhythm.value);
		if (!Settings.DateColorRhythm.value) {
			CurrentDate.GetStyle().color = CurrentDate.GetVar('color');
			CurrentDate.GetStyle().textShadow = CurrentDate.GetVar(
				'blur_color'
			);
		}
	}
	if (Settings.DateColor) {
		CurrentDate.GetStyle().color = CurrentDate.SetVar(
			'color',
			'rgb('
			+ Settings.DateColor.value.split(' ').map(
				function (c) {
					return Math.ceil(c * 255);
				}
			)
			+ ')'
		);
	}
	if (Settings.DateBlurColor) {
		CurrentDate.GetStyle().textShadow = CurrentDate.SetVar(
			'blur_color',
			'0 0 20px rgb('
			+ Settings.DateBlurColor.value.split(' ').map(
				function (c) {
					return Math.ceil(c * 255);
				}
			)
			+ ')'
		);
	}
	if (Settings.DateOpacity) {
		CurrentDate.GetStyle().opacity = Settings.DateOpacity.value / 100;
	}
}