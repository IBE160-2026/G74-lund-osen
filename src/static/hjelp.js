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

  // Om steget i hører til siden (gjennomgangen av «Følg en aksje», ECH1):
  // en feilside på samme adresse, som når basen ikke kan åpnes, har et annet
  // navn, og da lukkes omvisningen i stedet for å laste siden på nytt.
  paaSiden(steg, i, side) {
    return Boolean(steg[i]) && steg[i].side === side;
  },

  // Story 8.26 (svaret 11.11 kl. 16:58): «Vis meg rundt» bruker den samme
  // boksen, bare med stegene for siden man står på. De får sidenavnet SIDEN,
  // så et steg uten delen hoppes over som i omvisningen, og ingen går til en
  // annen side.
  SIDEN: "siden",
  sidensSteg(liste) {
    if (!Array.isArray(liste)) return [];
    return liste.map((s) => ({ side: OMVISNING.SIDEN, anker: s.anker, tittel: s.tittel, tekst: s.tekst, ogsaa: s.ogsaa }));
  },

  // Tilbudet første gang: bare på oversikten, og bare før det er besvart.
  skalTilby(side, svar) {
    return side === "oversikt" && svar === null;
  },

  // Story 8.26 (tillegg 21, gruppens svar 12.11 kl. 09:58, «Brukerutfall» i
  // §7 i PRD-en): tilbudet starter «Vis meg rundt» for oversikten, ikke hele
  // omvisningen på 23 steg, så en ny bruker kommer fort til en aksje selv.
  TILBUDET: "Første gang her? «Vis meg rundt» viser deg denne siden, ett steg om gangen.",

  // Linja på det siste steget i «Vis meg rundt» på oversikten, og hvor
  // «Ferdig» går: til det første navnet under «Skilte seg ut», eller til
  // tabellen når ingen aksje står der (en annen dag, en sortering, ingen med
  // 2 av 3). null på de andre sidene og i hele omvisningen, som går videre
  // til aksjesiden selv.
  videre(side, bareSiden, harNavn) {
    if (side !== "oversikt" || !bareSiden) return null;
    if (harNavn) {
      return { linje: "Klikk så et navn under «Skilte seg ut» for å se hvorfor aksjen skilte seg ut.", maal: "ut" };
    }
    return { linje: "Klikk så et navn i tabellen for å se sjekkene for aksjen.", maal: "tabellen" };
  },
};

// Story 8.26 (gruppens svar 11.11 kl. 22:04, tillegg 17): «Følg en aksje»
// filtrerer og sorterer i nettleseren med en gang ved klikk på en brikke, en
// omsetning eller en sortering, som ferdige_lister.filtrer og .sorter gjør på
// serveren. Rene funksjoner, så testene kan kjøre dem med Node.
const FOLGLISTA = {
  // Om raden (dataset fra malen) passer med søket, bransjene og omsetningen.
  passer(rad, tekst, bransjer, omsetning) {
    const t = (tekst || "").trim().toLowerCase();
    if (t && !rad.kode.includes(t) && !rad.navn.includes(t)) return false;
    if (bransjer.length && !bransjer.includes(rad.bransje)) return false;
    if (omsetning && rad.omsetning !== omsetning) return false;
    return true;
  },
  // Sammenligningen for sorteringen: «omsatt» (høyest median først, ikke
  // målt sist), «navn» (A–Å, med Æ, Ø og Å sist) og «bransje» (rangen, så
  // navnet). Likt ordnes etter navnet og så tickeren.
  // Gjennomgangen (ECH1): samme nøkkel som ferdige_lister._norsk, med æ, ø og
  // å sist, ikke localeCompare, som i nb regner «aa» som å.
  norsk(navn) {
    return navn.toLowerCase().replace(/æ/g, "{0").replace(/ø/g, "{1").replace(/å/g, "{2");
  },
  sammenlign(a, b, sortering) {
    const na = FOLGLISTA.norsk(a.navn);
    const nb = FOLGLISTA.norsk(b.navn);
    const navn = (na < nb ? -1 : na > nb ? 1 : 0) || (a.kode < b.kode ? -1 : a.kode > b.kode ? 1 : 0);
    if (sortering === "navn") return navn;
    if (sortering === "bransje") return Number(a.rang) - Number(b.rang) || navn;
    const ma = a.median === "" ? null : Number(a.median);
    const mb = b.median === "" ? null : Number(b.median);
    if ((ma === null) !== (mb === null)) return ma === null ? 1 : -1;
    return (mb || 0) - (ma || 0) || navn;
  },
};

// Story 8.27: avgjørelsene i panelet «Mine notater», uten en side, så
// testene kan kjøre dem med Node (gjennomgangen, VG2 og VG3). Skriptet for
// panelet nederst bruker dem.
const NOTATPANEL = {
  AAPENT: "ose-notatpanel", // localStorage: "ja" når panelet er åpent
  SIDEN: "ose-notatpanel-side", // localStorage: "venstre" eller "hoeyre"
  ANKER: "#notatpanel", // appen sender tilbake hit etter lagring

  // Panelet står bare fra 1056 px, og bare når det er åpent.
  synlig(aapen, bred) {
    return Boolean(aapen) && Boolean(bred);
  },
  // Åpent ved start når det er husket som åpent, eller siden kom fra et
  // skjema i panelet.
  aapentVedStart(lagret, anker) {
    return lagret === "ja" || anker === NOTATPANEL.ANKER;
  },
  // Det som lagres når knappen trykkes: åpent når panelet var skjult.
  etterKnappen(skjult) {
    return skjult ? "ja" : null;
  },
  venstre(lagret) {
    return lagret === "venstre";
  },
  // Det som lagres når «Flytt» trykkes, og teksten på knappen etterpå.
  flytt(venstreNaa) {
    return venstreNaa ? "hoeyre" : "venstre";
  },
  flyttTekst(venstre) {
    return venstre ? "Flytt til høyre" : "Flytt til venstre";
  },
  // Esc lukker panelet bare når fokus er i det, og ingen annen boks er åpen
  // (hjelpen eller omvisningen), og ingen annen kontroll har brukt tasten.
  // Gjennomgangen (ECH4): da lukker ett trykk bare den øverste.
  escLukker(tast, brukt, skjult, fokusIPanelet, annenAapen) {
    return tast === "Escape" && !brukt && !skjult && fokusIPanelet && !annenAapen;
  },
};

if (typeof module === "object" && module.exports) {
  module.exports = OMVISNING;
  module.exports.FOLGLISTA = FOLGLISTA;
  module.exports.NOTATPANEL = NOTATPANEL;
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
  // Story 8.26: stegene boksen går gjennom, og siden de hører til. Hele
  // omvisningen, eller bare siden med «Vis meg rundt».
  let aktive = steg;
  let stedet = SIDE;
  let boksen = null;
  let merket = null;
  // Story 8.19 (spørsmål 8): en del til som merkes med steget, som linja
  // bak «Oppdatert» i den ekte versjonen.
  let ogsaaMerket = null;
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

  // Story 8.26 (tillegg 18): et steg som peker på en kolonneoverskrift,
  // merker overskriften og cellene i kolonnen i de første radene.
  const RADENE_I_KOLONNEN = 3;
  let kolonnen = [];
  function merkKolonnen(th) {
    const tabell = th.closest("table");
    const antall = th.parentElement.cells.length;
    const celler = [th];
    // Gjennomgangen (ECH6): alle tbody-ene, ikke bare den første.
    for (const rad of tabell.querySelectorAll("tbody tr")) {
      if (celler.length > RADENE_I_KOLONNEN) break;
      if (rad.cells.length === antall && rad.cells[th.cellIndex].tagName === "TD") celler.push(rad.cells[th.cellIndex]);
    }
    for (const c of celler) c.classList.add("omvisning-kolonne");
    celler[celler.length - 1].classList.add("omvisning-kolonne-siste");
    return celler;
  }
  function fjernMerket() {
    if (merket) merket.classList.remove("omvisning-merket");
    merket = null;
    if (ogsaaMerket) ogsaaMerket.classList.remove("omvisning-merket");
    ogsaaMerket = null;
    for (const c of kolonnen) c.classList.remove("omvisning-kolonne", "omvisning-kolonne-siste");
    kolonnen = [];
  }

  function avslutt() {
    // «Vis meg rundt» lagrer ingen tilstand, så en omvisning som er i gang
    // på en annen fane eller side, røres ikke.
    if (aktive === steg) skriv(sessionStorage, OMVISNING.STEGET, null);
    aktive = steg;
    stedet = SIDE;
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
    const j = OMVISNING.nesteSteg(aktive, i, retning, stedet, finnes);
    if (j < 0) return avslutt();
    const s = aktive[j];
    if (s.side !== stedet) {
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

  // Story 8.26 (tillegg 21): det første navnet under «Skilte seg ut» i
  // tabellen på oversikten, eller null når delen ikke står der.
  function foersteNavn() {
    const del = document.querySelector("#aksjene tr.del.ut");
    const tbody = del ? del.closest("tbody") : null;
    return tbody ? tbody.querySelector('a[href^="/aksje/"]') : null;
  }

  // «Ferdig» på det siste steget: boksen lukkes, og fokus går til det første
  // navnet under «Skilte seg ut», eller til tabellen.
  function tilNavnene(maal) {
    avslutt();
    const navnet = maal === "ut" ? foersteNavn() : null;
    if (navnet) {
      navnet.closest("tbody").querySelector("tr.del.ut").scrollIntoView({ block: "start" });
      navnet.focus({ preventScroll: true });
      return;
    }
    const tabellen = document.getElementById("aksjene");
    if (!tabellen) return;
    if (!tabellen.hasAttribute("tabindex")) tabellen.tabIndex = -1;
    tabellen.scrollIntoView({ block: "start" });
    tabellen.focus({ preventScroll: true });
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
    const s = aktive[j];
    const del = delen(document.getElementById(s.anker));
    if (aktive === steg) skriv(sessionStorage, OMVISNING.STEGET, OMVISNING.tilstand(j, 1, her()));
    fjernMerket();
    if (del.tagName === "TH") {
      kolonnen = merkKolonnen(del);
    } else {
      merket = del;
      del.classList.add("omvisning-merket");
    }
    const ogsaa = s.ogsaa ? document.getElementById(s.ogsaa) : null;
    if (ogsaa) {
      ogsaaMerket = ogsaa;
      ogsaa.classList.add("omvisning-merket");
    }
    // Gjennomgangen (BH7, ECH7): delen øverst, så boksen nederst dekker
    // mindre av den, også på smal skjerm. Story 8.19 (spørsmål 8): står den
    // andre delen over, som linja bak «Oppdatert», rulles det dit, så begge vises.
    const oeverst = ogsaa && ogsaa.compareDocumentPosition(del) & Node.DOCUMENT_POSITION_FOLLOWING ? ogsaa : del;
    oeverst.scrollIntoView({ block: "start" });
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
    teller.textContent = OMVISNING.teller(j, aktive.length);
    const tittel = document.createElement("h2");
    tittel.id = "omvisning-tittel";
    tittel.textContent = s.tittel;
    const tekst = document.createElement("p");
    tekst.id = "omvisning-tekst";
    tekst.textContent = s.tekst;
    const knappene = document.createElement("div");
    knappene.className = "omvisning-knapper";
    const lov = OMVISNING.knappene(aktive, j, stedet, finnes);
    const tilbake = knapp("Tilbake", "omvisning-tilbake", () => gaaTil(j - 1, -1));
    tilbake.disabled = !lov.tilbake;
    const siste = lov.ferdig;
    // Story 8.26 (tillegg 21): på det siste steget i «Vis meg rundt» på
    // oversikten står én linje til, og «Ferdig» går til navnene.
    const videre = siste ? OMVISNING.videre(SIDE, aktive !== steg, foersteNavn() !== null) : null;
    const ferdig = videre ? () => tilNavnene(videre.maal) : avslutt;
    knappene.append(
      tilbake,
      knapp(siste ? "Ferdig" : "Neste", "omvisning-neste", () => (siste ? ferdig() : gaaTil(j + 1, 1))),
      knapp("Lukk", "omvisning-lukk", avslutt),
    );
    boksen.append(teller, tittel, tekst);
    if (videre) {
      const linja = document.createElement("p");
      linja.className = "omvisning-videre";
      linja.textContent = videre.linje;
      boksen.append(linja);
    }
    boksen.append(knappene);
    // Story 8.26 (svaret kl. 16:58): siste steg med «Vis meg rundt» har
    // «Ferdig» og lenken til hele omvisningen.
    if (siste && aktive !== steg) {
      const hele = document.createElement("p");
      hele.className = "omvisning-hele";
      const lenke = document.createElement("a");
      lenke.href = "#";
      lenke.textContent = "Spill av hele omvisningen";
      lenke.addEventListener("click", (e) => {
        e.preventDefault();
        avslutt();
        start();
      });
      hele.append(lenke);
      boksen.append(hele);
    }
    boksen.focus();
    // Story 8.26 (tillegg 18): boksen står ikke over det som er merket. Dekker
    // den det nederst til høyre, flyttes den til venstre.
    // Dekker den også der, står boksen øverst når det merkede står i nedre
    // halvdel av vinduet.
    boksen.classList.remove("til-venstre", "oeverst");
    const merkede = kolonnen.length ? kolonnen : [del];
    function dekker() {
      const b = boksen.getBoundingClientRect();
      return merkede.some((el) => {
        const r = el.getBoundingClientRect();
        return r.left < b.right && r.right > b.left && r.top < b.bottom && r.bottom > b.top;
      });
    }
    if (dekker()) boksen.classList.add("til-venstre");
    if (dekker()) {
      // Gjennomgangen (ECH7): prøv øverst, og behold det bare hvis det hjelper.
      boksen.classList.remove("til-venstre");
      boksen.classList.add("oeverst");
      if (dekker()) boksen.classList.remove("oeverst");
    }
  }

  function start() {
    // Gjennomgangen av 8.26 (ECH1, BH4): er boksen fra «Vis meg rundt» åpen,
    // lukkes den først, så hele omvisningen spilles og ikke bare siden.
    if (aktive !== steg) avslutt();
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
  // Story 8.26 (tillegg 21): ja starter «Vis meg rundt» for oversikten, ikke
  // hele omvisningen. «Spill av omvisningen» står øverst som før.
  function tilby() {
    const rad = document.createElement("div");
    rad.className = "omvisning-tilbud";
    rad.setAttribute("role", "region");
    rad.setAttribute("aria-label", "Omvisning");
    const tekst = document.createElement("p");
    tekst.textContent = OMVISNING.TILBUDET;
    const ja = knapp("Vis meg rundt", "omvisning-ja", () => {
      rad.remove();
      skriv(localStorage, OMVISNING.SVARET, "ja");
      visSiden(sidensListe);
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
  // Story 8.26: «Vis meg rundt» med stegene for siden, fra knappen.
  function visSiden(liste) {
    if (boksen) avslutt();
    aktive = OMVISNING.sidensSteg(liste);
    stedet = OMVISNING.SIDEN;
    if (aktive.length === 0) {
      aktive = steg;
      stedet = SIDE;
      return;
    }
    gaaTil(0, 1);
  }
  // Stegene for siden, som tilbudet første gang også bruker.
  let sidensListe = null;
  for (const b of document.querySelectorAll("button.vis-meg-rundt[hidden]")) {
    let liste;
    try {
      liste = JSON.parse(b.dataset.steg);
    } catch {
      continue;
    }
    if (sidensListe === null) sidensListe = liste;
    b.hidden = false;
    b.addEventListener("click", () => visSiden(liste));
  }
  function oppstart() {
    const lagret = les(sessionStorage, OMVISNING.STEGET);
    const videre = lagret === null ? null : OMVISNING.fortsett(lagret, her(), steg.length);
    if (videre && OMVISNING.paaSiden(steg, videre.i, SIDE)) {
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
    // Gjennomgangen av 8.26 (ECH2): en side fra hurtigbufferen har ikke
    // lenger boksen fra «Vis meg rundt», så hele omvisningen gjelder igjen.
    aktive = steg;
    stedet = SIDE;
    // Tillegg 21: uten «Vis meg rundt» på siden (ingen aksjer å vise) kommer
    // tilbudet ikke, og det huskes ikke som besvart.
    if (
      sidensListe &&
      OMVISNING.skalTilby(SIDE, les(localStorage, OMVISNING.SVARET)) &&
      !document.querySelector(".omvisning-tilbud")
    ) {
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
// radene står i siden; skriptet skjuler dem som ikke passer (som
// ferdige_lister.filtrer, gjennomgangen BH5) og sier hvor mange som vises.
// Story 8.26 (tillegg 17): også bransjene, omsetningen og sorteringen virker
// med en gang, med klikk og med tastaturet, uten å laste siden, og adressen
// følger valget. «Vis» står bare uten skriptet. Står her fordi sidene bare
// har ett skript (8.0f), og gjelder bare siden med lista.
(function () {
  // Flettingen av 8.22 inn i 8.25: testene laster skriptet i Node, uten side.
  if (typeof document === "undefined") return;
  const felt = document.querySelector("input[data-folgsok]");
  const lista = document.getElementById("foelgbare");
  if (!felt || !lista) return;
  const skjema = felt.form;
  const rader = Array.from(lista.querySelectorAll("tr[data-kode]"));
  const antall = document.getElementById("antall-vist");
  const filtrert = document.getElementById("antall-filtrert");
  const ingen = document.getElementById("ingen-treff");
  const tittel = document.getElementById("alle-tittel");
  const ordnet = document.getElementById("ordnet-etter");
  const alle = skjema.querySelector("a.valgbrikke");
  for (const knapp of skjema.querySelectorAll("button[type=submit]")) knapp.hidden = true;
  function valgte() {
    return Array.from(skjema.querySelectorAll("input[name=bransje]:checked")).map((i) => i.value);
  }
  function verdi(navn) {
    const i = skjema.querySelector(`input[name=${navn}]:checked`);
    return i ? i.value : "";
  }
  function oppdater() {
    const bransjer = valgte();
    const omsetning = verdi("omsetning");
    const sortering = verdi("sorter") || "omsatt";
    rader.sort((a, b) => FOLGLISTA.sammenlign(a.dataset, b.dataset, sortering));
    lista.append(...rader);
    let vist = 0;
    let iFilteret = 0;
    for (const rad of rader) {
      const filter = FOLGLISTA.passer(rad.dataset, "", bransjer, omsetning);
      const med = filter && FOLGLISTA.passer(rad.dataset, felt.value, bransjer, omsetning);
      rad.hidden = !med;
      if (filter) iFilteret += 1;
      if (med) vist += 1;
    }
    if (antall) antall.textContent = String(vist);
    if (filtrert) filtrert.textContent = String(iFilteret);
    if (ingen) ingen.hidden = vist > 0;
    if (ordnet) ordnet.hidden = sortering !== "omsatt";
    if (tittel) {
      const liste = bransjer.length > 1 ? bransjer.slice(0, -1).join(", ") + " og " + bransjer[bransjer.length - 1] : bransjer[0];
      tittel.textContent = "Alle som kan følges" + (liste ? " i " + liste : "");
    }
    if (alle) {
      alle.classList.toggle("valgt", bransjer.length === 0);
      if (bransjer.length === 0) alle.setAttribute("aria-current", "true");
      else alle.removeAttribute("aria-current");
    }
    const ledd = new URLSearchParams(new FormData(skjema));
    try {
      window.history.replaceState(null, "", "/folg?" + ledd.toString() + "#filteret");
    } catch {
      // Uten historikken virker lista likevel.
    }
  }
  felt.addEventListener("input", oppdater);
  skjema.addEventListener("change", oppdater);
  skjema.addEventListener("submit", (e) => {
    e.preventDefault();
    oppdater();
  });
  if (alle) {
    alle.addEventListener("click", (e) => {
      e.preventDefault();
      for (const i of skjema.querySelectorAll("input[name=bransje]:checked")) i.checked = false;
      oppdater();
    });
  }
})();


// Story 8.27 (gruppens svar 11.11 kl. 21:09–21:20): «Mine notater» i et
// panel fra knappen øverst. Fra 1056 px åpner knappen panelet fast i kanten,
// som hjelpefeltet (8.0f), og siden gir plass. Smalere, og uten skriptet, er
// knappen en lenke til notatene i Min liste. Om panelet er åpent, og hvilken
// side det står på, står i localStorage, så det huskes fra side til side og
// fra gang til gang. Avgjørelsene står i NOTATPANEL over.
(function () {
  if (typeof document === "undefined") return;
  const panel = document.getElementById("notatpanel");
  const knapp = document.querySelector("a.notatknapp");
  if (!panel || !knapp) return;
  const P = NOTATPANEL;
  const BRED = window.matchMedia("(min-width: 1056px)");
  const rot = document.documentElement;
  const innhold = panel.querySelector(".notatpanel-innhold");
  const flytt = panel.querySelector("button.panelflytt");
  const mal = document.getElementById("notatpanel-mal");
  let hentet = false;

  // Er lagringen slått av, kaster localStorage, og panelet virker likevel.
  // Gjennomgangen (BH11): valgene står også her, så panelet holder seg
  // når lagringen er slått av og bredden endres.
  const minne = {};
  function les(noekkel) {
    try {
      return localStorage.getItem(noekkel);
    } catch {
      return noekkel in minne ? minne[noekkel] : null;
    }
  }
  function skriv(noekkel, verdi) {
    minne[noekkel] = verdi;
    try {
      if (verdi === null) localStorage.removeItem(noekkel);
      else localStorage.setItem(noekkel, verdi);
    } catch {
      // Lagringen er slått av.
    }
  }

  // Innholdet står i en <template> fra appen, så skriptet henter ingenting.
  // Det settes inn første gang panelet åpnes på siden.
  function hent() {
    if (hentet || !mal) return;
    hentet = true;
    innhold.replaceChildren(mal.content.cloneNode(true));
  }

  // Panelet står bare fra 1056 px. Smalere er knappen en lenke igjen.
  function vis(aapen, fokus) {
    const synlig = P.synlig(aapen, BRED.matches);
    // Gjennomgangen (ECH9): fokus i panelet som skjules, går til knappen.
    const fokusInne = panel.contains(document.activeElement);
    panel.hidden = !synlig;
    rot.classList.toggle("notatpanel-aapent", synlig);
    if (BRED.matches) {
      knapp.setAttribute("aria-controls", panel.id);
      knapp.setAttribute("aria-expanded", synlig ? "true" : "false");
      knapp.setAttribute("role", "button");
    } else {
      knapp.removeAttribute("aria-controls");
      knapp.removeAttribute("aria-expanded");
      knapp.removeAttribute("role");
    }
    if (synlig) {
      hent();
      if (fokus) panel.focus({ preventScroll: true });
    } else if (fokusInne) {
      knapp.focus({ preventScroll: true });
    }
  }

  function side(venstre) {
    rot.classList.toggle("panel-venstre", venstre);
    flytt.textContent = P.flyttTekst(venstre);
  }

  knapp.addEventListener("click", (e) => {
    if (!BRED.matches) return;
    e.preventDefault();
    const verdi = P.etterKnappen(panel.hidden);
    skriv(P.AAPENT, verdi);
    vis(verdi === "ja", verdi === "ja");
  });
  // Mellomrom åpner også, som en knapp, når lenken er en knapp.
  // Gjennomgangen (BH9): ikke på nytt mens tasten holdes inne.
  knapp.addEventListener("keydown", (e) => {
    if (e.key === " " && BRED.matches && !e.repeat) {
      e.preventDefault();
      knapp.click();
    }
  });

  function lukk() {
    skriv(P.AAPENT, null);
    vis(false);
    knapp.focus();
  }
  panel.querySelector("button.panellukk").addEventListener("click", lukk);

  flytt.addEventListener("click", () => {
    const verdi = P.flytt(rot.classList.contains("panel-venstre"));
    side(P.venstre(verdi));
    skriv(P.SIDEN, verdi);
  });

  // Gjennomgangen (BH8): uten popover i nettleseren kaster velgeren.
  function annenAapen() {
    if (document.querySelector(".omvisning")) return true;
    try {
      return Boolean(document.querySelector(".hjelpevindu:popover-open"));
    } catch {
      return false;
    }
  }
  // Gjennomgangen (ECH4): på vei ned, før hjelpen og omvisningen lukker seg
  // på Esc, så ett trykk bare lukker den øverste.
  document.addEventListener(
    "keydown",
    (e) => {
      if (P.escLukker(e.key, e.defaultPrevented, panel.hidden, panel.contains(document.activeElement), annenAapen())) {
        lukk();
      }
    },
    true,
  );

  BRED.addEventListener("change", () => vis(les(P.AAPENT) === "ja", false));

  function start() {
    side(P.venstre(les(P.SIDEN)));
    // Etter lagring sender appen tilbake med #notatpanel, så panelet står
    // åpent også når lagringen er slått av.
    const fraSkjema = location.hash === P.ANKER;
    if (fraSkjema) {
      skriv(P.AAPENT, "ja");
      // Gjennomgangen (BH1): ankeret tas bort, så «Lukk» varer også når
      // siden lastes på nytt.
      history.replaceState(history.state, "", location.pathname + location.search);
    }
    vis(P.aapentVedStart(les(P.AAPENT), fraSkjema ? P.ANKER : ""), fraSkjema);
  }
  start();
  // Gjennomgangen (ECH5): en side fra hurtigbufferen ved «Tilbake» har
  // gamle notater og kanskje en tekst som alt er lagret, så den lastes på
  // nytt når panelet var satt inn.
  window.addEventListener("pageshow", (e) => {
    if (!e.persisted) return;
    if (hentet) location.reload();
    else start();
  });
})();
