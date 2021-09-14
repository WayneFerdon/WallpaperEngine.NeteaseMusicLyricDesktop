var TimeOpacity = 0.8
var TimePositionX = 50
var TimePositionY = 50
var TimeShowSencends = true
var TimeColor
var TimeBlurColor
var Clock = document.getElementById("Clock");
var TimeStyle = true;
let NewDate = new Date();

ClockInit();
NewDate.setDate(NewDate.getDate());
setTimeout(SecondPassed, 2000);
AutoTime();


function ClockInit() {
	Clock.style.width = g_Width + 'px';
	Clock.style.lineHeight = g_Height + 'px';
	Clock.style.height = g_Height + 'px';
	Clock.style.fontSize = Math.floor(g_Height / 300 * 20) + 'px';
	document.body.style.setProperty(
		'--glith_size',
		g_Width + 'px ' + g_Height + 'px'
	);
}
function SecondPassed() {
	$('.Clock').removeClass('is-off');
}
function GetTime() {
	var Current = new Date();
	var RealTime;
	var Hour = Current.getHours();
	var StrEnd = "";
	if (!TimeStyle) {
		str = Hour < 12 ? "AM" : "PM";
		Hour = Hour <= 12 ? Hour : Hour - 12;
	}
	Clock.innerHTML = Add0(Hour) + " : " + Add0(Current.getMinutes());
	RealTime = Clock.innerHTML;
	if (TimeShowSencends) {
		var Second = Add0(Current.getSeconds()) + StrEnd;
		Clock.innerHTML += " <span class='sec'>" + Second + "</span>";
		RealTime += ' : ' + Second;
	}
	$('.time').html(RealTime);
}

function AutoTime() {
	GetTime();
	setTimeout(AutoTime, 1000);
}
function Add0(n) {
	return n < 10 ? '0' + n : '' + n;
}
