var CrbUI_A_CONF;
var CrbUI_AP;

(function()
{
	var a = !1,
		e = {
			COLOR: "#B9E5FA",
			LINE_WIDTH: 10,
			SIZE: 36,
			PATH: "",
			JQUERY: jQuery
		};

	CrbUI_A_CONF = e;
	e.JQUERY(document).ready(function () {
		CrbUI_AP || (CrbUI_AP = new f)
	});

	function f() {
		this.init();
		this.render()
	}
	f.prototype.init = function () {
		this.g = e.OVERLAY;
		this.d = Modernizr.canvas;
		this.i = this.c = Modernizr.audio;
		a == this.i && g(this);
		if (this.g && (this.k = null != e.OVERLAY_DELAY ? e.OVERLAY_DELAY : 5E3, a == Modernizr.audio.mp3)) {
			var b = e.JQUERY("<div />");
			e.JQUERY(b).css("position", "absolute");
			e.JQUERY(b).css("left", "0px");
			e.JQUERY(b).css("top", "0px");
			var c = '/static/' + "CrbUI/audio/button/swf/CrbUI_AP_Overlay.swf";
			e.JQUERY(b).html('<object id="CrbUI_AP_Overlay" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="1" height="1"><param name="movie" value="' + c + '" /><param name="wmode" value="transparent" /><\!--[if !IE]>--\><object type="application/x-shockwave-flash" data="' + c + '" width="1" height="1"><\!--<![endif]--\><p><a href="http://get.adobe.com/flashplayer/">Adobe Flash Player</a> Is Required</p><\!--[if !IE]>--\></object><\!--<![endif]--\></object>');
			e.JQUERY(document.body).append(b);
			swfobject.registerObject("CrbUI_AP_Overlay", "9.0.115", '/static/' + "CrbUI/audio/button/swf/expressInstall.swf");
			this.p = swfobject.getObjectById("CrbUI_AP_Overlay")
		}
	};
	f.prototype.render = function (b) {
		e.JQUERY(".CrbUI_AudioButton", b).each(function (b, d) {
			new h(e.JQUERY(d).get())
		})
	};

	function g(b) {
		var c = e.JQUERY("<div />");
		e.JQUERY(c).css("position", "absolute");
		e.JQUERY(c).css("left", "0px");
		e.JQUERY(c).css("top", "0px");
		var d = '/static/' + "CrbUI/audio/button/swf/CrbUI_AP.swf";
		e.JQUERY(c).html('<object id="CrbUI_AP_Flash" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="1" height="1"><param name="movie" value="' + d + '" /><param name="wmode" value="transparent" /><\!--[if !IE]>--\><object type="application/x-shockwave-flash" data="' + d + '" width="1" height="1"><\!--<![endif]--\><p><a href="http://get.adobe.com/flashplayer/">Adobe Flash Player</a> Is Required</p><\!--[if !IE]>--\></object><\!--<![endif]--\></object>');
		e.JQUERY(document.body).append(c);
		swfobject.registerObject("CrbUI_AP_Flash", "9.0.115", '/static/' + "CrbUI/audio/button/swf/expressInstall.swf");
		b.e = swfobject.getObjectById("CrbUI_AP_Flash")
	}
	f.prototype.swfReady = function () {
		this.b && i(this)
	};
	f.prototype.play = function (b) {
		if (this.b == b) if (this.c) this.a.play();
		else try {
				this.e._resume()
			} catch (c) {
				console.log("CrbUI_AudioButton error resumeFlash")
			} else {
			this.stop();
			this.b = b;
			if (this.i) {
				this.c = !0;
				this.a = new Audio;
				e.JQUERY(this.a).attr("preload", "auto");
				b = e.JQUERY(this.b.element).attr("id"); - 1 == b.search(".mp3") && (b += "");
				var d = e.JQUERY(this.b.element).attr("id"); - 1 == d.search(".ogg") && (d += ".ogg");
				this.a.src = Modernizr.audio.mp3 ? b : d;
				e.JQUERY(this.a).bind("error", e.JQUERY.proxy(this.l, this));
				e.JQUERY(document.body).append(this.a);
				e.JQUERY(this.a).bind("ended", e.JQUERY.proxy(this.onEnded, this));
				e.JQUERY(this.a).bind("timeupdate", e.JQUERY.proxy(this.onPosition, this));
				this.g && e.JQUERY(this.a).bind("play", e.JQUERY.proxy(this.n, this));
				try {
					this.a.currentTime = formatMillisecondsToSeconds(this.b.element[0].getAttribute('data-inpoint'));
				}
				catch (e) {
					console.error("Failed to play from inpoint");
				}
				this.a.play()
			} else i(this);
			this.d && (b = this.b.canvas.getContext("2d"), b.translate(0.5 * this.b.size, 0.5 * this.b.size), b.rotate(-90 * (Math.PI / 180)))
		}
		j(this.b, !0)
	};
	f.prototype.l = function () {
		this.c = a;
		e.JQUERY(this.a).unbind();
		e.JQUERY(this.a).remove();
		this.e ? i(this) : g(this)
	};
	f.prototype.n = function () {
		k(this)
	};

	function k(b) {
		b.h = setTimeout(e.JQUERY.proxy(b.o, b), 500 * Math.random() + b.k)
	}
	f.prototype.o = function () {
		if (Modernizr.audio.mp3) {
			var b = new Audio;
			e.JQUERY(b).attr("src", this.g);
			b.play()
		} else this.p._play(this.g);
		k(this)
	};

	function i(b) {
		b.c = a;
		var c = e.JQUERY(b.b.element).attr("id"); - 1 == c.search(".mp3") && (c += "");
		b.e._play(c)
	}
	f.prototype.stop = function (b) {
		this.h && clearTimeout(this.h);
		this.b && (this.b == b ? (this.c ? this.a.pause() : this.e._pause(), j(this.b, a)) : this.reset())
	};
	f.prototype.reset = function () {
		this.c ? l(this) : this.e._stop();
		m(this)
	};

	function l(b) {
		e.JQUERY(b.a).unbind();
		b.a.pause();
		b.a.src = "";
		e.JQUERY(b.a).remove();
		b.a = null
	}
	function m(b) {
		j(b.b, a);
		if (b.d) {
			var c = b.b.canvas.getContext("2d");
			c.setTransform(1, 0, 0, 1, 0, 0);
			c.clearRect(0, 0, b.b.canvas.width, b.b.canvas.height)
		}
		b.b = null
	}
	f.prototype.onEnded = function () {
		this.h && clearTimeout(this.h);
		this.c ? l(this) : this.e._stop();
		n(this.b, 1);
		m(this)
	};
	f.prototype.onPosition = function (b) {
		this.c ? this.a.duration && this.a.currentTime && n(this.b, this.a.currentTime / this.a.duration) : n(this.b, b)
	};

	function h(b) {
		b ? (this.element = b, e.JQUERY(this.element).css("position", "relative")) : this.element = e.JQUERY('<div style="position:relative;"/>');
		this.size = void 0 !== e.JQUERY(this.element).attr("width") ? e.JQUERY(this.element).attr("width") : e.SIZE;
		this.lineWidth = 0.5 * this.size - 0.5 * e.LINE_WIDTH - 1;
		e.JQUERY(this.element).css("width", this.size);
		e.JQUERY(this.element).css("height", this.size);
		if (this.d = Modernizr.canvas) this.canvas = document.createElement("canvas"), this.canvas.setAttribute("width", this.size), this.canvas.setAttribute("height", this.size), e.JQUERY(this.canvas).css("position", "absolute"), e.JQUERY(this.canvas).css("top", "0px"), e.JQUERY(this.canvas).css("left", "0px"), e.JQUERY(this.canvas).css("background-color", "#3c3c3c");
		this.f = e.JQUERY('<img src="' + '/static/' + 'images/play_button_white.svg" width="' + this.size + '" height="' + this.size + '" style="position:absolute; top:0px; left:0px;" />');
		this.j = 2 * Math.PI;
		e.JQUERY(this.f).click(e.JQUERY.proxy(this.m, this));
		this.d && e.JQUERY(this.element).append(this.canvas);
		e.JQUERY(this.element).append(this.f);
	}

	function n(b, c) {
		if (b.d) {
			var d = b.canvas.getContext("2d");
			d.clearRect(0, 0, b.canvas.width, b.canvas.height);
			d.beginPath();
			d.arc(0, 0, b.lineWidth, 0, c * b.j, a);
			d.strokeStyle = e.COLOR;
			d.lineWidth = e.LINE_WIDTH;
			d.stroke()
		}
	}
	function j(b, c) {
		c ? e.JQUERY(b.f).attr("src", '/static/' + "images/pause_button_white.svg") : e.JQUERY(b.f).attr("src", '/static/' + "images/play_button_white.svg")
	}
	h.prototype.m = function () {
		e.JQUERY(this.f).attr("src") == '/static/' + "images/play_button_white.svg" ? CrbUI_AP.play(this) : CrbUI_AP.stop(this)
	};
	function formatMillisecondsToSeconds(milliseconds) {
		return milliseconds / 1000;
	}

})()
