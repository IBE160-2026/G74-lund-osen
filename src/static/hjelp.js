// Story 8.0f: hjelpen ved «?» i ett fast felt som ikke dekker siden
// (avgjort 21.10 kl. 22:47 og 24.10 kl. 11:31 og 11:34). Uten skriptet er
// vinduene popover (auto) midt på skjermen, som i 8.0b. Skriptet setter
// klassen hjelpefelt på <html>, og bare da gjelder stilen for feltet.
// Fra 1024 px står feltet fast i kanten, og stilen gir plass. Smalere står
// det over en tom plass rett under «?», like høy som feltet.
"use strict";

(function () {
  const BRED = window.matchMedia("(min-width: 1024px)");
  const rot = document.documentElement;
  let knappen = null; // «?» som åpnet feltet, og som får fokus tilbake
  let plassen = null; // den tomme plassen under «?» på smal skjerm

  function aapent() {
    return document.querySelector(".hjelpevindu:popover-open");
  }

  // Blokken som går over hele bredden, 16 px fra kantene som feltet, så
  // ingenting står ved siden av plassen.
  function hel(el) {
    const b = el.getBoundingClientRect();
    const bredde = document.documentElement.clientWidth;
    return !getComputedStyle(el).display.startsWith("inline") && b.left <= 17 && b.right >= bredde - 17;
  }

  function fjernPlassen() {
    if (plassen) plassen.remove();
    plassen = null;
  }

  // Setter inn plassen under «?» og legger feltet over den. Høyden settes
  // når feltet vises (hoeyde), fordi det ikke kan måles før.
  function lagPlassen(felt, knapp) {
    fjernPlassen();
    if (BRED.matches || !knapp) return;
    const rad = knapp.closest("tr");
    if (rad) {
      plassen = document.createElement("tr");
      const celle = plassen.insertCell();
      celle.colSpan = Array.from(rad.cells).reduce((sum, c) => sum + c.colSpan, 0);
      rad.after(plassen);
    } else {
      let blokk = knapp.parentElement;
      while (blokk.parentElement !== document.body && !hel(blokk)) blokk = blokk.parentElement;
      plassen = document.createElement("div");
      blokk.after(plassen);
    }
    plassen.className = "hjelpeplass";
    plassen.setAttribute("aria-hidden", "true");
    felt.style.setProperty("--topp", plassen.getBoundingClientRect().top + window.scrollY + "px");
  }

  function hoeyde(felt) {
    if (plassen) plassen.style.height = felt.offsetHeight + 16 + "px";
  }

  document.addEventListener("click", (e) => {
    const knapp = e.target.closest("button.hjelpeknapp");
    if (knapp) knappen = knapp;
  }, true);

  // beforetoggle og toggle bobler ikke, så de fanges på vei ned.
  document.addEventListener("beforetoggle", (e) => {
    const felt = e.target;
    if (!felt.classList || !felt.classList.contains("hjelpevindu")) return;
    if (e.newState === "open") {
      const forrige = aapent();
      if (forrige && forrige !== felt) forrige.hidePopover();
      lagPlassen(felt, knappen);
    } else {
      fjernPlassen();
    }
  }, true);

  document.addEventListener("toggle", (e) => {
    const felt = e.target;
    if (!felt.classList || !felt.classList.contains("hjelpevindu")) return;
    if (e.newState === "open") {
      hoeyde(felt);
      felt.focus();
    } else if (!aapent() && knappen && knappen.isConnected) {
      knappen.focus();
    }
  }, true);

  document.addEventListener("keydown", (e) => {
    const felt = aapent();
    if (e.key === "Escape" && felt) felt.hidePopover();
  });

  BRED.addEventListener("change", () => {
    const felt = aapent();
    if (felt) {
      lagPlassen(felt, knappen);
      hoeyde(felt);
    }
  });

  for (const felt of document.querySelectorAll(".hjelpevindu[popover]")) {
    felt.popover = "manual";
    felt.tabIndex = -1;
  }
  for (const knapp of document.querySelectorAll("button.hjelpeknapp")) {
    knapp.popoverTargetAction = "show";
  }
  rot.classList.add("hjelpefelt");
})();
