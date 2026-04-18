(function () {
  "use strict";

  /* Mobile nav */
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (!open) {
        nav.querySelectorAll(".nav-item--dropdown.is-open").forEach(function (li) {
          li.classList.remove("is-open");
        });
      }
    });
  }

  /* Mobile: tap About to expand submenu (desktop uses hover) */
  var mqMobileNav = window.matchMedia("(max-width: 900px)");
  document.querySelectorAll(".nav-parent").forEach(function (parent) {
    parent.addEventListener("click", function (e) {
      if (!mqMobileNav.matches || !nav || !nav.classList.contains("is-open")) return;
      var li = parent.closest(".nav-item--dropdown");
      if (!li) return;
      e.preventDefault();
      var willOpen = !li.classList.contains("is-open");
      nav.querySelectorAll(".nav-item--dropdown.is-open").forEach(function (o) {
        if (o !== li) o.classList.remove("is-open");
      });
      li.classList.toggle("is-open", willOpen);
    });
  });

  /* Count-up counters */
  function animateValue(el, end, duration) {
    var start = 0;
    var startTime = null;
    function step(ts) {
      if (!startTime) startTime = ts;
      var p = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(start + (end - start) * eased);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  var counterEls = document.querySelectorAll(".counter__value[data-target]");
  if (counterEls.length && "IntersectionObserver" in window) {
    var obs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var target = parseInt(el.getAttribute("data-target"), 10);
          if (!isNaN(target)) animateValue(el, target, 1200);
          obs.unobserve(el);
        });
      },
      { threshold: 0.3 }
    );
    counterEls.forEach(function (el) {
      obs.observe(el);
    });
  }

  /* Event countdown */
  function pad(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function renderCountdown(el) {
    var raw = el.getAttribute("data-deadline");
    if (!raw) return;
    var end = new Date(raw).getTime();
    function tick() {
      var now = Date.now();
      var diff = end - now;
      if (diff <= 0) {
        el.textContent = "Event Ended";
        if (el._tid) clearInterval(el._tid);
        return;
      }
      var d = Math.floor(diff / 86400000);
      var h = Math.floor((diff % 86400000) / 3600000);
      var m = Math.floor((diff % 3600000) / 60000);
      var s = Math.floor((diff % 60000) / 1000);
      el.textContent =
        d +
        " " +
        (d === 1 ? "Day" : "Days") +
        " " +
        pad(h) +
        " Hrs " +
        pad(m) +
        " Min " +
        pad(s) +
        " Sec";
    }
    tick();
    if (Date.now() < end) {
      el._tid = setInterval(tick, 1000);
    }
  }

  document
    .querySelectorAll(
      ".entry-countdown[data-deadline], .event-countdown[data-deadline]"
    )
    .forEach(renderCountdown);

  /* Static contact form */
  var form = document.querySelector("[data-contact-form]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      alert(
        "This is a static preview site. Please email operationatcloud@gmail.com with your message, or connect a form backend to this form."
      );
    });
  }

  /* Newsletter form — opens mail client to complete subscription */
  document
    .querySelectorAll("[data-newsletter-form]")
    .forEach(function (nf) {
      nf.addEventListener("submit", function (e) {
        e.preventDefault();
        var input = nf.querySelector('input[type="email"]');
        var email = (input && input.value ? input.value : "").trim();
        var subject = encodeURIComponent("Please add me to the @Cloud newsletter");
        var body = encodeURIComponent(
          "Hi @Cloud team,\n\nPlease subscribe " + email + " to the newsletter.\n\nThanks!"
        );
        window.location.href =
          "mailto:operationatcloud@gmail.com?subject=" +
          subject +
          "&body=" +
          body;
      });
    });

  /* Testimonial carousel — auto-rotate groups of visible items (responsive) */
  document
    .querySelectorAll("[data-testimonial-carousel]")
    .forEach(function (root) {
      var track = root.querySelector(".testimonial-track");
      var pag = root.querySelector(".testimonial-pagination");
      if (!track || !pag) return;
      var items = Array.prototype.slice.call(
        track.querySelectorAll(".testimonial-item")
      );
      if (items.length < 2) return;
      var interval = parseInt(root.getAttribute("data-interval"), 10) || 6000;
      var mqOne = window.matchMedia("(max-width: 768px)");

      function visibleCount() {
        return mqOne.matches ? 1 : 2;
      }

      function pageCount() {
        return Math.max(1, Math.ceil(items.length / visibleCount()));
      }

      var index = 0;
      var timer = null;

      function render() {
        var per = visibleCount();
        items.forEach(function (el, i) {
          var page = Math.floor(i / per);
          el.classList.toggle("is-hidden", page !== index);
        });
        var dots = pag.querySelectorAll("button");
        dots.forEach(function (d, i) {
          if (i === index) {
            d.setAttribute("aria-current", "true");
          } else {
            d.removeAttribute("aria-current");
          }
        });
      }

      function buildPagination() {
        pag.innerHTML = "";
        var n = pageCount();
        for (var i = 0; i < n; i++) {
          (function (i) {
            var b = document.createElement("button");
            b.type = "button";
            b.setAttribute("aria-label", "Go to slide " + (i + 1));
            b.addEventListener("click", function () {
              index = i;
              render();
              restart();
            });
            pag.appendChild(b);
          })(i);
        }
      }

      function next() {
        index = (index + 1) % pageCount();
        render();
      }

      function start() {
        stop();
        if (pageCount() > 1) timer = setInterval(next, interval);
      }
      function stop() {
        if (timer) clearInterval(timer);
        timer = null;
      }
      function restart() {
        start();
      }

      buildPagination();
      render();
      start();

      root.addEventListener("mouseenter", stop);
      root.addEventListener("mouseleave", start);

      var resize;
      window.addEventListener("resize", function () {
        clearTimeout(resize);
        resize = setTimeout(function () {
          index = 0;
          buildPagination();
          render();
          restart();
        }, 150);
      });
    });
})();
