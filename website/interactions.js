// StudyGuard AI Design System V2 -- shared interaction toolkit.
// Dependency-free (no Three.js/React needed). Respects prefers-reduced-motion.
// Used by website/ and desktop/frontend/. Exposes window.SG.
(function (global) {
  "use strict";
  var REDUCED = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function revealOnScroll(selector) {
    selector = selector || ".reveal";
    var items = document.querySelectorAll(selector);
    if (!items.length) return;
    if (REDUCED || !("IntersectionObserver" in global)) { items.forEach(function (el) { el.classList.add("is-visible"); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-visible"); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    items.forEach(function (el) { io.observe(el); });
  }

  function magnetic(selector, strength) {
    if (REDUCED) return;
    strength = strength || 14;
    document.querySelectorAll(selector || ".magnetic").forEach(function (el) {
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) / r.width;
        var y = (e.clientY - r.top - r.height / 2) / r.height;
        el.style.transform = "translate(" + (x * strength) + "px," + (y * strength) + "px)";
      });
      el.addEventListener("mouseleave", function () { el.style.transform = ""; });
    });
  }

  function ripple(selector) {
    document.querySelectorAll(selector || ".ripple").forEach(function (el) {
      el.addEventListener("click", function (e) {
        var r = el.getBoundingClientRect();
        var dot = document.createElement("span");
        var size = Math.max(r.width, r.height);
        dot.className = "ripple-dot";
        dot.style.width = dot.style.height = size + "px";
        dot.style.left = (e.clientX - r.left - size / 2) + "px";
        dot.style.top = (e.clientY - r.top - size / 2) + "px";
        el.appendChild(dot);
        setTimeout(function () { dot.remove(); }, 650);
      });
    });
  }

  function tilt(selector, max) {
    if (REDUCED) return;
    max = max || 8;
    document.querySelectorAll(selector || ".tilt").forEach(function (el) {
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width - 0.5;
        var py = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = "perspective(900px) rotateY(" + (px * max) + "deg) rotateX(" + (-py * max) + "deg)";
      });
      el.addEventListener("mouseleave", function () { el.style.transform = ""; });
    });
  }

  function countUp(el, target, opts) {
    opts = opts || {};
    var dur = REDUCED ? 0 : (opts.duration || 900);
    var decimals = opts.decimals || 0;
    var start = performance.now();
    if (dur === 0) { el.textContent = target.toFixed(decimals); return; }
    function tick(now) {
      var t = Math.min(1, (now - start) / dur);
      var eased = 1 - Math.pow(1 - t, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function toast(message, opts) {
    opts = opts || {};
    var duration = opts.duration || 4000;
    var host = document.getElementById("sg-toast-host");
    if (!host) {
      host = document.createElement("div");
      host.id = "sg-toast-host";
      host.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);display:flex;flex-direction:column;gap:8px;z-index:1100;";
      document.body.appendChild(host);
    }
    var el = document.createElement("div");
    el.className = "sg-toast glass";
    el.style.cssText = "padding:10px 16px;border-radius:999px;font-size:14px;animation:sg-scale-in .25s ease;box-shadow:var(--shadow-md);color:var(--text)";
    el.textContent = message;
    host.appendChild(el);
    setTimeout(function () {
      el.style.transition = "opacity .3s"; el.style.opacity = "0";
      setTimeout(function () { el.remove(); }, 300);
    }, duration);
  }

  function confetti(container, count) {
    if (REDUCED) return;
    container = container || document.body;
    count = count || 60;
    var colors = ["#6366F1", "#7C3AED", "#F59E0B", "#10B981"];
    for (var i = 0; i < count; i++) {
      var p = document.createElement("span");
      var size = 6 + Math.random() * 6;
      p.style.cssText = "position:fixed;top:-10px;left:" + (Math.random() * 100) + "vw;width:" + size + "px;height:" + size + "px;background:" + colors[i % colors.length] + ";border-radius:" + (Math.random() > 0.5 ? "50%" : "3px") + ";z-index:1200;pointer-events:none;";
      var duration = 1800 + Math.random() * 1200;
      var drift = (Math.random() - 0.5) * 200;
      if (p.animate) {
        p.animate(
          [{ transform: "translate(0,0) rotate(0deg)", opacity: 1 }, { transform: "translate(" + drift + "px,100vh) rotate(" + (360 + Math.random() * 360) + "deg)", opacity: 0.9 }],
          { duration: duration, easing: "cubic-bezier(.2,.6,.4,1)" }
        );
      }
      container.appendChild(p);
      setTimeout(function (node) { return function () { node.remove(); }; }(p), duration + 50);
    }
  }

  function ambientOrbs(canvasEl) {
    if (!canvasEl) return;
    var ctx = canvasEl.getContext("2d");
    var w, h, orbs;
    function resize() {
      w = canvasEl.width = canvasEl.offsetWidth * (global.devicePixelRatio || 1);
      h = canvasEl.height = canvasEl.offsetHeight * (global.devicePixelRatio || 1);
    }
    resize();
    global.addEventListener("resize", resize);
    orbs = Array.from({ length: 5 }, function () {
      return {
        x: Math.random() * w, y: Math.random() * h, r: (80 + Math.random() * 160) * (global.devicePixelRatio || 1),
        vx: (Math.random() - 0.5) * 0.15, vy: (Math.random() - 0.5) * 0.15,
        hue: Math.random() > 0.5 ? "99,102,241" : "124,58,237"
      };
    });
    function draw() {
      ctx.clearRect(0, 0, w, h);
      orbs.forEach(function (o) {
        o.x += o.vx; o.y += o.vy;
        if (o.x < -o.r) o.x = w + o.r; if (o.x > w + o.r) o.x = -o.r;
        if (o.y < -o.r) o.y = h + o.r; if (o.y > h + o.r) o.y = -o.r;
        var g = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.r);
        g.addColorStop(0, "rgba(" + o.hue + ",0.20)");
        g.addColorStop(1, "rgba(" + o.hue + ",0)");
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(o.x, o.y, o.r, 0, Math.PI * 2); ctx.fill();
      });
      if (!REDUCED) requestAnimationFrame(draw);
    }
    draw();
  }

  function ring(el, opts) {
    opts = opts || {};
    var value = opts.value || 0, max = opts.max || 100, size = opts.size || 96, stroke = opts.stroke || 10;
    var color = opts.color || "#4F46E5", track = opts.track || "rgba(255,255,255,.08)";
    var r = (size - stroke) / 2;
    var c = 2 * Math.PI * r;
    var pct = Math.max(0, Math.min(1, value / max));
    el.innerHTML = '<svg width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '" role="img" aria-label="' + Math.round(pct * 100) + '%">' +
      '<circle cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" fill="none" stroke="' + track + '" stroke-width="' + stroke + '"/>' +
      '<circle class="sg-ring-progress" cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" fill="none" stroke="' + color + '" stroke-width="' + stroke + '" stroke-linecap="round" stroke-dasharray="' + c + '" stroke-dashoffset="' + c + '" transform="rotate(-90 ' + size / 2 + ' ' + size / 2 + ')"/></svg>';
    var circle = el.querySelector(".sg-ring-progress");
    requestAnimationFrame(function () {
      circle.style.transition = REDUCED ? "none" : "stroke-dashoffset 900ms cubic-bezier(.2,0,0,1)";
      circle.style.strokeDashoffset = String(c * (1 - pct));
    });
  }

  function sparkline(el, values, opts) {
    opts = opts || {};
    values = values || [];
    var color = opts.color || "#4F46E5", height = opts.height || 40;
    if (!values.length) { el.innerHTML = ""; return; }
    var w = el.clientWidth || 160, h = height;
    var min = Math.min.apply(null, values), max = Math.max.apply(null, values);
    var span = max - min || 1;
    var points = values.map(function (v, i) {
      var x = (i / (values.length - 1 || 1)) * w;
      var y = h - ((v - min) / span) * h;
      return x + "," + y;
    }).join(" ");
    el.innerHTML = '<svg width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none">' +
      '<polyline points="' + points + '" fill="none" stroke="' + color + '" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sg-spark-line"/></svg>';
    var line = el.querySelector(".sg-spark-line");
    var len = line.getTotalLength ? line.getTotalLength() : 300;
    line.style.strokeDasharray = String(len); line.style.strokeDashoffset = String(len);
    requestAnimationFrame(function () {
      line.style.transition = REDUCED ? "none" : "stroke-dashoffset 900ms ease-out";
      line.style.strokeDashoffset = "0";
    });
  }

  function commandPalette(opts) {
    var items = opts.items, onRun = opts.onRun;
    var el = document.getElementById("sg-command-palette");
    if (!el) {
      el = document.createElement("div");
      el.id = "sg-command-palette";
      el.setAttribute("role", "dialog");
      el.setAttribute("aria-modal", "true");
      el.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:1200;display:none;align-items:flex-start;justify-content:center;padding-top:12vh;";
      el.innerHTML = '<div class="glass" style="width:min(560px,92vw);border-radius:16px;box-shadow:var(--shadow-lg);overflow:hidden">' +
        '<input id="sg-cmd-input" placeholder="Search actions, pages..." style="width:100%;box-sizing:border-box;padding:16px;border:0;background:transparent;color:var(--text);font-size:16px;outline:none;border-bottom:1px solid var(--border)"/>' +
        '<div id="sg-cmd-list" style="max-height:320px;overflow:auto;padding:6px"></div></div>';
      document.body.appendChild(el);
      el.addEventListener("click", function (e) { if (e.target === el) close(); });
    }
    var input = el.querySelector("#sg-cmd-input");
    var list = el.querySelector("#sg-cmd-list");
    function render(filter) {
      var f = (filter || "").toLowerCase();
      var filtered = items.filter(function (i) { return i.label.toLowerCase().indexOf(f) !== -1; });
      list.innerHTML = filtered.length ? filtered.map(function (i, idx) {
        return '<div class="sg-cmd-item" data-idx="' + idx + '" style="padding:10px 12px;border-radius:10px;cursor:pointer;display:flex;justify-content:space-between" tabindex="0">' + i.label + '<span style="color:var(--text-muted,#9AA4B2)">' + (i.hint || "") + '</span></div>';
      }).join("") : '<div style="padding:12px;color:var(--text-muted,#9AA4B2)">No results</div>';
      list.querySelectorAll(".sg-cmd-item").forEach(function (node) {
        node.addEventListener("mouseenter", function () { node.style.background = "rgba(99,102,241,.15)"; });
        node.addEventListener("mouseleave", function () { node.style.background = ""; });
        node.addEventListener("click", function () { var item = filtered[Number(node.dataset.idx)]; close(); onRun(item); });
      });
    }
    function open() { el.style.display = "flex"; input.value = ""; render(); input.focus(); }
    function close() { el.style.display = "none"; }
    input.addEventListener("input", function () { render(input.value); });
    document.addEventListener("keydown", function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); el.style.display === "flex" ? close() : open(); }
      if (e.key === "Escape") close();
    });
    return { open: open, close: close };
  }

  global.SG = {
    revealOnScroll: revealOnScroll, magnetic: magnetic, ripple: ripple, tilt: tilt, countUp: countUp,
    toast: toast, confetti: confetti, ambientOrbs: ambientOrbs, ring: ring, sparkline: sparkline,
    commandPalette: commandPalette, REDUCED: REDUCED
  };
})(window);
