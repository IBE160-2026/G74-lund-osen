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

> **Status 2026-09-21. Alle fire spørsmålene er avklart.**
>
> - **Spørsmål 1** sendt 20.09, **besvart 21.09: ja, med fire betingelser.**
>   Ført ordrett i `kilder-og-rettigheter.md`, seksjonen «EODHDs skriftlige
>   svar: ja, med betingelser».
> - **Spørsmål 2 og 3** holdt tilbake til det første var besvart, **sendt
>   21.09 kl. 19:33 og besvart samme kveld: «Yes, we confirm both».** Ført
>   ordrett i «Oppfølgingen samme kveld: begge bekreftet». Bekreftelsen
>   gjelder EODHDs egne data — kategorifordelingene utledet av NewsWeb ligger
>   under Euronexts vilkår og er ikke avklart av dette svaret.
> - **Spørsmål 4** ble ikke sendt. Nyhetstesten 21.09 avgjorde det i stedet:
>   gratisnivået dekker `/api/news` for `.OL`-tickere.
>
> Det som gjenstår av godkjenningen, er ikke et spørsmål til EODHD, men en
> plikt de la på oss: betingelse 4 om at modelltjenesten ikke trener på
> innholdet vi sender inn.

**Fyll inn før sending:** avsenderadressen, i e-postklienten. Den trenger ikke
ligge i repoet. Ikke legg ved API-nøkkelen.

---

Subject: Terms of use questions — non-commercial student project, free plan

Hello,

We are a student group at Molde University College (Høgskolen i Molde), Norway,
building a small application as coursework for the course IBE160. The
application is run locally, is not published or sold, and will be demonstrated
once to our teacher and fellow students. We use the free plan.

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
Joakim Lund and Marian Osen
Group G74, course IBE160
Molde University College, Norway


---

# Utkast: oppfølging i samme tråd

**Skrevet 2026-09-21. SENDT samme dag kl. 19:33 av Marian, og besvart samme
kveld.** Svaret — «Yes, we confirm both», fra Lana A., EOD Support Team — er
ført ordrett i `kilder-og-rettigheter.md`. Teksten under står slik den ble
sendt, fordi det er ordlyden i spørsmålet som avgjør hvor langt svaret rekker.

**Hvorfor nå.** Beslutningen 20.09 var å holde spørsmål 2 og 3 tilbake til
språkmodellspørsmålet var besvart, fordi support erfaringsmessig svarer på det
letteste når flere stilles samtidig. Den betingelsen er innfridd: svaret kom
21.09. Å stille dem nå koster ingenting og svekker ikke det svaret vi allerede
har.

**Begge gjelder ting vi gjør allerede** — demonstrasjonen i undervisning, og
det offentlige repoet. Det er grunnen til at de ikke kan bli liggende.

**Merk** at svaret 21.09 kom fra EOD Support Team, ikke fra en juridisk
avdeling. Det er verdt å ha i bakhodet når svaret på disse to kommer: det er
belegg for hva leverandøren aksepterer, ikke en tolkning av vilkårene som binder
dem.

**Send som svar i samme tråd**, slik at godkjenningen av 21.09 står rett over.
Ikke legg ved API-nøkkelen.

---

Subject: Re: Terms of use questions — non-commercial student project, free plan

Hello Alejandro,

Thank you for the clear answer on the language model question. We have recorded
it in our project documentation, and we will make sure the LLM service we choose
does not use submitted content for training.

When we first wrote, we deliberately asked only that one question. Two others
from the same list are still open, and both concern things we are already doing,
so we would rather ask than assume. Neither requires any API calls to answer.

1. **"Displaying" in an educational setting.** The Personal Use section states
   that Non-Professional Users are prohibited from "selling, reselling,
   retransmitting, redistributing, displaying, or granting access to the
   Information or Services, whether in its original or repackaged form". Does
   "displaying" cover showing our application, with EODHD price data visible on
   screen, in a single classroom demonstration to a teacher and fellow
   students? We read the clause as being about giving others access to the
   data, but we would rather ask than assume.

2. **Aggregated statistics in a public repository.** Our source code and
   planning documents are in a public GitHub repository, while the downloaded
   datasets themselves are kept local and excluded from version control. The
   repository does contain summary statistics we computed from your data — for
   example the median daily turnover in NOK for a ticker over a three-month
   period, and the share of exchange announcements falling in a given category.
   Does such aggregated, derived statistics count as the Information "in
   repackaged form", or is it outside the scope of the clause?

To be concrete about the second question: what is published is a table of
fifteen tickers with one median turnover figure each, computed over 65 trading
days, plus percentage shares per announcement category. The underlying price
series and announcements are not published and are excluded from version
control. If that distinction is not one your terms recognise, we would like to
know now rather than later.

Thank you again for your help.

Best regards,
Joakim Lund and Marian Osen
Group G74, course IBE160
Molde University College, Norway
