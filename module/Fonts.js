function SetFontCustom(Dir, Name) {
	let NewStyle = document.createElement('style');
	NewStyle.append(document.createTextNode("\
	@font-face {\
	    font-family: " + Name + ";\
	    src: url('" + "file:///" + Dir + "') format('truetype');\
	}\
	"));
	document.head.append(NewStyle)
}
function SetFont(Name) {
	let Font = document.createElement('link');
	Font.rel = 'stylesheet';
	Font.href = 'https://fonts.googleapis.com/css?family=' + Name.replace(/ /g, '+');
	Font.type = 'text/css';
	document.head.append(Font);
}