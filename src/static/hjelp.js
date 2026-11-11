// Story 8.0f: hjelpen ved «?» i ett fast felt som ikke dekker siden
// (avgjort 21.10 kl. 22:47 og 24.10 kl. 11:31 og 11:34). Uten skriptet er
// vinduene popover (auto) midt på skjermen, som i 8.0b. Skriptet setter
// klassen hjelpefelt på <html>, og bare da gjelder stilen for feltet.
// Fra 1056 px står feltet fast i kanten, og stilen gir plass. Smalere står
// det over en tom plass rett under «?», like høy som feltet.
"use strict";

(function () {
  // Story 8.25: testene kjører omvisningen under med Node, uten en side.
  if (typeof HTMLElement === "undefined") return;
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


// Story 8.25 (gruppens svar 10.11 kl. 22:59): «Spill av omvisningen» ved «Vis
// meg rundt». Omvisningen går gjennom sidene i fast rekkefølge, ett steg om
// gangen, med de samme tekstene som «Vis meg rundt» (hjelpetekster.py).
// Stegene står som data i rammen (id-en omvisning), så siden har ett skript.
// Hvor omvisningen er, står i sessionStorage, så den følger med fra side til
// side. At tilbudet første gang er besvart, står i localStorage i nettleseren
// (spørsmål 3 i spec-8-25-spill-av-omvisningen.md), så det trengs ingen
// migrasjon. Uten skriptet står lista fra 8.9 som før.
const OMVISNING = {
  // Sidene i fast rekkefølge, og adressen til hver. Aksjesiden er den første
  // aksjen i tabellen på oversikten, som omvisningen leser der. «Følg en
  // aksje» etter Min liste (svaret 11.11 kl. 14:33, spørsmål 7).
  SIDENE: ["oversikt", "aksje", "boersometer", "min_liste", "folg", "innstillinger"],
  ADRESSE: {
    oversikt: "/",
    boersometer: "/boersometer",
    min_liste: "/min-liste?vis=alle",
    folg: "/folg",
    innstillinger: "/innstillinger",
  },
  STEGET: "ose-omvisning", // sessionStorage: indeksen til steget
  AKSJEN: "ose-omvisning-aksje", // sessionStorage: adressen til aksjesiden
  SVARET: "ose-omvisning-svar", // localStorage: tilbudet første gang er besvart

  // Indeksen til steget man kommer til fra i i retningen (1 eller -1). Et
  // steg på denne siden uten delen det peker på, hoppes over; et steg på en
  // annen side kan ikke sjekkes her, så det gis tilbake. -1 når det ikke er
  // flere steg.
  nesteSteg(steg, i, retning, side, finnes) {
    for (let j = i; j >= 0 && j < steg.length; j += retning) {
      if (steg[j].side !== side || finnes(steg[j].anker)) return j;
    }
    return -1;
  },

  // Adressen til en side, eller null når aksjesiden ikke er kjent.
  adresse(side, aksjen) {
    if (side === "aksje") return aksjen || null;
    return OMVISNING.ADRESSE[side] || null;
  },

  // Adressen omvisningen må starte på, eller null når den kan starte her.
  // Flettingen av 8.23 (gjennomgangen 11.11, ECH1-ECH3): oversikten med
  // ?vis=min eller et filter viser ikke hele tabellen, og med en tom Min liste
  // står ingen aksjer der. Da går omvisningen først til oversikten uten valg,
  // så stegene merker tabellen og aksjesiden er den første aksjen i den.
  startAdresse(side, her) {
    const oversikten = OMVISNING.ADRESSE.oversikt;
    return side === "oversikt" && her !== oversikten ? oversikten : null;
  },

  // «Steg 3 av 18»: nummeret i hele omvisningen.
  teller(i, antall) {
    return `Steg ${i + 1} av ${antall}`;
  },

  // Tilstanden som lagres når omvisningen går til en side: steget, retningen
  // og adressen den selv gikk til (gjennomgangen av 8.25, BH1, BH2, ECH1-ECH3).
  tilstand(i, retning, adresse) {
    return JSON.stringify({ i, retning, adresse });
  },

  // Om omvisningen skal fortsette på siden med adressen her: bare når siden
  // er den omvisningen selv gikk til, så en lenke, nettleserens Tilbake eller
  // en feilside lukker den i stedet for å sende brukeren videre. Gir
  // {i, retning} eller null.
  fortsett(lagret, her, antall) {
    let t;
    try {
      t = JSON.parse(lagret);
    } catch {
      return null;
    }
    if (!t || typeof t !== "object" || t.adresse !== her) return null;
    if (!Number.isInteger(t.i) || t.i < 0 || t.i >= antall) return null;
    return { i: t.i, retning: t.retning === -1 ? -1 : 1 };
  },

  // Om «Tilbake» virker og om «Neste» heter «Ferdig» ved steg j
  // (gjennomgangen, BH3, ECH4): bare når det finnes et steg i den retningen.
  knappene(steg, j, side, finnes) {
    return {
      tilbake: OMVISNING.nesteSteg(steg, j - 1, -1, side, finnes) >= 0,
      ferdig: OMVISNING.nesteSteg(steg, j + 1, 1, side, finnes) < 0,
    };
  },

  // Esc lukker omvisningen, men ikke når et hjelpevindu er åpent: da lukker
  // Esc vinduet først (gjennomgangen, BH9).
  skalLukke(tast, vinduAapent) {
    return tast === "Escape" && !vinduAapent;
  },

  // Tilbudet første gang: bare på oversikten, og bare før det er besvart.
  skalTilby(side, svar) {
    return side === "oversikt" && svar === null;
  },
};

if (typeof module === "object" && module.exports) {
  module.exports = OMVISNING;
}

(function () {
  if (typeof document === "undefined") return;
  const data = document.getElementById("omvisning");
  if (!data) return;
  let steg;
  try {
    steg = JSON.parse(data.dataset.steg);
  } catch {
    return;
  }
  if (!Array.isArray(steg) || steg.length === 0) return;
  const SIDE = data.dataset.side;
  let boksen = null;
  let merket = null;
  let fokusFoer = null;

  function les(lager, noekkel) {
    try {
      return lager.getItem(noekkel);
    } catch {
      return null;
    }
  }
  function skriv(lager, noekkel, verdi) {
    try {
      if (verdi === null) lager.removeItem(noekkel);
      else lager.setItem(noekkel, verdi);
    } catch {
      // Lagringen er slått av: omvisningen virker på denne siden.
    }
  }

  function aksjen() {
    if (SIDE === "oversikt") {
      const lenke = document.querySelector('#aksjene a[href^="/aksje/"]');
      if (lenke) skriv(sessionStorage, OMVISNING.AKSJEN, lenke.getAttribute("href"));
    }
    return les(sessionStorage, OMVISNING.AKSJEN);
  }

  function fjernMerket() {
    if (merket) merket.classList.remove("omvisning-merket");
    merket = null;
  }

  function avslutt() {
    skriv(sessionStorage, OMVISNING.STEGET, null);
    fjernMerket();
    if (boksen) boksen.remove();
    boksen = null;
    document.removeEventListener("keydown", tast);
    // Gjennomgangen (BH8): tilbake dit fokuset var, eller til knappen.
    const tilbake =
      fokusFoer && fokusFoer !== document.body && document.contains(fokusFoer)
        ? fokusFoer
        : document.querySelector("button.spill-av:not([hidden])");
    if (tilbake) tilbake.focus();
  }

  function tast(e) {
    if (boksen && OMVISNING.skalLukke(e.key, document.querySelector(".hjelpevindu:popover-open") !== null)) {
      e.preventDefault();
      avslutt();
    }
  }

  function her() {
    return window.location.pathname + window.location.search;
  }

  function knapp(tekst, klasse, handling) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = klasse;
    b.textContent = tekst;
    b.addEventListener("click", handling);
    return b;
  }

  function gaaTil(i, retning) {
    const j = OMVISNING.nesteSteg(steg, i, retning, SIDE, finnes);
    if (j < 0) return avslutt();
    const s = steg[j];
    if (s.side !== SIDE) {
      const adresse = OMVISNING.adresse(s.side, aksjen());
      if (!adresse) return gaaTil(j + retning, retning);
      skriv(sessionStorage, OMVISNING.STEGET, OMVISNING.tilstand(j, retning, adresse));
      window.location.href = adresse;
      return;
    }
    vis(j);
  }

  function finnes(anker) {
    return document.getElementById(anker) !== null;
  }

  // Noen anker fra 8.9 er et tomt merke rett foran delen, som
  // <span id="noekkeltallene">. Da merkes delen etter merket.
  function delen(anker) {
    // Gjennomgangen (BH10): bare et tomt <span>, ikke et bilde eller et felt.
    if (anker.tagName === "SPAN" && anker.childElementCount === 0 && anker.textContent.trim() === "" && anker.nextElementSibling) {
      return anker.nextElementSibling;
    }
    return anker;
  }

  function vis(j) {
    const s = steg[j];
    const del = delen(document.getElementById(s.anker));
    skriv(sessionStorage, OMVISNING.STEGET, OMVISNING.tilstand(j, 1, her()));
    fjernMerket();
    merket = del;
    del.classList.add("omvisning-merket");
    // Gjennomgangen (BH7, ECH7): delen øverst, så boksen nederst dekker
    // mindre av den, også på smal skjerm.
    del.scrollIntoView({ block: "start" });
    if (!boksen) {
      fokusFoer = document.activeElement;
      boksen = document.createElement("div");
      boksen.className = "omvisning";
      boksen.setAttribute("role", "dialog");
      boksen.setAttribute("aria-modal", "false");
      boksen.setAttribute("aria-labelledby", "omvisning-tittel");
      boksen.setAttribute("aria-describedby", "omvisning-tekst");
      boksen.tabIndex = -1;
      document.body.appendChild(boksen);
      document.addEventListener("keydown", tast);
    }
    boksen.replaceChildren();
    const teller = document.createElement("p");
    teller.className = "omvisning-teller";
    teller.textContent = OMVISNING.teller(j, steg.length);
    const tittel = document.createElement("h2");
    tittel.id = "omvisning-tittel";
    tittel.textContent = s.tittel;
    const tekst = document.createElement("p");
    tekst.id = "omvisning-tekst";
    tekst.textContent = s.tekst;
    const knappene = document.createElement("div");
    knappene.className = "omvisning-knapper";
    const lov = OMVISNING.knappene(steg, j, SIDE, finnes);
    const tilbake = knapp("Tilbake", "omvisning-tilbake", () => gaaTil(j - 1, -1));
    tilbake.disabled = !lov.tilbake;
    const siste = lov.ferdig;
    knappene.append(
      tilbake,
      knapp(siste ? "Ferdig" : "Neste", "omvisning-neste", () => (siste ? avslutt() : gaaTil(j + 1, 1))),
      knapp("Lukk", "omvisning-lukk", avslutt),
    );
    boksen.append(teller, tittel, tekst, knappene);
    boksen.focus();
  }

  function start() {
    skriv(localStorage, OMVISNING.SVARET, "ja");
    // En aksje fra en tidligere omvisning gjelder ikke; den leses på nytt.
    skriv(sessionStorage, OMVISNING.AKSJEN, null);
    const adresse = OMVISNING.startAdresse(SIDE, her());
    if (adresse) {
      skriv(sessionStorage, OMVISNING.STEGET, OMVISNING.tilstand(0, 1, adresse));
      window.location.href = adresse;
      return;
    }
    gaaTil(0, 1);
  }

  // Første gang appen åpnes: tilbudet øverst på oversikten, én gang. Et
  // svar, ja eller nei, huskes i nettleseren.
  function tilby() {
    const rad = document.createElement("div");
    rad.className = "omvisning-tilbud";
    rad.setAttribute("role", "region");
    rad.setAttribute("aria-label", "Omvisning");
    const tekst = document.createElement("p");
    tekst.textContent = "Første gang her? Omvisningen viser sidene i appen, ett steg om gangen.";
    const ja = knapp("Spill av omvisningen", "spill-av", () => {
      rad.remove();
      start();
    });
    const nei = knapp("Nei takk", "omvisning-nei", () => {
      skriv(localStorage, OMVISNING.SVARET, "nei");
      rad.remove();
    });
    rad.append(tekst, ja, nei);
    const main = document.querySelector("main");
    if (main) main.prepend(rad);
  }

  for (const b of document.querySelectorAll("button.spill-av[hidden]")) {
    b.hidden = false;
    b.addEventListener("click", start);
  }
  function oppstart() {
    const lagret = les(sessionStorage, OMVISNING.STEGET);
    const videre = lagret === null ? null : OMVISNING.fortsett(lagret, her(), steg.length);
    if (videre) {
      gaaTil(videre.i, videre.retning);
      return;
    }
    // En annen side enn den omvisningen gikk til: den lukkes stille.
    if (lagret !== null) skriv(sessionStorage, OMVISNING.STEGET, null);
    if (boksen) {
      fjernMerket();
      boksen.remove();
      boksen = null;
      document.removeEventListener("keydown", tast);
    }
    if (OMVISNING.skalTilby(SIDE, les(localStorage, OMVISNING.SVARET)) && !document.querySelector(".omvisning-tilbud")) {
      tilby();
    }
  }

  oppstart();
  // Gjennomgangen (BH5): en side fra hurtigbufferen ved «Tilbake» leser
  // tilstanden på nytt.
  window.addEventListener("pageshow", (e) => {
    if (e.persisted) oppstart();
  });
})();

// Story 8.22 (spørsmål 8): søket i «Følg en aksje» mens man skriver. Alle
// radene står i siden; skriptet skjuler dem som ikke har teksten i tickeren
// eller navnet (hver for seg, som ferdige_lister.filtrer, gjennomgangen BH5),
// og sier hvor mange som vises. Uten skriptet gjør knappen «Vis» det samme på
// serveren. Et klikk på en bransje, en omsetning eller en sortering sender
// skjemaet; med tastaturet krysser mellomrom av en bransje og flytter
// piltastene valget uten å laste siden, og «Vis» sender
// det (gjennomgangen, BH4, ECH2, WCAG 3.2.2). Står her fordi sidene bare har
// ett skript (8.0f), og gjelder bare siden med lista. Tillegg 3: radene er
// rader i en tabell, som på oversikten.
(function () {
  // Flettingen av 8.22 inn i 8.25: testene laster skriptet i Node, uten side.
  if (typeof document === "undefined") return;
  const felt = document.querySelector("input[data-folgsok]");
  const lista = document.getElementById("foelgbare");
  if (!felt || !lista) return;
  const rader = Array.from(lista.querySelectorAll("tr[data-kode]"));
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
