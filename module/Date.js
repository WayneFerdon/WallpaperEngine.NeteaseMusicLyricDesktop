const we_array = new Array("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday");
const wes_array = new Array("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat");
const me_array = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");


var DateColor;

class DateM {
	constructor(ID) {
		this.Date = document.querySelector(ID);
		this.Load = [0, 4];
		this.initial();
		this.startTimer();
	}

	GetStyle() {
		return this.Date.style;
	}

	initial() {
		this.GetStyle().fontSize = Math.floor(window.height / 300 * 20) + 'px';
		this.Load[0]++;
	}

	startTimer() {
		try {
			this.GetDates();
			this.timer = setTimeout(this.startTimer.bind(this), 1000);
		} catch (e) {
			alert(e);
		}
	}

	SetFormat(format) {
		this.Format = format;
		this.Load[0]++;
	}

	SetAlignment(Alignment) {
		try {
			this.Alignment = Alignment == 'left' ? 50 : Alignment == 'right' ? -50 : 0;
			this.GetStyle().textAlign = Alignment;
			this.SetX();
		} catch (e) {
			alert(e);
		}
	}

	SetX(X) {
		try {
			this.X = X === undefined ? this.X : X
			this.GetStyle().left = this.X - 50 + this.Alignment + '%'
		} catch (e) {
			alert(e);
		}
	}

	SetY(Y) {
		try {
			this.Y = Y === undefined ? this.Y : Y;
			this.GetStyle().top = this.Y + '%';
		} catch (e) {
			alert(e);
		}
	}

	SetVar(Variable, Value) {
		try {
			this[Variable] = Value;
			return Value;
		} catch (e) {
			alert(e);
		}
	}

	getVar(Variable) {
		try {
			if (this[Variable] != null) {
				return this[Variable];
			}
			else {
				return null;
			}
		} catch (e) {
			alert(e);
		}
	}

	loaded() {
		return this.Load[0] >= this.Load[1];
	}

	LoadEx(bool) {
		if (bool) {
			this.Load[0] += this.Load[1];
			return true;
		}
		else {
			return false;
		}
	}

	GetDates() {
		var Current = new Date();
		var DateHtml;

		if (this.Format == "" || this.Format == null) {
			DateHtml = "None Format";
		}
		else {
			DateHtml = this.Format;
			DateHtml = DateHtml
				.replaceAll("{,}", '<br>')
				.replaceAll("{DD}", Current.getDate())
				.replaceAll("{MM}", Add0(Current.getMonth() + 1))
				.replaceAll("{YYYY}", Current.getFullYear())
				.replaceAll("{week}", we_array[Current.getDay()])
				.replaceAll("{wek}", wes_array[Current.getDay()])
				.replaceAll("{month}", me_array[Current.getMonth()]);
		}
		this.Date.innerHTML = DateHtml;
		this.Load[0]++;
	}
}

function SetOldFont(Target, Type) {
	switch (Type) {
		case 1:
			{
				Target.style.fontFamily = '"等线 Light","Microsoft Yahei Light"';
				break;
			}
		case 2:
			{
				Target.style.fontFamily = "'Lato', sans-serif";
				break;
			}
		case 3:
			{
				Target.style.fontFamily = "'Brush Script Std', cursive";
				break;
			}
		case 4:
			{
				Target.style.fontFamily = "'Papyrus', fantasy";
				break;
			}
		case 5:
			{
				Target.style.fontFamily = "'Harrington', fantasy";
				break;
			}
		case 6:
			{
				Target.style.fontFamily = "'Open Sans', sans-serif";
				break;
			}
		default:
			{
				break;
			}
	}
}