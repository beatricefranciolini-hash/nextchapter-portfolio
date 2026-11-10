// Mobile menu and tap-to-enlarge images. The site works without JavaScript; this only adds comfort.
(function () {
  var btn = document.querySelector(".menu-btn");
  var nav = document.getElementById("nav");
  if (btn && nav) {
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var box = document.querySelector(".lightbox");
  if (!box || typeof box.showModal !== "function") return;
  var big = box.querySelector("img");
  document.querySelectorAll("main figure img").forEach(function (img) {
    img.setAttribute("tabindex", "0");
    img.setAttribute("role", "button");
    img.setAttribute("aria-label", "Enlarge: " + (img.alt || "image"));
    function open() {
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      box.showModal();
    }
    img.addEventListener("click", open);
    img.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
    });
  });
  box.addEventListener("click", function () { box.close(); });
})();
