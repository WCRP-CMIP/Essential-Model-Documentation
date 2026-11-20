/*
  EMD theme behaviour.

  Right-hand "On this page" menu: collapsed by default on every page. A button
  replaces its title visually (the title stays in the page for Material's own
  small-screen drawer) and expands or collapses the list.
*/
(function () {
  var CHEVRON =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" ' +
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function setupToc() {
    var navs = document.querySelectorAll(".md-sidebar--secondary .md-nav--secondary");
    navs.forEach(function (nav, i) {
      if (nav.dataset.emdToc) return;
      var title = nav.querySelector(":scope > .md-nav__title");
      var list = nav.querySelector(":scope > .md-nav__list");
      if (!title || !list) return;

      nav.dataset.emdToc = "1";
      nav.classList.add("emd-toc", "emd-toc--collapsed");
      if (!list.id) list.id = "emd-toc-list-" + i;

      var button = document.createElement("button");
      button.type = "button";
      button.className = "emd-toc__toggle";
      button.setAttribute("aria-controls", list.id);
      button.setAttribute("aria-expanded", "false");
      button.innerHTML = "<span>" + title.textContent.trim() + "</span>" + CHEVRON;
      button.addEventListener("click", function () {
        var open = !nav.classList.toggle("emd-toc--collapsed");
        button.setAttribute("aria-expanded", String(open));
      });
      title.insertAdjacentElement("afterend", button);
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setupToc);
  else setupToc();
})();
