-- 0004 - maalingene bak de tre sjekkene. Story 2.1c, FR-408, FR-706, AD-7,
-- AD-16, AD-18.
--
-- Av de tre sjekkene lagret raden bare fortegnene. Tallene de ble avgjort av,
-- ble kastet, og et fortegn uten maaling kan ikke etterproeves (FR-706). Raden er et
-- oeyeblikksbilde av hva regelen saa, saa maalingene kopieres inn som verdier,
-- som kursen (AD-18). De lagres uavrundet og i samme enhet som regelen regner
-- i. Avrunding skjer bare der tallet vises (regel 21).
--
-- Kolonnene legges til med ADD COLUMN og en CHECK i kolonnen, uten
-- DROP TABLE: vurdering er uerstattelig (AD-7). CHECK-en i en kolonne kan
-- vise til andre kolonner i raden. Verdiene ellers (endelige tall, ikke
-- fortegnet mot maalingen) kontrolleres av Vurdering i porten.
--
-- En rad med grunn har ingen maaling. En vurdering har alle fire, bortsett
-- fra at volumforhold mangler naar medianvolumet var 0, og da er interesse 0.
-- Basen sjekker bare om tallene finnes, og fortegnet naar de er tall: en
-- tekst i en REAL-kolonne lagres som tekst og sammenlignes som stoerre enn
-- alle tall, saa typen kontrolleres av Vurdering i porten.

-- En vurderingsrad uten grunn fra foer 0004 har ingen maalinger, og de kan
-- ikke fylles inn etterpaa (AD-7). Migrasjonen stopper derfor, loeperen ruller
-- den tilbake, og basen staar paa versjon 3 med feilen synlig. Nyere SQLite
-- avviser ogsaa ADD COLUMN naar en gammel rad bryter CHECK-en. Hvilken
-- versjon som innfoerte det, er ikke slaatt opp, og hjelpetabellen gjoer det
-- uten betydning. Kontrollen staar her, som kontroll_0003 i 0003.

CREATE TABLE kontroll_0004 (
    vurderinger_uten_grunn INTEGER NOT NULL CHECK (vurderinger_uten_grunn = 0)
);

INSERT INTO kontroll_0004 (vurderinger_uten_grunn)
SELECT count(*) FROM vurdering WHERE grunn IS NULL;

DROP TABLE kontroll_0004;

-- Broek: (justert sluttkurs - MA50) / MA50, samme tall trend sammenligner med
-- noytralsonen. 0,02 er 2 %.
ALTER TABLE vurdering ADD COLUMN trend_avvik REAL
    CHECK ((grunn IS NULL) = (trend_avvik IS NOT NULL));

-- Broek: dagens endring i justert sluttkurs fra forrige boersdag.
ALTER TABLE vurdering ADD COLUMN dagens_endring REAL
    CHECK ((grunn IS NULL) = (dagens_endring IS NOT NULL));

-- Broek: standardavviket til de daglige endringene i vinduet foer dagen.
-- Aldri negativt.
ALTER TABLE vurdering ADD COLUMN standardavvik REAL
    CHECK ((grunn IS NULL) = (standardavvik IS NOT NULL) AND standardavvik >= 0);

-- Forholdstall: dagens volum / medianvolumet de volum_vindu dagene foer. 1,5 er
-- halvannen gang medianen. NULL i en vurdering bare naar medianvolumet var 0,
-- og da er interesse 0. Aldri negativt.
ALTER TABLE vurdering ADD COLUMN volumforhold REAL
    CHECK ((grunn IS NOT NULL AND volumforhold IS NULL
            OR grunn IS NULL AND (volumforhold IS NOT NULL OR interesse = 0))
           AND volumforhold >= 0);
