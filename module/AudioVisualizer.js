(function (global, factory) {
	'use strict';
	if (typeof define === 'function' && define.amd) {
		define(['jquery'], function ($) {
			return factory($, global, global.document, global.Math);
		});
	} else if (typeof exports === "object" && exports) {
		module.exports = factory(require('jquery'), global, global.document, global.Math);
	} else {
		factory(jQuery, global, global.document, global.Math);
	}
})(typeof window !== 'undefined' ? window : this, function ($, window, document, Math, undefined) {
	'use strict';
	(function () {
		var lastTime = 0;
		var vendors = ['ms', 'moz', 'webkit', 'o'];
		for (var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
			window.requestAnimationFrame = window[vendors[x] + 'RequestAnimationFrame'];
			window.cancelAnimationFrame = window[vendors[x] + 'CancelAnimationFrame'] || window[vendors[x] + 'CancelRequestAnimationFrame'];
		}
		if (!window.requestAnimationFrame) {
			window.requestAnimationFrame = function (callback, element) {
				var currTime = new Date().GetTime();
				var timeToCall = Math.max(0, 16 - (currTime - lastTime));
				var id = window.setTimeout(function () {
					callback(currTime + timeToCall);
				},
					timeToCall);
				lastTime = currTime + timeToCall;
				return id;
			};
		}

		if (!window.cancelAnimationFrame) {
			window.cancelAnimationFrame = function (id) {
				clearTimeout(id);
			};
		}
	}());
	var canvas;
	var context;
	var canvasWidth, canvasHeight;
	var originX, originY;
	var minLength = 300;
	var pointArray1 = [],
		pointArray2 = [],
		staticPointsArray = [],
		ballPointArray = [];
	var lastAudioSamples = [];
	for (var i = 0; i < 128; i++) {
		lastAudioSamples[i] = 0;
	}
	var rotationAngle1 = 0,
		rotationAngle2 = 0;
	function getRingArray(audioSamples, num) {
		var AudioArray = [].concat(audioSamples || []);
		var max = AudioArray.length - num;
		var isfirst = true;
		for (var i = 0; i < max; i++) {
			if (isfirst) {
				AudioArray.shift();
				isfirst = false;
			} else {
				AudioArray.pop();
				isfirst = true;
			}
		}
		return AudioArray;
	}
	function getBallArray(audioSamples, num) {
		var AudioArray = [];
		for (var i = 0; i < 120; i += num) {
			AudioArray.push(audioSamples[i] || []);
		}
		return AudioArray;
	}
	function getAudioSamples(audioSamples, index, decline, isChange) {
		var audioValue = audioSamples[index] ? audioSamples[index] : 0;
		audioValue = Math.max(audioValue, lastAudioSamples[index] - decline || 0.1);
		audioValue = Math.min(audioValue, 1.5);  // 溢出部分按值1.5处理
		if (isChange) {
			lastAudioSamples[index] = audioValue;
		}
		return audioValue;
	}
	function rotation(rotationAngle, deg) {
		rotationAngle += Math.PI / 180 * deg;
		if (rotationAngle >= 360 && rotationAngle <= 360) {
			rotationAngle = 0;
		}
		return rotationAngle;
	}
	function getDeg(point, index, angle) {
		return Math.PI / 180 * (360 / point) * (index + angle / 3)
	}
	function getXY(radius, deg, x, y) {
		return {
			'x': Math.cos(deg) * radius + x,
			'y': Math.sin(deg) * radius + y
		};
	}
	function setPoint(audioSamples, direction, that, isChange) {
		var pointArray = [];
		var ringArray = getRingArray(audioSamples, that.pointNum);
		rotationAngle1 = rotation(rotationAngle1, that.ringRotation);
		for (var i = 0; i < ringArray.length; i++) {
			var deg = getDeg(ringArray.length, i, rotationAngle1);
			var audioValue = getAudioSamples(audioSamples, i, that.decline, isChange);
			var radius = that.radius * (minLength / 2) + direction * (that.distance + audioValue * (that.amplitude * 15));
			var point = getXY(radius, deg, originX, originY);
			pointArray.push({ 'x': point.x, 'y': point.y });
		}
		return pointArray;
	}
	function setStaticPoint(audioSamples, that) {
		var pointArray = [];
		var ringArray = getRingArray(audioSamples, that.pointNum);
		rotationAngle1 = rotation(rotationAngle1, that.ringRotation);
		for (var i = 0; i < ringArray.length; i++) {
			var deg = getDeg(ringArray.length, i, rotationAngle1);
			var radius = that.radius * (minLength / 2);
			var point = getXY(radius, deg, originX, originY);
			pointArray.push({ 'x': point.x, 'y': point.y });
		}
		return pointArray;
	}
	function setBall(audioSamples, that) {
		var pointArray = [];
		var ballArray = getBallArray(audioSamples, that.ballSpacer);
		rotationAngle2 = rotation(rotationAngle2, that.ballRotation);
		for (var i = 0; i < ballArray.length; i++) {
			var deg = getDeg(ballArray.length, i, rotationAngle2);
			var audioValue = Math.min(audioSamples[i] ? audioSamples[i] : 0, 1);
			var radius = that.radius * (minLength / 2) + (that.distance + 50) + audioValue * 75;
			var point = getXY(radius, deg, originX, originY);
			pointArray.push({ 'x': point.x, 'y': point.y });
		}
		return pointArray;
	}
	function getPointArray(num) {
		switch (num) {
			case 1:
				return staticPointsArray;
			case 2:
				return pointArray1;
			case 3:
				return pointArray2;
		}
	}
	function getRainbowGradient(x0, y0, x1, y1) {
		var rainbow = context.createLinearGradient(x0, y0, x1, y1);
		rainbow.addColorStop(0, "rgb(255, 0, 0)");
		rainbow.addColorStop(0.15, "rgb(255, 0, 255)");
		rainbow.addColorStop(0.33, "rgb(0, 0, 255)");
		rainbow.addColorStop(0.5, "rgb(0, 255, 255)");
		rainbow.addColorStop(0.67, "rgb(0, 255, 0)");
		rainbow.addColorStop(0.85, "rgb(255, 255, 0)");
		rainbow.addColorStop(1, "rgb(255, 0, 0)");
		return rainbow;
	}
	function drawRing(pointArray) {
		context.beginPath();
		context.moveTo(pointArray[0].x, pointArray[0].y);
		for (var i = 0; i < pointArray.length; i++) {
			context.lineTo(pointArray[i].x, pointArray[i].y);
		}
		context.closePath();
		context.stroke();
	}
	function drawBall(pointArray, ballSize) {
		for (var i = 0; i < pointArray.length; i++) {
			context.beginPath();
			context.arc(pointArray[i].x - 0.5, pointArray[i].y - 0.5, ballSize, 0, 360, false);
			context.closePath();
			context.fill();
		}
	}
	function drawLine(pointArray1, pointArray2) {
		context.beginPath();
		var max = Math.min(pointArray1.length, pointArray2.length);
		for (var i = 0; i < max; i++) {
			context.moveTo(pointArray1[i].x, pointArray1[i].y);
			context.lineTo(pointArray2[i].x, pointArray2[i].y);
		}
		context.closePath();
		context.stroke();
	}
	var AudioVisualizer = function (el, options) {
		this.$el = $(el);
		this.opacity = options.opacity;
		this.color = options.color;
		this.shadowColor = options.shadowColor;
		this.shadowBlur = options.shadowBlur;
		this.offsetX = options.offsetX;
		this.offsetY = options.offsetY;
		this.isClickOffset = options.isClickOffset;
		this.amplitude = options.amplitude;
		this.decline = options.decline;
		this.isRing = options.isRing;
		this.isStaticRing = options.isStaticRing;
		this.isInnerRing = options.isInnerRing;
		this.isOuterRing = options.isOuterRing;
		this.radius = options.radius;
		this.ringRotation = options.ringRotation;
		this.isLineTo = options.isLineTo;
		this.firstPoint = options.firstPoint;
		this.secondPoint = options.secondPoint;
		this.pointNum = options.pointNum;
		this.distance = options.distance;
		this.lineWidth = options.lineWidth;
		this.isBall = options.isBall;
		this.ballSpacer = options.ballSpacer;
		this.ballSize = options.ballSize;
		this.ballRotation = options.ballRotation;

		canvas = document.createElement('canvas');
		canvas.id = 'canvas-audio';
		$(canvas).css({
			'position': 'absolute',
			'top': 0,
			'left': 0,
			'z-index': 2,
			'opacity': this.opacity
		});
		canvasWidth = canvas.width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
		canvasHeight = canvas.height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

		minLength = Math.min(canvasWidth, canvasHeight);
		originX = canvasWidth * this.offsetX;
		originY = canvasHeight * this.offsetY;
		context = canvas.getContext('2d');
		context.fillStyle = 'rgb(' + this.color + ')';
		context.lineWidth = this.lineWidth;
		context.strokeStyle = 'rgb(' + this.color + ')';
		context.shadowColor = 'rgb(' + this.color + ')';
		context.shadowBlur = this.shadowBlur;

		$(this.$el).append(canvas);

		this.setupPointerEvents();
	};
	AudioVisualizer.prototype = {
		setupPointerEvents: function () {
			var that = this;
			$(this.$el).click(function (e) {
				if (that.isClickOffset) {
					var x = e.clientX || canvasWidth * that.offsetX;
					var y = e.clientY || canvasHeight * that.offsetY;
					that.offsetX = x / canvasWidth;
					that.offsetY = y / canvasHeight;
				}
			});
			$(window).on('resize', function () {
				canvasWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
				canvasHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
				minLength = Math.min(canvasWidth, canvasHeight);
				originX = canvasWidth * this.offsetX;
				originY = canvasHeight * this.offsetY;
			});

		},
		clearCanvas: function () {
			context.clearRect(0, 0, canvasWidth, canvasHeight);
		},
		drawCanvas: function (audioSamples) {
			this.clearCanvas();
			originX = canvasWidth * this.offsetX;
			originY = canvasHeight * this.offsetY;
			pointArray1 = setPoint(audioSamples, -1, this, true);
			pointArray2 = setPoint(audioSamples, 1, this, false);
			staticPointsArray = setStaticPoint(audioSamples, this);
			ballPointArray = setBall(audioSamples, this);
			rotation(this.rotation);
			if (this.isRing) {
				if (this.isStaticRing) {
					drawRing(staticPointsArray);
				}
				if (this.isInnerRing) {
					drawRing(pointArray1);
				}
				if (this.isOuterRing) {
					drawRing(pointArray2);
				}
			}
			var firstArray = getPointArray(this.firstPoint);
			var secondArray = getPointArray(this.secondPoint);
			if (this.isLineTo && this.firstPoint !== this.secondPoint) {
				drawLine(firstArray, secondArray);
			}
			if (this.isBall) {
				drawBall(ballPointArray, this.ballSize);
			}

		},
		destroy: function () {
			this.$el
				.off('#canvas-audio')
				.removeData('audiovisualizer');
			$('#canvas-audio').remove();
		},
		set: function (property, value) {
			switch (property) {
				case 'opacity':
					$(canvas).css(property, value);
					break;
				case 'color':
					context.fillStyle = 'rgb(' + value + ')';
					context.strokeStyle = 'rgb(' + value + ')';
					break;
				case 'shadowColor':
					context.shadowColor = 'rgb(' + value + ')';
					break;
				case 'shadowBlur':
					context.shadowBlur = value;
					break;
				case 'lineWidth':
					context.lineWidth = value;
					break;
				case 'offsetX':
				case 'offsetY':
				case 'isClickOffset':
				case 'isRing':
				case 'isStaticRing':
				case 'isInnerRing':
				case 'isOuterRing':
				case 'ringRotation':
				case 'radius':
				case 'amplitude':
				case 'decline':
				case 'distance':
				case 'isLineTo':
				case 'firstPoint':
				case 'secondPoint':
				case 'pointNum':
				case 'isBall':
				case 'ballSpacer':
				case 'ballSize':
				case 'ballRotation':
					this[property] = value;
					break;
			}
		}
	};
	AudioVisualizer.DEFAULTS = {
		opacity: 0.90,
		color: '255,255,255',
		shadowColor: '255,255,255',
		shadowBlur: 15,
		offsetX: 0.5,
		offsetY: 0.5,
		isClickOffset: false,
		radius: 0.5,
		amplitude: 5,
		decline: 0.2,
		isRing: true,
		isStaticRing: false,
		isInnerRing: true,
		isOuterRing: true,
		ringRotation: 0,
		isLineTo: false,
		firstPoint: 2,
		secondPoint: 3,
		pointNum: 120,
		distance: 0,
		lineWidth: 5,
		isBall: true,
		ballSpacer: 3,
		ballSize: 3,
		ballRotation: 0
	};
	var old = $.fn.audiovisualizer;
	$.fn.audiovisualizer = function (option) {
		var args = (arguments.length > 1) ? Array.prototype.slice.call(arguments, 1) : undefined;
		return this.each(function () {
			var $this = $(this);
			var data = $this.data('audiovisualizer');
			var options = $.extend({}, AudioVisualizer.DEFAULTS, $this.data(), typeof option === 'object' && option);
			if (!data && typeof option === 'string') {
				return;
			}
			if (!data) {
				$this.data('audiovisualizer', (data = new AudioVisualizer(this, options)));
			}
			else if (typeof option === 'string') {
				AudioVisualizer.prototype[option].apply(data, args);
			}
		});
	};

	$.fn.audiovisualizer.Constructor = AudioVisualizer;
	$.fn.audiovisualizer.noConflict = function () {
		$.fn.audiovisualize = old;
		return this;
	};
});