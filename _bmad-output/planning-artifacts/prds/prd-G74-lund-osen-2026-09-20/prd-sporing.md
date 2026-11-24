---
title: "Sporingen av PRD-en"
status: aktiv
created: 2026-11-17
updated: 2026-11-24T21:58
---

# Sporingen av PRD-en

For hver ID i [`prd.md`](prd.md), brukerreisene (UJ), kravene (FR og NFR) og
suksessmålene (SM): avsnittet den står i, statusen, storyene og testfilene.
Lista over antakelsene og de foreløpige tallene står til slutt. Fila hører til
PRD-en og endres i samme commit som en ID i `prd.md`.
`tests/test_prd_sporing_9_20.py` feiler hvis en ID mangler her eller ikke finnes
i `prd.md`, hvis avsnittet ikke er der overskriften står i `prd.md`, hvis
statusen ikke følger tabellen i §2 etter regelen i «Slik leses kolonnene», hvis
en story ikke finnes i `epics.md` eller en testfil ikke finnes, hvis «Hvorfor
noen numre mangler» ikke stemmer med `prd.md`, hvis lista over antakelsene ikke
stemmer med markørene i `prd.md`, eller hvis en lenke her ikke virker.

## Slik leses kolonnene

- **Status** er lest i tabellen «Kjerne, ekstra og senere» i §2 i `prd.md`.
  «Bygget» er at minst én rad for kravet har «ja» og ingen er «senere», og
  «bygget, en del senere» at minst én rad har «ja» og én er «senere».
  «Senere» er at hver rad er «senere», og «senere (plan A)» gjelder FR-606, som
  står i §4.6. «Utenfor v1 (plan A)» er at kravet står i vedlegg A. «Tatt bort»
  er at ingen rad har «ja» og ikke alle er «senere», som FR-108.
  NFR-ene gjelder hele appen. Brukerreisene er «bygget», fordi de beskriver det
  appen gjør, og suksessmålene «måles», med statusen i endringsloggen.
- **Storyene** er dem som har ID-en under «Oppfyller» i
  [`epics.md`](../../epics.md), også stories i epicene for plan A, som ikke er
  bygget. «Levert før nedbrytingen» er de tolv kravene som var bygget før
  stories ble skrevet («FR Coverage Map» i `epics.md`). Kravene som er
  kommet til etter 12.11, og UJ og SM, har storyene der de ble bygget eller
  skrevet. Hvert nummer finnes som «### Story X.Y» i `epics.md`.
- **Testene** er filene i `tests/` som nevner ID-en, og filene som tester
  oppførselen kravet beskriver, der de er funnet.
  `tests/test_prd_9_11.py` og `tests/test_prd_sporing_9_20.py` er ikke tatt
  med, fordi de sjekker teksten i PRD-en, ikke appen. «Ingen» betyr at ingen
  test er funnet. Suksessmålene som en person måler, har ingen test.

## Tabellen

| ID | Avsnitt | Status | Storyene | Testene |
|---|---|---|---|---|
| UJ-1 | §1 | bygget | 9.11 | ingen egen; kravene reisen hviler på, har sine |
| UJ-2 | §1 | bygget | 9.16 | ingen egen; kravene reisen hviler på, har sine |
| UJ-3 | §1 | bygget | 9.16 | `tests/test_ki_visning.py` |
| FR-101 | §4.1 | bygget, en del senere | levert før nedbrytingen; 1.4a, 1.4c, 2.2b, 2.9, 2.9b, 8.0, 8.0c, 8.0e, 8.5, 8.6, 8.15, 8.17 | `tests/test_app.py`, `tests/test_hjelpetekster.py`, `tests/test_hovedindeks.py`, `tests/test_markedsoversikt.py`, `tests/test_min_liste.py`, `tests/test_notater.py`, `tests/test_oversiktsleser.py`, `tests/test_vis_meg_rundt_8_26.py` |
| FR-102 | §4.1 | bygget | levert før nedbrytingen; 8.5, 8.11, 8.15, 8.17 | `tests/test_ferdige_lister.py`, `tests/test_markedsoversikt.py`, `tests/test_min_liste.py` |
| FR-103 | §4.1 | bygget | levert før nedbrytingen; 8.0c, 8.12, 8.15 | `tests/test_app.py`, `tests/test_hjelpetekster.py`, `tests/test_markedsoversikt.py`, `tests/test_utseende.py` |
| FR-104 | §4.1 | bygget | 2.9, 2.9b, 2.9c, 8.4 | `tests/test_app.py`, `tests/test_hovedindeks.py`, `tests/test_periodevalget_oversikten.py` |
| FR-105 | §4.1 | bygget | 2.9b, 8.6 | `tests/test_app.py`, `tests/test_hovedindeks.py`, `tests/test_periodevalget_oversikten.py` |
| FR-106 | §4.1 | bygget | 8.6, 8.17 | `tests/test_boersometer.py` |
| FR-107 | §4.1 | senere | 8.12 | ingen |
| FR-108 | §4.1 | tatt bort | 8.11 | `tests/test_ferdige_lister.py`, `tests/test_ferdige_lister_8_11b.py`, `tests/test_raadordene_9_12.py`, `tests/test_vis_meg_rundt_8_26.py` |
| FR-109 | §4.1 | bygget, en del senere | 8.9, 8.13, 8.25, 8.26 | `tests/test_hjelpetekster.py`, `tests/test_omvisningen_8_25.py`, `tests/test_vis_meg_rundt_8_9.py` |
| FR-110 | §4.1 | bygget | 8.10, 8.10b | `tests/test_innstillinger.py`, `tests/test_innstillinger_ki.py` |
| FR-111 | §4.1 | bygget | 8.3 | `tests/test_min_liste.py` |
| FR-112 | §4.1 | bygget | 2.12, 8.22, 8.26, 8.29 | `tests/test_din_egen_liste_8_22.py`, `tests/test_kom_i_gang_8_29.py` |
| FR-201 | §4.2 | bygget | levert før nedbrytingen; 2.9c, 8.0c, 8.2c, 8.5, 8.7, 8.14, 8.16, 8.18 | `tests/test_app.py`, `tests/test_demo.py`, `tests/test_perioder.py` |
| FR-202 | §4.2 | bygget | levert før nedbrytingen; 8.7, 8.16 | `tests/test_demo.py`, `tests/test_sjekk_2_og_3_i_grafen_8_7.py` |
| FR-203 | §4.2 | bygget, en del senere | 2.10, 5.2, 6.5, 7.2, 8.4, 8.5 | `tests/test_historikken.py`, `tests/test_investorsiden.py` |
| FR-204 | §4.2 | bygget | levert før nedbrytingen | `tests/test_aksjedetalj.py`, `tests/test_app.py`, `tests/test_boersometer.py`, `tests/test_docker.py` |
| FR-205 | §4.2 | senere | 8.4 | ingen |
| FR-206 | §4.2 | bygget | 8.8 | `tests/test_signaldager.py` |
| FR-207 | §4.2 | senere | 8.18 | ingen |
| FR-208 | §4.2 | bygget | 8.21, 8.24, 8.27 | `tests/test_notater.py`, `tests/test_notatpanel_8_27.py` |
| FR-209 | §4.2 | bygget, en del senere | 8.21, 8.24 | `tests/test_notater.py` |
| FR-301 | vedlegg A, 4.3 | utenfor v1 (plan A) | 7.1 | ingen |
| FR-302 | vedlegg A, 4.3 | utenfor v1 (plan A) | 7.2 | ingen |
| FR-303 | vedlegg A, 4.3 | utenfor v1 (plan A) | 7.3 | ingen |
| FR-401 | §4.4 | bygget | 2.2, 2.3d, 3.3, 9.15 | `tests/test_app.py`, `tests/test_fetch_prices.py`, `tests/test_kveldshenting.py` |
| FR-402 | §4.4 | bygget | 2.1, 2.3, 2.3b, 2.3d | `tests/test_fetch_prices.py` |
| FR-403 | §4.4 | bygget | 2.4 | `tests/test_etterfyllingen_2_4.py` |
| FR-404 | vedlegg A | utenfor v1 (plan A) | 6.1, 6.2 | ingen |
| FR-405 | vedlegg A | utenfor v1 (plan A) | 6.2 | ingen |
| FR-406 | §4.4 | bygget | 1.1, 1.2, 1.3, 1.4a, 1.4b, 2.1b | `tests/test_app.py`, `tests/test_demo.py`, `tests/test_snapshotleser.py` |
| FR-407 | §4.4 | bygget | 2.6, 8.5, 8.14, 8.18 | `tests/test_justeringsdager_2_6_8_14.py` |
| FR-408 | §4.4 | bygget, en del senere | 1.1, 1.5b, 1.6, 1.9, 2.1, 2.1c, 2.2b, 2.5, 2.7, 2.17, 8.4, 8.8, 8.12, 9.15 | `tests/test_app.py`, `tests/test_oversiktsleser.py`, `tests/test_signaldager.py`, `tests/test_vurderingslager.py` |
| FR-409 | §4.4 | bygget | 1.7, 2.2b, 2.7, 2.11, 2.17, 8.8, 8.12, 8.17 | `tests/test_app.py`, `tests/test_lista.py`, `tests/test_markedsoversikt.py`, `tests/test_oversiktsleser.py`, `tests/test_signaldager.py`, `tests/test_tilstand.py`, `tests/test_vurderingslager.py` |
| FR-410 | §4.4 | bygget | 2.8 | `tests/test_fetch_prices.py`, `tests/test_indeks.py` |
| FR-411 | §4.4 | bygget | 3.4, 3.4b, 3.4h, 8.18, 9.17 | `tests/test_app.py`, `tests/test_demo.py`, `tests/test_demo_ki.py`, `tests/test_indeks.py`, `tests/test_ki_visning.py`, `tests/test_utseende.py` |
| FR-412 | §4.4 | bygget | 2.11, 2.12, 2.21, 2.22, 8.6, 8.11, 8.11c, 8.28, 9.27, 9.28 | `tests/test_de_15_mest_omsatte_8_28.py`, `tests/test_ferdige_lister.py`, `tests/test_ferdige_lister_8_11b.py`, `tests/test_ki_grunnlag.py`, `tests/test_kode_4_2_22.py`, `tests/test_lista.py`, `tests/test_statusene_9_27.py`, `tests/test_tatt_inn_9_28.py`, `tests/test_ut_og_inn_2_21.py`, `tests/test_valg.py` |
| FR-413 | §4.4 | bygget | 2.13 | `tests/test_ferdige_lister_8_11b.py`, `tests/test_omsetning.py` |
| FR-414 | §4.4 | senere | 2.14 | ingen |
| FR-415 | §4.4 | bygget | 2.12, 8.22, 8.26 | `tests/test_bransjene_8_22.py`, `tests/test_foelg_en_aksje_8_22.py`, `tests/test_valg.py`, `tests/test_vis_meg_rundt_8_26.py` |
| FR-416 | §4.4 | senere | 2.20 | ingen |
| FR-501 | vedlegg A, 4.5 | utenfor v1 (plan A) | 6.3 | `tests/test_meldinger.py` |
| FR-502 | vedlegg A, 4.5 | utenfor v1 (plan A) | 6.4 | `tests/test_meldinger.py` |
| FR-503 | vedlegg A, 4.5 | utenfor v1 (plan A) | 6.5 | `tests/test_meldinger.py` |
| FR-601 | §4.6 | bygget | 2.18, 5.1, 8.10, 8.10b, 10.3, 10.6, 10.10 | `tests/test_demo_ki.py`, `tests/test_demoproeven.py`, `tests/test_ettertid_2_17.py`, `tests/test_innstillinger_ki.py`, `tests/test_ki_dagen.py`, `tests/test_ki_visning.py` |
| FR-602 | §4.6 | bygget | 2.18, 3.4b, 5.2, 10.3, 10.6, 10.10 | `tests/test_demo_ki.py`, `tests/test_ki_visning.py`, `tests/test_rikere_ki_tekster.py` |
| FR-602A | vedlegg A, 4.6A | utenfor v1 (plan A) | ingen | ingen |
| FR-603 | §4.6 | bygget | 3.4b, 5.3, 10.2, 10.6, 10.7, 10.10, 10.11 | `tests/test_demo_ki.py`, `tests/test_ki_dagen.py`, `tests/test_ki_modell.py`, `tests/test_ki_tekst.py`, `tests/test_raadordene_9_12.py`, `tests/test_rikere_ki_tekster.py`, `tests/test_rikere_ki_tekster_tillegg.py` |
| FR-603A | vedlegg A, 4.6A | utenfor v1 (plan A) | ingen | ingen |
| FR-604 | §4.6 | bygget | 4.2, 4.3, 10.6 | `tests/test_demo.py`, `tests/test_demo_ki.py`, `tests/test_ki_dagen.py`, `tests/test_ki_lokal.py`, `tests/test_ki_modell.py`, `tests/test_ki_tekst.py`, `tests/test_ki_tjenestene.py`, `tests/test_ki_visning.py`, `tests/test_kilogg.py`, `tests/test_kilogg_sqlite.py`, `tests/test_rikere_ki_tekster.py`, `tests/test_rikere_ki_tekster_tillegg.py` |
| FR-604A | vedlegg A, 4.6A | utenfor v1 (plan A) | ingen | ingen |
| FR-605 | §4.6 | bygget | 4.2, 10.6, 10.10, 10.11 | `tests/test_demo_ki.py`, `tests/test_docker.py`, `tests/test_ki_dagen.py`, `tests/test_ki_lokal.py`, `tests/test_ki_modell.py`, `tests/test_ki_teksten_forklarer.py`, `tests/test_ki_tjenestene.py`, `tests/test_kilogg.py`, `tests/test_mest_av_bransjene.py`, `tests/test_rikere_ki_tekster.py` |
| FR-606 | §4.6 | senere (plan A) | 5.4 | ingen |
| FR-606A | vedlegg A, 4.6A | utenfor v1 (plan A) | ingen | ingen |
| FR-607 | §4.6 | bygget | 2.18, 10.6, 10.10, 10.11 | `tests/test_ki_dagen.py`, `tests/test_rikere_ki_tekster.py`, `tests/test_rikere_ki_tekster_tillegg.py` |
| FR-608 | §4.6 | bygget, en del senere | 9.6, 10.7, 10.8 | `tests/test_ki_tekst.py`, `tests/test_ki_tjenestene.py` |
| FR-701 | §4.7 | bygget | levert før nedbrytingen; 8.9 | `tests/test_signalberegning.py` |
| FR-702 | §4.7 | bygget | levert før nedbrytingen | `tests/test_signalberegning.py` |
| FR-703 | §4.7 | bygget | levert før nedbrytingen; 8.9, 8.11, 8.11c | `tests/test_docker.py`, `tests/test_hjelpetekster.py` |
| FR-704 | §4.7 | bygget | levert før nedbrytingen; 8.0c, 8.9 | `tests/test_hjelpetekster.py` |
| FR-705 | §4.7 | bygget | levert før nedbrytingen; 8.0, 8.0c | `tests/test_app.py`, `tests/test_markedsoversikt.py`, `tests/test_signalberegning.py` |
| FR-706 | §4.7 | bygget | levert før nedbrytingen; 8.0, 8.0c, 8.1, 8.7 | `tests/test_aksjedetalj.py`, `tests/test_app.py`, `tests/test_signalberegning.py` |
| NFR-01 | §5 | gjelder hele appen | 2.3, 2.3b, 2.3d, 2.4, 2.8, 2.10, 2.11, 2.12, 2.13, 4.0 | `tests/test_etterfyllingen_2_4.py`, `tests/test_fetch_prices.py`, `tests/test_ingen_nettverk.py`, `tests/test_omsetning.py` |
| NFR-02 | §5 | gjelder hele appen | 10.6 | `tests/test_ki_dagen.py`, `tests/test_ki_tekst.py` |
| NFR-03 | §5 | gjelder hele appen | 2.0, 2.9, 2.9c, 7.3 | `tests/test_app.py`, `tests/test_boersometer.py`, `tests/test_demoproeven.py`, `tests/test_fetch_prices.py`, `tests/test_markedsoversikt.py` |
| NFR-04 | §5 | gjelder hele appen | 2.3d, 5.1, 5.2, 5.3, 10.3 | `tests/test_demo_ki.py`, `tests/test_ki_dagen.py`, `tests/test_ki_modell.py`, `tests/test_ki_tekst.py`, `tests/test_ki_visning.py`, `tests/test_kilogg.py`, `tests/test_kveldshenting.py` |
| NFR-05 | §5 | gjelder hele appen | 2.9b, 5.2, 6.3, 6.5, 7.2, 8.0, 8.0c, 8.2c, 8.9, 8.13, 8.15, 8.19, 10.3 | `tests/test_app.py`, `tests/test_signalberegning.py` |
| NFR-06 | §5 | gjelder hele appen | 2.9, 2.9b, 2.9c, 2.12, 3.4h, 5.3, 8.0, 8.0c, 8.4, 8.8, 8.9, 8.11c, 8.13, 8.18, 8.21, 8.23, 8.24, 8.25, 8.26, 8.27, 8.28, 8.29, 8.30, 9.10, 9.11, 9.12, 9.18, 10.3, 10.6, 10.10, 10.11 | `tests/test_app.py`, `tests/test_boersometer.py`, `tests/test_demoproeven.py`, `tests/test_docker.py`, `tests/test_foelg_en_aksje_8_22.py`, `tests/test_hjelpetekster.py`, `tests/test_investorsidene_demo.py`, `tests/test_justeringsdager_2_6_8_14.py`, `tests/test_ki_dagen.py`, `tests/test_ki_modell.py`, `tests/test_ki_visning.py`, `tests/test_neste_henting.py`, `tests/test_notater.py`, `tests/test_notatpanel_8_27.py`, `tests/test_omvisningen_8_25.py`, `tests/test_raadordene_9_12.py`, `tests/test_rikere_ki_tekster.py`, `tests/test_rikere_ki_tekster_tillegg.py`, `tests/test_signaldager.py`, `tests/test_valg.py`, `tests/test_vis_meg_rundt_8_26.py` |
| NFR-07 | §5 | gjelder hele appen | 1.5, 2.0, 2.8, 3.2 | `tests/test_snapshotleser.py` |
| NFR-08 | §5 | gjelder hele appen | 2.9, 2.10, 2.14, 3.4, 8.5, 8.16, 8.18, 8.21 | `tests/test_aksjedetalj.py`, `tests/test_demo.py`, `tests/test_fetch_prices.py`, `tests/test_neste_henting.py`, `tests/test_notater.py`, `tests/test_perioder.py`, `tests/test_signalberegning.py`, `tests/test_sjekk_2_og_3_i_grafen_8_7.py` |
| SM-1 | §7 | måles | 9.11 | ingen; måles av mennesker |
| SM-2 | §7 | måles | 9.11 | ingen; måles av mennesker |
| SM-3 | §7 | måles | 9.11 | `tests/test_fetch_prices.py` |
| SM-4 | §7 | måles | 9.11 | `tests/test_signalberegning.py` |
| SM-5 | §7 | måles | 9.11 | ingen; måles av mennesker |
| SM-6 | §7 | måles | 9.11 | ingen; måles av mennesker |
| SM-7 | §7 | måles | 9.11 | `tests/test_signalberegning.py` |
| SM-8 | §7 | måles | 9.11 | `tests/test_ki_modell.py`, `tests/test_ki_teksten_forklarer.py`, `tests/test_kilogg.py` |
| SM-9 | §7 | måles | 9.11 | ingen; måles av mennesker |
| SM-10 | §7 | måles | 9.16 | ingen; måles av mennesker |
| SM-11 | §7 | måles | 9.16 | ingen; måles av mennesker |

## Hvorfor noen numre mangler

- **4.3 og 4.5 står bare i vedlegg A.** 4.3 er de kommende hendelsene
  (FR-301–FR-303) og 4.5 meldingsfilteret (FR-501–FR-503). Begge er plan A, så
  §4 har ingen 4.3 eller 4.5.
- **FR-404 og FR-405** er børsmeldingene i plan A og står i vedlegg A, så
  §4.4 hopper fra FR-403 til FR-406.
- **FR-602A, FR-603A, FR-604A og FR-606A** er A-variantene for KI over
  meldingene, i vedlegg A. Det finnes ingen FR-601A, FR-605A, FR-607A eller
  FR-608A: FR-601 og FR-605 gjelder begge planene, som §4.6A i vedlegg A sier,
  og FR-607 og FR-608 kom til etter plan B.
- **FR-407** står i §4.4 med de andre FR-4xx, ikke i §4.1.
- Ellers går numrene uten hull i hvert avsnitt: FR-101–FR-112, FR-201–FR-209,
  FR-401–FR-416, FR-601–FR-608 og FR-701–FR-706, NFR-01–NFR-08, UJ-1–UJ-3 og
  SM-1–SM-11. Et nummer brukes aldri om igjen.

## Antakelser og foreløpige tall

Hver markør `[ANTAKELSE]` og `[FORELØPIG]` i `prd.md` har en rad her, og
markøren lenker tilbake til raden. Alle står i vedlegg A, i plan A, som ikke er
bygget.

| # | Markør | Hvor | Hva | Hvordan den avklares |
|---|---|---|---|---|
| <a name="a1"></a>A1 | `[ANTAKELSE]` | [FR-302](prd.md#fr-302--hvilke-hendelser-og-hvor-langt-fram) | At aksjesiden viser kommende hendelser, og hvilke typer, er antatt | Når kalenderens innhold for aksjene i lista er undersøkt (punkt 12 i §8) |
| <a name="a2"></a>A2 | `[FORELØPIG]` | [FR-302](prd.md#fr-302--hvilke-hendelser-og-hvor-langt-fram) | Horisonten på 90 dager | Som A1 (punkt 12 i §8) |
| <a name="a3"></a>A3 | `[FORELØPIG]` | [FR-606A](prd.md#fr-606a--relevansskalaen) | Grensen mellom «kan påvirke» og «lite relevant» | Kan ikke avgjøres på papir (punkt 2 i §8) |
