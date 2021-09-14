class Loader {
	constructor(ID) {
		this.Self = document.querySelector(ID);
		this.Time = 0;
		this.Opacity = 100;
	}
	GetStyle() {
		return this.Self.style
	}
	setUpdate() {
		try {
			if (CurrentDate.loaded() && this.Time >= 400) {
				clearTimeout(this.Timer);
				this.off();
			}
			this.Time += 10;
			if (this.Time >= 5000) {
				clearTimeout(this.Timer);
				this.off();
			}
			this.Timer = setTimeout(this.setUpdate.bind(this), 10);
		} catch (e) {
			this.Timer = setTimeout(this.setUpdate.bind(this), 10);
		}
	}
	off() {
		try {
			this.Opacity -= 1;
			if (this.Opacity > 0) {
				this.Opacity -= 1;
				this.GetStyle().opacity = this.Opacity / 100;
				setTimeout(this.off.bind(this), 100);
			}
			else this.GetStyle().opacity = '0%';
		} catch (e) {
			alert(e);
		}
	}
}

StartLoader = new Loader('#loader');
StartLoader.setUpdate();
