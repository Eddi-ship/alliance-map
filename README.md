# Alliance Map (daglig oppdatering)

Kartet henter `map.sql` fra verdenen din hver natt, regner ut hvilken allianse som leder i hver region, og oppdaterer seg selv.

## Filene
- `index.html` er selve kartsiden. Den leser `data.json`.
- `data.json` er dagens tall. Den lages av `update.py`, så du skal ikke redigere den.
- `update.py` laster ned `map.sql` og regner ut kontroll per region.
- `colors.json` husker fargen til hver allianse, slik at fargene ikke skifter fra dag til dag.
- `locked.json` er listen over regioner som er låst i spillet. Den kan ikke leses ut av `map.sql`, så du holder den oppdatert selv.
- `.github/workflows/daily.yml` er det som starter oppdateringen hver natt.

## Sette opp (gratis, ca. 10 minutter)
1. Lag en gratis konto på github.com og logg inn.
2. Trykk **New repository**. Gi det et navn, for eksempel `alliance-map`, velg **Public** og trykk **Create repository**.
3. Trykk **uploading an existing file** og dra inn `index.html`, `data.json`, `colors.json`, `locked.json`, `update.py` og `README.md`. Trykk **Commit changes**.
4. Lag den siste filen for hånd, siden mappen `.github` ofte hoppes over ved opplasting: trykk **Add file → Create new file**, skriv `.github/workflows/daily.yml` som filnavn (skråstrekene lager mappene), lim inn innholdet fra `daily.yml` i denne mappen, og trykk **Commit changes**.
5. Gå til **Settings → Pages**. Under **Build and deployment** velger du **Deploy from a branch**, grenen `main` og mappen `/ (root)`, og trykker **Save**.
6. Gå til fanen **Actions**, velg **Daily update** og trykk **Run workflow** for å teste. Etter et minutt skal den bli grønn.
7. Kartet ligger nå på `https://BRUKERNAVN.github.io/alliance-map/`. Det kan ta et par minutter første gang. Denne lenken limer du inn på Discord.

Fra nå av kjører oppdateringen av seg selv hver dag kl. 03:30 UTC. Du kan også starte den for hånd fra Actions-fanen.

## Hvis noe ikke virker
- **Actions blir rød:** Åpne kjøringen og se på feilmeldingen. Hvis Travian blokkerer nedlastingen fra GitHub, beholder siden bare gårsdagens tall. Send meg feilmeldingen, så ser vi på det.
- **Kan ikke lagre endringer fra Actions:** Gå til **Settings → Actions → General → Workflow permissions** og velg **Read and write permissions**.
- **En region er ikke lenger låst:** Åpne `locked.json` på GitHub, trykk på blyanten, slett navnet og lagre. Neste kjøring bruker det.
- **Ny verden:** Endre `WORLD` øverst i `update.py`.

## Om tallene
Kontrollprosenten er et anslag: ledende alliansens andel av befolkningen til alle spillere i en allianse i regionen. Spillets egne tall kan avvike noen få poeng.
