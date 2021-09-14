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
                var id = window.setTimeout(
                    function () {
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

    var img = new Image();
    var imgWidth, imgHeight;
    var currantCanvas;
    var currantContext;

    var particlesArray = [];

    var timer = null;

    var mus = 1;

    function getDist(x1, y1, x2, y2) {
        var dx = x1 - x2,
            dy = y1 - y2;
        return Math.sqrt(dx * dx + dy * dy);
    }


    function checkOverlap(index) {
        for (var i = 0; i < particlesArray.length; i++) {
            if (i === index) {
                continue;
            }
            var particles1 = particlesArray[index];
            var particles2 = particlesArray[i];
            var dist = getDist(particles1.x, particles1.y, particles2.x, particles2.y);
            if (dist <= particles1.radius + particles2.radius) {
                particles1.x = Math.random() * canvasWidth;
                particles1.y = Math.random() * canvasHeight;
                checkOverlap(index);
            }
        }
    }

    function moveStraight(particles, isStraight, directionX, directionY) {
        if (isStraight) {
            particles.vx = directionX / 100;
            particles.vy = directionY / 100;
        } else {
            particles.vx = directionX / 100 + Math.random() - 0.5;
            particles.vy = directionY / 100 + Math.random() - 0.5;
        }
    }
    var bass = 1;

    function moveParticles(particles, isMove, g_IsMusicRandom, speed, musicStrengh) {
        mus = musicStrengh;
        if (isMove && g_IsMusicRandom) {
            particles.x += particles.vx * speed / 4 * bass;
            particles.y += particles.vy * speed / 4 * bass;
            return;
        }
        if (isMove) {
            particles.x += particles.vx * speed / 4;
            particles.y += particles.vy * speed / 4;
        }
    }

    function bounceParticles(index, isBounce) {
        if (isBounce) {
            for (var i = 0; i < particlesArray.length; i++) {
                if (i === index) {
                    continue;
                }
                var particles1 = particlesArray[index];
                var particles2 = particlesArray[i];
                var dist = getDist(particles1.x, particles1.y, particles2.x, particles2.y);
                var dist_p = particles1.radius + particles2.radius;
                if (dist <= dist_p) {
                    particles1.vx = -particles1.vx;
                    particles1.vy = -particles1.vy;

                    particles2.vx = -particles2.vx;
                    particles2.vy = -particles2.vy;
                }
            }
        }
    }

    function marginalCheck(particles, moveOutMode) {
        if (moveOutMode === 'bounce') {
            var new_pos = {
                x_left: particles.radius,
                x_right: canvasWidth,
                y_top: particles.radius,
                y_bottom: canvasHeight
            }
        } else {
            var new_pos = {
                x_left: -particles.radius,
                x_right: canvasWidth + particles.radius,
                y_top: -particles.radius,
                y_bottom: canvasHeight + particles.radius
            }
        }

        if (particles.x - particles.radius > canvasWidth) {
            particles.x = new_pos.x_left;
            particles.y = Math.random() * canvasHeight;
        }

        else if (particles.x + particles.radius < 0) {
            particles.x = new_pos.x_right;
            particles.y = Math.random() * canvasHeight;
        }

        if (particles.y - particles.radius > canvasHeight) {
            particles.y = new_pos.y_top;
            particles.x = Math.random() * canvasWidth;
        }

        else if (particles.y + particles.radius < 0) {
            particles.y = new_pos.y_bottom;
            particles.x = Math.random() * canvasWidth;
        }

        if (moveOutMode === 'bounce') {

            if (particles.x + particles.radius > canvasWidth) {
                particles.vx = -particles.vx;
            }

            else if (particles.x - particles.radius < 0) {
                particles.vx = -particles.vx;
            }


            if (particles.y + particles.radius > canvasHeight) {
                particles.vy = -particles.vy;
            }

            else if (particles.y - particles.radius < 0) {
                particles.vy = -particles.vy;
            }
        }
    }

    function initParticlesArray(that) {

        for (var i = 0; i < that.number; i++) {

            var x = ~~(0.5 + Math.random() * canvasWidth);
            var y = ~~(0.5 + Math.random() * canvasHeight);

            particlesArray.push({

                opacity: that.opacity,
                color: that.color,
                shadowColor: that.shadowColor,
                shadowBlur: that.shadowBlur,
                shapeType: that.shapeType,
                radius: that.sizeValue,
                x: x,
                y: y,
                speed: 0,
                vx: 0,
                vy: 0
            });
        }
        for (var i = 0; i < particlesArray.length; i++) {

            particlesArray[i].opacity = that.opacityRandom ? Math.min(Math.random(), that.opacity) : that.opacity;
            particlesArray[i].radius = (that.sizeRandom ? Math.random() : 1) * that.sizeValue;
            particlesArray[i].speed = Math.max(1, (that.speedRandom ? Math.random() : 1) * that.speed);
            moveStraight(particlesArray[i], that.isStraight, that.directionX, that.directionY);
            checkOverlap(i);
        }
    }

    function addParticles(that, num) {
        var old = that.number;
        if (num > old) {
            var n = num - old;
            var tempArray = [];
            for (var i = 0; i < n; i++) {
                var x = ~~(0.5 + Math.random() * canvasWidth);
                var y = ~~(0.5 + Math.random() * canvasHeight);
                tempArray.push({
                    opacity: that.opacity,
                    color: that.color,
                    shadowColor: that.shadowColor,
                    shadowBlur: that.shadowBlur,
                    shapeType: that.shapeType,
                    radius: that.sizeValue,
                    x: x,
                    y: y,
                    speed: 0,
                    vx: 0,
                    vy: 0
                });
            }
            for (var i = 0; i < tempArray.length; i++) {
                tempArray[i].opacity = (that.opacityRandom ? Math.random() : that.opacity);
                tempArray[i].radius = (that.sizeRandom ? Math.random() : 1) * that.sizeValue;
                tempArray[i].speed = (that.speedRandom ? Math.random() : 1) * that.speed;
                moveStraight(tempArray[i], that.isStraight, that.directionX, that.directionY);
            }
            particlesArray = particlesArray.concat(tempArray);
            for (var i = 0; i < particlesArray.length; i++) {
                checkOverlap(i);
            }
        } else if (num >= 0 && num < old) {
            var n = old - num;
            for (var i = 0; i < n; i++) {
                particlesArray.pop();
            }
        }
        that.number = particlesArray.length;
    }

    function setParticlesGlobalValue(that) {
        for (var i = 0; i < particlesArray.length; i++) {
            particlesArray[i].opacity = that.opacityRandom ? Math.min(Math.random(), that.opacity) : that.opacity;
            particlesArray[i].color = that.color;
            particlesArray[i].shadowColor = that.shadowColor;
            particlesArray[i].shadowBlur = that.shadowBlur;
        }
    }

    function setParticleSize(that) {
        for (var i = 0; i < particlesArray.length; i++) {
            particlesArray[i].shapeType = that.shapeType;
            particlesArray[i].radius = (that.sizeRandom ? Math.random() : 1) * that.sizeValue;
        }
    }

    function setParticlesMoveValue(that) {
        for (var i = 0; i < particlesArray.length; i++) {
            particlesArray[i].speed = Math.max(1, (that.speedRandom ? Math.random() : 1) * that.speed);
            moveStraight(particlesArray[i], that.isStraight, that.directionX, that.directionY);
        }
    }

    function updateParticlesArray(isMove, g_IsMusicRandom, isBounce, moveOutMode, musicStrengh) {
        for (var i = 0; i < particlesArray.length; i++) {
            moveParticles(particlesArray[i], isMove, g_IsMusicRandom, particlesArray[i].speed, musicStrengh);
            bounceParticles(i, isBounce);
            marginalCheck(particlesArray[i], moveOutMode);
        }
    }

    function drawShape(context, startX, startY, sideLength, sideCountNumerator, sideCountDenominator) {
        var sideCount = sideCountNumerator * sideCountDenominator;
        var decimalSides = sideCountNumerator / sideCountDenominator;
        var interiorAngleDegrees = (180 * (decimalSides - 2)) / decimalSides;
        var interiorAngle = Math.PI - Math.PI * interiorAngleDegrees / 180; // convert to radians
        context.translate(startX, startY);
        context.moveTo(0, 0);
        for (var i = 0; i < sideCount; i++) {
            context.lineTo(sideLength, 0);
            context.translate(sideLength, 0);
            context.rotate(interiorAngle);
        }
    }

    function drawParticles(particles) {
        context.save();
        context.fillStyle = 'rgb(' + particles.color + ')';
        context.shadowColor = 'rgb(' + particles.shadowColor + ')';
        context.shadowBlur = particles.shadowBlur;
        context.globalAlpha = particles.opacity;
        context.beginPath();
        switch (particles.shapeType) {
            case 'circle':
                context.arc(particles.x, particles.y, particles.radius, 0, Math.PI * 2, false);
                break;
            case 'edge':
                context.rect(particles.x - particles.radius, particles.y - particles.radius, particles.radius * 2, particles.radius * 2);
                break;
            case 'triangle':
                drawShape(context, particles.x - particles.radius, particles.y + particles.radius / 1.66, particles.radius * 2, 3, 2);
                break;
            case 'star':
                drawShape(
                    context,
                    particles.x - particles.radius * 2 / (5 / 4),
                    particles.y - particles.radius / (2 * 2.66 / 3.5),
                    particles.radius * 2 * 2.66 / (5 / 3),
                    5,
                    2
                );
                break;
            case 'image':
                if (currantCanvas.width > particles.radius * 10 || currantCanvas.height > particles.radius * 10) {
                    var scaling = 0.5;
                    var width, height;
                    if (currantCanvas.width > currantCanvas.height) {
                        scaling = particles.radius * 10 / currantCanvas.width;
                    } else {
                        scaling = particles.radius * 10 / currantCanvas.height;
                    }
                    width = currantCanvas.width * scaling;
                    height = currantCanvas.height * scaling;
                }
                context.drawImage(currantCanvas, particles.x, particles.y, width, height);
                break;
        }
        context.closePath();
        context.fill();
        context.restore();
    }

    function drawLine(index, that) {
        for (var i = 0; i < particlesArray.length; i++) {
            if (i === index) {
                continue;
            }
            var particles1 = particlesArray[index];
            var particles2 = particlesArray[i];
            var dist = getDist(particles1.x, particles1.y, particles2.x, particles2.y);
            if (dist <= that.linkDistance) {
                var d = (that.linkDistance - dist) / that.linkDistance;
                context.save();
                context.lineWidth = d * that.linkWidth;
                context.strokeStyle = "rgba(" + that.linkColor + "," + Math.min(d, that.linkOpacity) + ")";
                context.beginPath();
                context.moveTo(particles1.x, particles1.y);
                context.lineTo(particles2.x, particles2.y);
                context.closePath();
                context.stroke();
                context.restore();
            }
        }
    }

    function runParticlesTimer(that) {
        timer = requestAnimationFrame(function animal() {
            updateParticlesArray(that.isMove, that.g_IsMusicRandom, that.isBounce, that.moveOutMode, that.musicStrengh);
            context.clearRect(0, 0, canvasWidth, canvasHeight);
            for (var i = 0; i < particlesArray.length; i++) {
                drawParticles(particlesArray[i]);
                if (that.linkEnable) {
                    drawLine(i, that);
                }
            }
            timer = requestAnimationFrame(animal);
        });
    }

    function stopParticlesTimer() {
        if (timer) {
            cancelAnimationFrame(timer);
        }
    }

    var Particles = function (el, options) {
        this.$el = $(el);
        this.number = options.number;
        this.opacity = options.opacity;
        this.color = options.color;
        this.shadowColor = options.shadowColor;
        this.shadowBlur = options.shadowBlur;
        this.shapeType = options.shapeType;
        this.sizeValue = options.sizeValue;
        this.sizeRandom = options.sizeRandom;
        this.linkEnable = options.linkEnable;
        this.linkDistance = options.linkDistance;
        this.linkWidth = options.linkWidth;
        this.linkColor = options.linkColor;
        this.linkOpacity = options.linkOpacity;
        this.isMove = options.isMove;
        this.speed = options.speed;
        this.speedRandom = options.speedRandom;
        this.g_IsMusicRandom = options.g_IsMusicRandom;
        this.musicStrengh = options.musicStrengh;
        this.directionX = options.directionX;
        this.directionY = options.directionY;
        this.isStraight = options.isStraight;
        this.isBounce = options.isBounce;
        this.moveOutMode = options.moveOutMode;

        canvas = document.createElement('canvas');
        canvas.id = 'canvas-particles';
        $(canvas).css({
            'position': 'absolute',
            'top': 0,
            'left': 0,
            'z-index': 1,
            'opacity': this.opacity
        });
        canvasWidth = canvas.width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        canvasHeight = canvas.height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;

        context = canvas.getContext('2d');
        context.fillStyle = 'rgb(' + this.color + ')';
        context.shadowColor = 'rgb(' + this.color + ')';
        context.shadowBlur = this.shadowBlur;
        context.lineWidth = this.linkWidth;
        context.strokeStyle = "rgba(" + this.linkColor + "," + 1 + ")";

        currantCanvas = document.createElement('canvas');
        currantCanvas.width = canvasWidth;
        currantCanvas.height = canvasHeight;
        currantContext = currantCanvas.getContext('2d');

        img.id = 'particles-img';
        img.src = 'map/1.png';
        imgWidth = imgHeight = 500;
        this.ParticleImage('');

        $(this.$el).append(canvas);

        initParticlesArray(this);
        this.setupPointerEvents();

    };


    Particles.prototype = {

        setupPointerEvents: function () {

            $(window).on('resize', function () {
                canvasWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
                canvasHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
            });

        },

        drawCanvas: function (arr) {
            var audioAver = 0;
            switch (effectparticlesSettingsObject.tone) {
                case 1:
                    audioAver += arr[2] * 0.7;
                    audioAver += arr[3];
                    audioAver += arr[4];
                    audioAver += arr[5] * 0.9;
                    audioAver += arr[6] * 0.8;
                    audioAver += arr[7] * 0.7;
                    audioAver += arr[8] * 0.6;
                    audioAver += arr[9] * 0.5;
                    audioAver += arr[10] * 0.4;
                    audioAver += arr[11] * 0.3;
                    audioAver += arr[12] * 0.2;
                    audioAver += arr[13] * 0.1;
                    audioAver /= 13.5;
                    break;
                case 2:
                    audioAver += arr[4] * 0.1;
                    audioAver += arr[5] * 0.1;
                    audioAver += arr[6] * 0.2;
                    audioAver += arr[7] * 0.2;
                    audioAver += arr[8] * 0.3;
                    audioAver += arr[9] * 0.5;
                    audioAver += arr[10] * 0.7;
                    audioAver += arr[11] * 0.9;
                    audioAver += arr[12];
                    audioAver += arr[13] * 0.9;
                    audioAver += arr[14] * 0.7;
                    audioAver += arr[15] * 0.5;
                    audioAver += arr[16] * 0.3;
                    audioAver += arr[17] * 0.2;
                    audioAver += arr[18] * 0.2;
                    audioAver += arr[19] * 0.1;
                    audioAver += arr[20] * 0.1;
                    audioAver /= 7;
                    break;
                case 3:
                    audioAver += arr[6] * 0.1;
                    audioAver += arr[7] * 0.1;
                    audioAver += arr[8] * 0.1;
                    audioAver += arr[9] * 0.2;
                    audioAver += arr[10] * 0.3;
                    audioAver += arr[11] * 0.4;
                    audioAver += arr[12] * 0.5;
                    audioAver += arr[13] * 0.6;
                    audioAver += arr[14] * 0.65;
                    audioAver += arr[15] * 0.85;
                    audioAver += arr[16] * 0.9;
                    audioAver += arr[17];
                    audioAver += arr[18];
                    audioAver += arr[19] * 0.9;
                    audioAver += arr[20] * 0.85;
                    audioAver += arr[21] * 0.65;
                    audioAver += arr[22] * 0.6;
                    audioAver += arr[23] * 0.5;
                    audioAver += arr[24] * 0.4;
                    audioAver += arr[25] * 0.3;
                    audioAver += arr[26] * 0.2;
                    audioAver += arr[27] * 0.1;
                    audioAver += arr[28] * 0.1;
                    audioAver += arr[29] * 0.1;
                    audioAver /= 11.4;
                    break;
                case 4:
                    audioAver += arr[9] * 0.1;
                    audioAver += arr[10] * 0.1;
                    audioAver += arr[11] * 0.1;
                    audioAver += arr[12] * 0.1;
                    audioAver += arr[13] * 0.2;
                    audioAver += arr[14] * 0.3;
                    audioAver += arr[15] * 0.4;
                    audioAver += arr[16] * 0.55;
                    audioAver += arr[17] * 0.65;
                    audioAver += arr[18] * 0.8;
                    audioAver += arr[19] * 0.85;
                    audioAver += arr[20] * 0.95;
                    audioAver += arr[21];
                    audioAver += arr[22] * 0.95;
                    audioAver += arr[23] * 0.85;
                    audioAver += arr[24] * 0.8;
                    audioAver += arr[25] * 0.65;
                    audioAver += arr[26] * 0.55;
                    audioAver += arr[27] * 0.4;
                    audioAver += arr[28] * 0.3;
                    audioAver += arr[29] * 0.2;
                    audioAver += arr[30] * 0.1;
                    audioAver += arr[31] * 0.1;
                    audioAver += arr[32] * 0.1;
                    audioAver += arr[33] * 0.1;
                    audioAver /= 11.2;
                    break;
                default:
            }

            bass = audioAver * mus;


            if (bass <= 1) {
                bass = 1;
            };
        },

        clearCanvas: function () {
            context.clearRect(0, 0, canvasWidth, canvasHeight);
        },

        addParticles: function (num) {
            addParticles(this, num);
        },

        ParticleImage: function (imgSrc, blnDefault) {
            if (imgSrc) {
                if (blnDefault == "true") {
                    img.src = imgSrc;
                } else {
                    img.src = 'file:///' + imgSrc;
                }
            } else {
                img.src = 'Content/paitical/0.png';
            }
            img.onload = function () {
                if (img.width > imgWidth || img.height > imgHeight) {
                    var scaling = 0.5;
                    if (img.width > img.height) {
                        scaling = imgWidth / img.width;
                    } else {
                        scaling = imgHeight / img.height;
                    }
                    currantCanvas.width = img.width * scaling;
                    currantCanvas.height = img.height * scaling;
                    currantContext.drawImage(img, 0, 0, currantCanvas.width, currantCanvas.height);
                } else {
                    currantCanvas.width = img.width;
                    currantCanvas.height = img.height;
                    currantContext.drawImage(img, 0, 0);
                }
            }
        },

        startParticles: function () {
            stopParticlesTimer();
            runParticlesTimer(this);
        },

        stopParticles: function () {
            stopParticlesTimer();
        },

        set: function (property, value) {
            switch (property) {
                case 'number':
                case 'linkEnable':
                case 'linkDistance':
                case 'linkWidth':
                case 'linkColor':
                case 'linkOpacity':
                case 'isMove':
                case 'isBounce':
                case 'moveOutMode':
                    this[property] = value;
                    break;
                case 'color':
                case 'opacity':
                case 'opacityRandom':
                case 'shadowColor':
                case 'shadowBlur':
                    this[property] = value;
                    setParticlesGlobalValue(this);
                    break;
                case 'shapeType':
                case 'sizeValue':
                case 'sizeRandom':
                    this[property] = value;
                    setParticleSize(this);
                    break;
                case 'speed':
                case 'speedRandom':
                case 'g_IsMusicRandom':
                case 'musicStrengh':
                case 'directionX':
                case 'directionY':
                case 'isStraight':
                    this[property] = value;
                    setParticlesMoveValue(this);
                    break;
            }
        }

    };

    Particles.DEFAULTS = {
        number: 100,
        opacity: 0.75,
        opacityRandom: false,
        color: '255,255,255',
        shadowColor: '255,255,255',
        shadowBlur: 0,
        shapeType: 'circle',
        sizeValue: 5,
        sizeRandom: true,
        linkEnable: false,
        linkDistance: 100,
        linkWidth: 2,
        linkColor: '255,255,255',
        linkOpacity: 0.75,
        isMove: true,
        speed: 2,
        speedRandom: true,
        g_IsMusicRandom: false,
        musicStrengh: 100,
        direction: 0,
        direction: 0,
        isStraight: false,
        isBounce: false,
        moveOutMode: 'out'
    };

    var old = $.fn.particles;

    $.fn.particles = function (option) {
        var args = (arguments.length > 1) ? Array.prototype.slice.call(arguments, 1) : undefined;

        return this.each(function () {
            var $this = $(this);
            var data = $this.data('particles');
            var options = $.extend({}, Particles.DEFAULTS, $this.data(), typeof option === 'object' && option);

            if (!data && typeof option === 'string') {
                return;
            }
            if (!data) {
                $this.data('particles', (data = new Particles(this, options)));
            }
            else if (typeof option === 'string') {
                Particles.prototype[option].apply(data, args);
            }
        });
    };

    $.fn.particles.Constructor = Particles;

    $.fn.particles.noConflict = function () {
        $.fn.particles = old;
        return this;
    };

});