-- 0015 - hoey og lav i kurs og indeks. Story 2.10, FR-203, AD-5, AD-6, AD-16
-- (gruppens svar 2026-11-19 kl. 13:51).
--
-- Dagens hoeyeste og laveste kurs fra EODHD (high og low). Svarene og
-- oeyeblikksbildene har feltene alt, saa de koster ingen nye kall (AD-6).
-- Radene som finnes, faar NULL, og neste henting fyller dem for hele aaret,
-- fordi serien byttes ut i sin helhet (AD-5). En rad uten dem lagres uten
-- dem, og signalberegningen bruker dem ikke.
--
-- Kolonnene legges til med ADD COLUMN, uten DROP TABLE, som i 0004 og 0014.
-- CHECK-en i en kolonne kan vise til andre kolonner i raden, som i 0004, og
-- sier det samme som Kursrad: over null, og lav ikke over hoey. Typen
-- kontrolleres av Kursrad i porten, fordi en tekst i en REAL-kolonne lagres
-- som tekst (se 0004).

ALTER TABLE kurs ADD COLUMN hoey REAL CHECK (hoey IS NULL OR hoey > 0);

ALTER TABLE kurs ADD COLUMN lav REAL CHECK (lav IS NULL OR (lav > 0 AND (hoey IS NULL OR lav <= hoey)));

-- Hovedindeksen lagres som Kursrad, som aksjene. Uten kolonnene ville
-- SqliteIndekslager gitt en annen serie tilbake enn MinneIndekslager.
ALTER TABLE indeks ADD COLUMN hoey REAL CHECK (hoey IS NULL OR hoey > 0);

ALTER TABLE indeks ADD COLUMN lav REAL CHECK (lav IS NULL OR (lav > 0 AND (hoey IS NULL OR lav <= hoey)));
