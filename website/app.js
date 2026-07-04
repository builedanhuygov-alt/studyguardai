// StudyGuard AI website -- V2 interaction wiring. Pure vanilla JS, no build step.
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    // Sticky glass header on scroll
    var header = document.getElementById("site-header");
    window.addEventListener("scroll", function () {
      header.classList.toggle("scrolled", window.scrollY > 8);
    });

    // Theme toggle (persisted)
    var stored = localStorage.getItem("sg-theme");
    if (stored) document.documentElement.setAttribute("data-theme", stored);
    document.getElementById("theme-toggle").addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", current);
      localStorage.setItem("sg-theme", current);
    });

    if (window.SG) {
      SG.revealOnScroll(".reveal");
      SG.magnetic(".magnetic");
      SG.ripple(".ripple");
      SG.tilt(".tilt", 6);
      SG.ambientOrbs(document.getElementById("hero-canvas"));
      SG.ring(document.getElementById("hero-ring"), { value: 82, max: 100, size: 84, stroke: 8, color: "#4F46E5" });
      SG.countUp(document.getElementById("stat-score"), 87, { duration: 1200 });
      SG.countUp(document.getElementById("stat-focus"), 91, { duration: 1300 });
      document.getElementById("stat-streak").textContent = "0d";
      var streakEl = document.getElementById("stat-streak");
      var s = 0;
      var streakTimer = setInterval(function () { s++; streakEl.textContent = s + "d"; if (s >= 14) clearInterval(streakTimer); }, 70);

      document.querySelectorAll(".stat .num[data-count]").forEach(function (el) {
        var target = parseFloat(el.getAttribute("data-count"));
        var decimals = target % 1 !== 0 ? 1 : 0;
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) { SG.countUp(el, target, { duration: 1400, decimals: decimals }); io.unobserve(el); }
          });
        }, { threshold: 0.4 });
        io.observe(el);
      });
    }
  });
})();
