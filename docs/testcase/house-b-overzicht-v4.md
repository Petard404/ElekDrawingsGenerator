# Elektrische installatie — Woning B

**Ontwerpoverzicht v4** · 11 oktober 2026
Bron: `Woning B - elektrische installatie V3.xlsx`, blad *Beschrijving ruimtes*
Norm: AREI (België) · Aansluiting: 3N400V + N

> Bedoeld als invoer voor een softwarepakket. Alle entiteiten hebben een stabiele sleutel (`id`).
> Ruimtenamen zijn letterlijk overgenomen uit het bronbestand.

---

## 1. Samenvatting

| Grootheid | Aantal |
|---|---|
| Kringen hoofdbord | 22 |
| Kringen onderverdeelbord tuinhuis | 3 |
| Contactdozen hoofdbord | 74 |
| Contactdozen tuinhuis | 4 |
| Lichtpunten | 72 |
| Rolluikmotoren | 4 |
| Bedieningen (drukknoppen, sensoren, sturingen) | 85 |
| Benodigde stuuringangen | 94 |
| Differentiëlen 30 mA — hoofdbord | 4 (+1 te reserveren voor `G`) |
| Differentiëlen 30 mA — tuinhuis | 1 |

**Ontwerpregels**

| Regel | Waarde |
|---|---|
| Sectie stopcontactkringen | 2,5 mm² |
| Automaat stopcontactkringen | 20 A |
| Max. contactdozen per kring | 8 (AREI) |
| Max. kringen per differentieel | 7 (eigen keuze; AREI laat 8 toe) |
| Telregel meervoudige sokkel | 2, 3 of 4 mechanismen onder één afdekplaat = 1 contactdoos |
| Telregel lichtpunt | Lichtpunt op een stopcontactkring telt mee als contactdoos |
| Kringaanduiding | Letters A–Y; **H, I en Z niet in gebruik** |
| Bestaande kringen | 1 t.e.m. 35 = verlichting en sturing (bronbestand, ongewijzigd) |

---

## 2. Borden

| id | Bord | Voeding | Differentieel |
|---|---|---|---|
| `BRD-MAIN` | Hoofdbord | Netaansluiting 3N400V + N | Algemeen 300 mA (of 100 mA) type A, 4-polig |
| `BRD-TUIN` | Onderverdeelbord tuinhuis | Kring `J` vanuit `BRD-MAIN`, XVB 5G6 mm² in wachtbuis | 30 mA type A, 40 A |

**Selectiviteit.** Kring `J` staat bewust **niet** achter een 30 mA in het hoofdbord. Twee 30 mA's in
serie geven geen selectiviteit — bij een lek in het tuinhuis zou ook het hoofdbord uitvallen. Wil je
toch beide, kies bovenstrooms dan een selectieve differentieel (type S, vertraagd).

---

## 3. Kringen — hoofdbord

### 3.1 Kringen met een eigen aansluiting

| id | Diff | Ruimte | Belasting | Dozen | Automaat | Sectie | Grondslag |
|---|---|---|---|---|---|---|---|
| `A` | — (enkel 300 mA) | Keuken | Kookplaat 3N400V — **vaste aansluitdoos** | 0 | 3P+N 20 A curve C | 5G2,5 mm² (4 mm² bij 11 kW) | AREI: fornuis verplicht apart |
| `B` | `D1` | Keuken | Oven | 1 | 20 A | 3G2,5 mm² | AREI: verplicht apart |
| `C` | `D1` | Keuken | Vaatwas (eiland) | 1 | 20 A | 3G2,5 mm² | AREI: verplicht apart + 30 mA |
| `D` | `D2` | Berging | Wasmachine | 1 | 20 A | 3G2,5 mm² | AREI: verplicht apart + 30 mA |
| `E` | `D2` | Berging | Droogkast | 1 | 20 A | 3G2,5 mm² | AREI: verplicht apart + 30 mA |
| `F` | `D2` | Berging | C.V. (verwarmingsketel) | 1 | 20 A | 3G2,5 mm² | AREI: verplicht apart |
| `G` | ⚠ zie §4.1 | Carport | Laadpunt elektrische wagen | 1 | 3P+N 20 A (11 kW) / 32 A (22 kW) | 5G4 mm² / 5G6 mm² | Driefasig, eigen beveiliging |
| `J` | — (enkel 300 mA) | Tuinhuis | **Voeding `BRD-TUIN`** — geen contactdoos | 0 | 3P+N 20 A | XVB 5G6 mm² in wachtbuis | Selectiviteit, zie §2 |

Omdat de kookplaat een vaste aansluitdoos wordt, is voor `A` enkel de algemene 300 mA vereist.
Wordt het alsnog een stopcontact 3N400V, dan moet `A` achter een 30 mA (plaats vrij op `D1`).

### 3.2 Algemene stopcontactkringen

Alle kringen hieronder: 2,5 mm² / automaat 20 A.

| id | Diff | Ruimte | Inhoud | Dozen | Vrij |
|---|---|---|---|---|---|
| `K` | `D1` | Keuken — werkvlak | 2× driedubbel boven aanrecht, dampkap, koelkast | 4 | 4 |
| `L` | `D1` | Keuken — eiland | 2× driedubbel eiland, dubbel onder spoelbak, combimicrogolf | 4 | 4 |
| `M` | `D1` | Woonkamer (eethoek) + Inkom | 3× driedubbel eethoek, dubbel achter deur inkom, 2× dubbel inkom | 6 | 2 |
| `N` | `D1` | Woonkamer (zithoek) | 5× vierdubbel | 5 | 3 |
| `P` | `D4` | Berging/Technische ruimte | 7× dubbel (incl. diepvriezer) + W.W. (warmwaterboiler) | 8 | 0 |
| `Q` | `D3` | Badkamer | 4× dubbel, 2× driedubbel boven wastablet, enkel bij meubel, infraroodpaneel plafond | 8 | 0 |
| `R` | `D4` | Slaapkamer 1 | 4× dubbel, 2× dubbel naast bed (usb), dubbel midden bed (elektrisch bed) | 7 | 1 |
| `S` | `D4` | Slaapkamer 2 | 6× dubbel, 1× driedubbel | 7 | 1 |
| `T` | `D4` | Slaapkamer 3 | 6× dubbel, 1× driedubbel | 7 | 1 |
| `U` | `D4` | Nachthal, Dakzolder, bureau slpk 2 en 3 | dubbel nachthal, 2× dubbel zolder, 2× bureaupunt (stopc./lichtpunt) | 5 | 3 |
| `V` | `D2` | Carport + Terras 1 | 2× dubbel carport, 3× dubbel terras — geschakeld via teleruptor | 5 | 3 |
| `W` | `D2` | Tuin | Stopcontact waterpomp | 1 | 7 |
| `X` | `D4` | Berging/Technische ruimte | Driedubbel bij coax/datapunt — ICT-kast (modem, switch, NVR) | 1 | 7 |
| `Y` | `D2` | Reserve | Vrije automaat, nog niet toegewezen | 0 | 8 |

**Totaal contactdozen hoofdbord: 74**

Bijzonderheden:

- `V` komt overeen met de bestaande kring 31 uit het bronbestand (geschakeld via drukknoppen).
  Controleer dat die bedrading 2,5 mm² is en geen 1,5 mm².
- `U`: de bureaupunten in slaapkamer 2 en 3 staan in het bronbestand als "stopc. / Lichtpunt" —
  nog niet beslist wat het wordt. Ze tellen voorlopig zowel hier als bij de lichtpunten (§6).
- `R`: de 3 geschakelde enkele stopcontacten (bestaande kringen 33, 34, 35) blijven op de
  verlichtingssturing staan en tellen hier niet mee.
- `X` is losgetrokken van `P` zodat internet en domotica blijven draaien als er in de berging
  iets uitvalt — en omdat `P` anders op 9 dozen kwam.

### 3.3 Kringen — onderverdeelbord tuinhuis

| id | Inhoud | Dozen | Automaat | Sectie |
|---|---|---|---|---|
| `T1` | 4× dubbel stopcontact | 4 | 20 A | 3G2,5 mm² |
| `T2` | Verlichting tuinhuis (2 lichtpunten) | — | 16 A | 3G1,5 mm² |
| `T3` | Reserve — vrije plaats in het bord | — | — | — |

---

## 4. Differentieelschakelaars

| id | Gevoeligheid / type | Kringen | Aantal | Vrij | Groepering |
|---|---|---|---|---|---|
| `DIFF-ALG` | 300 mA (of 100 mA) type A, 4-polig | volledige installatie, incl. `A`, `G`, `J` | — | — | AREI: verplicht aan het begin. Brandbeveiliging, geen persoonsbeveiliging |
| `D1` | 30 mA type A | `B`, `C`, `K`, `L`, `M`, `N` | 6 | 1 | Keuken + woonkamer, eethoek en inkom |
| `D2` | 30 mA type A | `D`, `E`, `F`, `V`, `W`, `Y` | 6 | 1 | Vaste toestellen berging + buitenkringen + reserve |
| `D3` | 30 mA type A | `Q` + bestaande verlichtingskringen 20, 22, 23, 29 | 5 | 2 | Badkamer, zuiver gehouden |
| `D4` | 30 mA type A | `P`, `R`, `S`, `T`, `U`, `X` | 6 | 1 | Nachtzone + stopcontacten berging + ICT-kast |
| `DIFF-TUIN` | 30 mA type A, 40 A | `T1`, `T2`, `T3` | 3 | — | Staat in `BRD-TUIN`, niet in het hoofdbord |

**23 kringen achter een 30 mA in het hoofdbord.**

AREI eist 30 mA voor: badkamer (álle kringen, ook verlichting), vaatwas, wasmachine, droogkast,
contactdozen buiten en in vochtige ruimtes. De verlichtingskringen 20, 22, 23 en 29 van de badkamer
tellen daarom mee voor de grens per differentieel.

### 4.1 Openstaand — kring `G` (laadpunt)

De wallbox is nog niet gekozen, en die keuze bepaalt de beveiliging:

| Wallbox | Bovenstroomse beveiliging |
|---|---|
| Met ingebouwde 6 mA DC-detectie (de meeste moderne modellen) | 30 mA **type A**, exclusief voor `G` |
| Zonder | 30 mA **type B**, exclusief voor `G` |

**Een laadpunt zonder enige 30 mA komt bij een keuring niet door.** `G` staat hier voorlopig enkel
achter `DIFF-ALG` omdat de keuze openstaat; reserveer hoe dan ook een plaats voor een eigen
differentieel, dat niets anders deelt. Voorzie ook load balancing in functie van het aansluitvermogen.

---

## 5. Rolluiken

| id | Ruimte | Bestaande kring | Sturing |
|---|---|---|---|
| `RL-01` | Woonkamer (eethoek) | 11 | links van schuifdeur |
| `RL-02` | Keuken | 13 | links van achterdeur |
| `RL-03` | Badkamer | 23 | rechts van raam |
| `RL-04` | Slaapkamer 1 | 25 | rechts van raam |

Geen zonnewering of screens op het bronbestand.

**Niet voorzien:** slaapkamer 2, slaapkamer 3 en de zithoek hebben geen rolluik. Als dat bewust is,
leg dan minstens de wachtbuizen — achteraf een motor bijplaatsen zonder leiding is een dure ingreep.

---

## 6. Lichtpunten — 72 totaal

| Zone | Ruimte | Aantal |
|---|---|---|
| Buiten | Pad buiten inkom | 5 |
| Buiten | Oprit | 4 |
| Buiten | Carport | 6 |
| Buiten | Terras 1 | 7 |
| Buiten | Tuinhuis | 2 |
| **Subtotaal buiten** | | **24** |
| Gelijkvloers | Inkom | 2 |
| Gelijkvloers | Wc gelijkvloers | 1 |
| Gelijkvloers | Woonkamer (zithoek) | 7 |
| Gelijkvloers | Woonkamer (eethoek) | 8 |
| Gelijkvloers | Keuken | 3 |
| Gelijkvloers | Berging/Technische ruimte | 5 |
| **Subtotaal gelijkvloers** | | **26** |
| Verdiep | Trap 1ste | 2 |
| Verdiep | Wc 1ste | 1 |
| Verdiep | Badkamer | 4 |
| Verdiep | Nachthal | 2 |
| Verdiep | Slaapkamer 1 | 6 |
| Verdiep | Slaapkamer 2 | 3 |
| Verdiep | Slaapkamer 3 | 3 |
| Verdiep | Dakzolder | 1 |
| **Subtotaal verdiep + zolder** | | **22** |

Kanttekeningen:

- De 2 bureaupunten "stopc. / Lichtpunt" (slaapkamer 2 en 3) zijn hier meegeteld én bij kring `U`,
  omdat nog niet beslist is wat ze worden.
- 4 lichtpunten hebben **geen kringnummer** in het bronbestand: 2× boven de kasten in slaapkamer 1
  en 2× centraal in het tuinhuis (die laatste vallen onder `T2`).
- Meerdere lichtpunten op één regel zijn armaturen op dezelfde kring, geen aparte kringen.
- AREI legt geen minimum aantal lichtpunten op, wel dat elke ruimte er minstens één heeft — dat is overal zo.

---

## 7. Bedieningen en stuuringangen

| Type | Aantal | Ingangen/stuk | Ingangen |
|---|---|---|---|
| Drukknop verlichting | 69 | 1 | 69 |
| Rolluiksturing bij het raam | 4 | 2 (op/neer) | 8 |
| Extra rolluikdrukknop elders | 5 | 2 (op/neer) | 10 |
| Bewegingssensor (pad, oprit, 2× carport, terras) | 5 | 1 | 5 |
| Timer / aanwezigheidsmelder dakzolder | 1 | 1 | 1 |
| Beldrukknop | 1 | 1 | 1 |
| **Totaal** | **85** | | **94** |

**Aannames** (beide verlagen het totaal indien anders):

- Elke rolluikbediening telt als **2 ingangen** (op en neer). Met een enkele toggle-knop: 85 ingangen.
- De beldrukknop gaat naar de sturingskast. Gaat hij rechtstreeks naar de interkom: 93 ingangen.

**Modules.** Bij 8 ingangen per module zijn er **12 modules** nodig (96 ingangen).
**Advies: 14 modules voorzien** (112 ingangen). Reden: 7 drukknoppen hebben in het bronbestand nog
geen kringnummer (4× slaapkamer 1, 1× slaapkamer 2, 1× slaapkamer 3, 1× tuinhuis) en moeten er nog
bij. Dat scheelt een module bijbestellen halverwege de werf.

---

## 8. Openstaande punten

| # | Punt | Blokkeert |
|---|---|---|
| 1 | **Laadpaal:** wallbox kiezen → bepaalt 30 mA type A of type B (§4.1) | Bordindeling, materiaallijst |
| 2 | **Combimicrogolf:** sommige keurders zien een combimicro met ovenfunctie als "oven" en eisen een aparte kring. Grijze zone — vooraf aftoetsen met de installateur | Kring `L` |
| 3 | **Warmwaterboiler:** zit nu op kring `P`. Bij dag-/nachttarief moet hij er weer uit, via een dag-nachtcontactor op een eigen kring | Kring `P` (zit op 8/8) |
| 4 | **Vermogens aanvullen:** de kolommen N-L1 / N-L2 / N-L3 staan op 1720 / 6840 / 2460 W maar zijn slechts gedeeltelijk ingevuld — kookplaat, oven, laadpunt en de meeste stopcontacten van woonkamer en inkom ontbreken. Aanvullen vóór de fasen definitief toegewezen worden | Fasebalans |
| 5 | **Verlichtingskringen achter 30 mA?** Buiten de badkamer geen AREI-eis, wel gangbaar bij nieuwbouw. Met 7 kringen per differentieel zijn er dan ca. 5 differentiëlen extra nodig | Bordgrootte |
| 6 | **Bureaupunten slaapkamer 2 en 3:** stopcontact, lichtpunt of beide? | Telling §6, kring `U` |
| 7 | **Rolluiken slaapkamer 2, 3 en zithoek:** plaatsen of enkel wachtbuis? | §5 |
| 8 | **Badkamer:** voor het Vasco-infraroodpaneel liefst een vaste aansluitdoos i.p.v. een contactdoos in het plafond. Alle contactdozen buiten volume 0/1/2 houden (min. 60 cm van bad/douche) | Kring `Q` |
| 9 | **Kabellengtes:** bij trajecten boven ca. 30 m (tuinhuis, carport, laadpaal) spanningsval narekenen; mogelijk een sectie hoger | Materiaallijst |
| 10 | **Overspanningsbeveiliging type 2** aan het begin van het hoofdbord, en overweeg er ook één in `BRD-TUIN` | Bordindeling |

---

## 9. Voorbehoud

Dit is een ontwerpvoorstel, geen uitvoeringsdossier. Het definitieve eendraadschema en situatieschema
moeten door de installateur opgemaakt worden, en de installatie moet vóór ingebruikname gekeurd
worden door een erkend organisme.
