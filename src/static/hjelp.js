// Story 8.0f: hjelpen ved «?» i ett fast felt som ikke dekker siden
// (avgjort 21.10 kl. 22:47 og 24.10 kl. 11:31 og 11:34). Uten skriptet er
// vinduene popover (auto) midt på skjermen, som i 8.0b. Skriptet setter
// klassen hjelpefelt på <html>, og bare da gjelder stilen for feltet.
// Fra 1056 px står feltet fast i kanten, og stilen gir plass. Smalere står
// det over en tom plass rett under «?», like høy som feltet.
"use strict";

(function () {
  // Gjennomgangen (ECH3): uten popover i nettleseren står hjelpen som før.
  if (!("popover" in HTMLElement.prototype)) return;
  const BRED = window.matchMedia("(min-width: 1056px)");
  const rot = document.documentElement;
  let knappen = null; // «?» som åpnet feltet, og som får fokus tilbake
  let plassen = null; // den tomme plassen under «?» på smal skjerm
  const SIDEN = "hjelpefelt-side"; // venstre eller hoeyre, i sessionStorage

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
  // når feltet vises (hoeyde), fordi det ikke kan måles før. En rad i en
  // tabell får plassen som en ny rad når tabellen går over hele bredden
  // (gjennomgangen, BH7).
  function lagPlassen(felt, knapp) {
    fjernPlassen();
    if (BRED.matches || !knapp) return;
    const rad = knapp.closest("tr");
    if (rad && hel(rad.closest("table"))) {
      plassen = document.createElement("tr");
      const celle = plassen.insertCell();
      celle.colSpan = Array.from(rad.cells).reduce((sum, c) => sum + c.colSpan, 0);
      rad.after(plassen);
    } else {
      // Gjennomgangen (ECH4, BH8): aldri forbi et barn av <body>.
      let blokk = (rad ? rad.closest("table") : knapp).parentElement;
      while (blokk.parentElement && blokk.parentElement !== document.body && !hel(blokk)) blokk = blokk.parentElement;
      plassen = document.createElement("div");
      blokk.after(plassen);
    }
    plassen.className = "hjelpeplass";
    plassen.setAttribute("aria-hidden", "true");
    plasser(felt);
  }

  function plasser(felt) {
    if (plassen) felt.style.setProperty("--topp", plassen.getBoundingClientRect().top + window.scrollY + "px");
  }

  function hoeyde(felt) {
    if (plassen) plassen.style.height = felt.offsetHeight + 16 + "px";
  }

  // Gjennomgangen (BH4, ECH1): feltet og plassen følger med når siden eller
  // feltet endrer størrelse, for eksempel når skriftene er lastet eller
  // telefonen snus.
  const observatoer = new ResizeObserver(() => {
    const felt = aapent();
    if (felt && plassen) {
      hoeyde(felt);
      plasser(felt);
    }
  });
  observatoer.observe(document.body);

  document.addEventListener("click", (e) => {
    const knapp = e.target.closest("button.hjelpeknapp");
    if (!knapp) return;
    const forrige = knappen;
    knappen = knapp;
    // Gjennomgangen av 8.2b (BH1): vinduene for «Ga» og «Målt mot» har en
    // knapp i hvert sjekkort (gruppens svar 04.11 kl. 09:58). Er vinduet
    // alt åpent fra en annen knapp, gir «show» ingen toggle, så feltet
    // flyttes hit her.
    const felt = knapp.popoverTargetElement;
    // Story 8.23 (A3, brukertesten 10.11): et nytt trykk på samme «?» lukker
    // hjelpen. Knappen har action «show», så klikket stoppes her, og feltet
    // lukkes som med «Lukk».
    if (felt && felt.matches(":popover-open") && forrige === knapp) {
      e.preventDefault();
      felt.hidePopover();
      return;
    }
    if (felt && felt.matches(":popover-open") && forrige !== knapp) {
      lagPlassen(felt, knapp);
      hoeyde(felt);
      felt.focus({ preventScroll: BRED.matches });
    }
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
      observatoer.observe(felt);
      felt.focus({ preventScroll: BRED.matches });
    } else {
      observatoer.unobserve(felt);
      // Gjennomgangen (BH1, ECH5): fokus tilbake uten å bla, så den som har
      // bladd med feltet åpent, blir der, og bare til et «?» som vises.
      if (!aapent() && knappen && knappen.isConnected && knappen.getClientRects().length) {
        knappen.focus({ preventScroll: true });
      }
    }
  }, true);

  document.addEventListener("keydown", (e) => {
    const felt = aapent();
    // Gjennomgangen (BH11, ECH6): ikke når en annen kontroll har brukt Esc.
    if (e.key === "Escape" && felt && !e.defaultPrevented) felt.hidePopover();
  });

  // Valget huskes mens fanen er åpen. Er lagringen slått av, kaster
  // sessionStorage, og feltet flyttes likevel, men bare på denne siden.
  function lagret() {
    try {
      return sessionStorage.getItem(SIDEN);
    } catch {
      return null;
    }
  }

  function side(venstre) {
    rot.classList.toggle("felt-venstre", venstre);
    for (const k of document.querySelectorAll(".hjelpevindu button.flytt")) {
      k.textContent = venstre ? "Flytt til høyre" : "Flytt til venstre";
    }
  }

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".hjelpevindu button.flytt")) return;
    const venstre = !rot.classList.contains("felt-venstre");
    side(venstre);
    try {
      sessionStorage.setItem(SIDEN, venstre ? "venstre" : "hoeyre");
    } catch {
      // Lagringen er slått av.
    }
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
  side(lagret() === "venstre");
  // Gjennomgangen (ECH7): en side fra hurtigbufferen ved «Tilbake» leser
  // valget på nytt.
  window.addEventListener("pageshow", (e) => {
    if (e.persisted) side(lagret() === "venstre");
  });
  rot.classList.add("hjelpefelt");
})();

// Story 8.22 (spørsmål 8): søket i «Følg en aksje» mens man skriver. Alle
// radene står i siden; skriptet skjuler dem som ikke har teksten i tickeren
// eller navnet (hver for seg, som ferdige_lister.filtrer, gjennomgangen BH5),
// og sier hvor mange som vises. Uten skriptet gjør knappen «Vis» det samme på
// serveren. Et klikk på en bransje eller en omsetning sender skjemaet; med
// tastaturet flytter piltastene valget uten å laste siden, og «Vis» sender
// det (gjennomgangen, BH4, ECH2, WCAG 3.2.2). Står her fordi sidene bare har
// ett skript (8.0f), og gjelder bare siden med lista.
(function () {
  const felt = document.querySelector("input[data-folgsok]");
  const lista = document.getElementById("foelgbare");
  if (!felt || !lista) return;
  const rader = Array.from(lista.querySelectorAll("li[data-kode]"));
  const antall = document.getElementById("antall-vist");
  const ingen = document.getElementById("ingen-treff");
  function filtrer() {
    const tekst = felt.value.trim().toLowerCase();
    let vist = 0;
    for (const rad of rader) {
      const med = !tekst || rad.dataset.kode.includes(tekst) || rad.dataset.navn.includes(tekst);
      rad.hidden = !med;
      if (med) vist += 1;
    }
    if (antall) antall.textContent = String(vist);
    if (ingen) ingen.hidden = vist > 0;
  }
  felt.addEventListener("input", filtrer);
  let klikk = false;
  for (const gruppe of felt.form.querySelectorAll("fieldset")) {
    gruppe.addEventListener("pointerdown", () => {
      klikk = true;
    });
    gruppe.addEventListener("keydown", () => {
      klikk = false;
    });
    gruppe.addEventListener("change", () => {
      if (klikk) felt.form.submit();
      klikk = false;
    });
  }
})();
