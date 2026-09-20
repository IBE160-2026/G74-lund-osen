# Utkast: vilkårsspørsmål til EODHD

Skrevet 2026-09-20. Sendes til `support@eodhistoricaldata.com`.

**Hvorfor:** lesningen av de fullstendige vilkårene 2026-09-20 ga *uklart* på
spørsmålet om språkmodellbruk — vilkårene verken tillater eller forbyr det. Se
`kilder-og-rettigheter.md`, seksjonen «EODHD: hva de fullstendige vilkårene
sier». Et skriftlig svar er eneste vei fra «uklart» til ja eller nei, og det er
frist 2026-09-27 fordi åpent punkt 1 i PRD-en blokkerer meldingsdelen og
relevanseksperimentet.

**Når svaret kommer:** før det inn i `kilder-og-rettigheter.md` med dato og
sitat, på samme måte som E24-klausulen. Svaret er belegg og skal siteres, ikke
refereres.

**Fyll inn før sending:** navn og institusjon i signaturen. Ikke legg ved
API-nøkkelen.

---

Subject: Terms of use questions — non-commercial student project, free plan

Hello,

We are a student group at a Norwegian university, building a small application
as coursework (course code IBE160). The application is run locally, is not
published or sold, and will be demonstrated once to our teacher and fellow
students. We use the free plan.

We have read the Terms and Conditions at
https://eodhd.com/financial-apis/terms-conditions in full, and four questions
are not answered there. We would be grateful for a written answer we can cite
in our project documentation.

1. **Language models.** May article content retrieved from the news API
   (`/api/news`) be used as input to a large language model, in order to
   classify how relevant an article is to a given company and to generate a
   short explanation in Norwegian? The output would be shown only inside our
   locally run application. We ask because another provider we evaluated
   prohibits this explicitly in their feed terms, and your Terms and Conditions
   do not mention language models in either direction.

2. **"Displaying" in an educational setting.** The Personal Use section states
   that Non-Professional Users are prohibited from "selling, reselling,
   retransmitting, redistributing, displaying, or granting access to the
   Information or Services, whether in its original or repackaged form". Does
   "displaying" cover showing our application, with EODHD price data visible on
   screen, in a single classroom demonstration to a teacher and fellow
   students? We read the clause as being about giving others access to the
   data, but we would rather ask than assume.

3. **Aggregated statistics in a public repository.** Our source code and
   planning documents are in a public GitHub repository, while the downloaded
   datasets themselves are kept local and excluded from version control. The
   repository does contain summary statistics we computed from your data — for
   example the median daily turnover in NOK for a ticker over a three-month
   period, and the share of exchange announcements falling in a given category.
   Does such aggregated, derived statistics count as the Information "in
   repackaged form", or is it outside the scope of the clause?

4. **Free plan access to the news API for Oslo Børs tickers.** Does the free
   plan give access to `/api/news` for Oslo Børs tickers (for example
   `EQNR.OL`), or is news data limited to the six demo tickers? We ask because
   `/api/calendar` returns HTTP 403 with the message "Only EOD data allowed for
   free users", and the documentation states that all data types are available
   without limitation only for the demo tickers. We would like to know before
   spending calls on a test.

Thank you for your help.

Best regards,
‹navn›
‹institusjon›, course IBE160
