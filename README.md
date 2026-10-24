# Begrenztes Vertrauen: Lager und Splitter – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-begrenztes-vertrauen-demo.streamlit.app/)** -->

Elftes Stück der **Netzwerkanalyse-Reihe** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ und drittes des **Anpassungs-Arms** (Stücke 9 bis 12): wie in der [Meinungsbildungs-Demo](https://sebastianhanisch-meinungsbildung-demo.streamlit.app/) (Stück 9) mitteln die Betriebe ihre Einschätzung, aber **nur mit Partnern, deren Einschätzung nicht zu weit von der eigenen liegt** (Hegselmann–Krause). Die [Voter-Demo](https://sebastianhanisch-voter-modell-demo.streamlit.app/) (Stück 10) übernimmt dagegen zufällig; die [Blockmodell-Demo](https://sebastianhanisch-stochastic-block-demo.streamlit.app/) (Stück 2) liefert die Verbünde.

In einem Netz von Subunternehmern und Lieferanten schätzt jeder Betrieb eine Zahl zwischen 0 und 1 (zum Beispiel „wie lange dauert die Umstellung auf das neue Verfahren“) und hört nur auf Partner innerhalb seines **Vertrauensradius ε**. Der Konsens ist dann nicht mehr sicher: je nach Radius bleiben ein, zwei oder viele **Lager** übrig. Die Demo zeigt, **wie viele Lager bleiben, was das Netz ändert und was von bekannten Vermutungen gilt**.

## Kernfrage

**Wie viele Lager bleiben, und was ändert das Netz?** Der Hook: im **vollständigen Graphen** (jeder kennt jeden) ist die Zahl der Lager im Median über zufällige Starts eine Treppe in ε, mit Konsens bei ε = 0,25 in etwa 80 bis 90 % der Läufe; im **dünnen Netz** zerfällt die Meinung bei kleinem Radius (ε = 0,10) in fast nur gestrandete **Splitter**, ab ε ≈ 0,2 in einen großen Block und viele **Splitter**, und der Konsens braucht einen viel größeren Radius. Zwei Vermutungen gelten nur eingeschränkt: die **Reihenfolge** der Meinungen bleibt nur im vollständigen Graphen erhalten, und dass der **Konsens bei sinkendem Radius zurückkehrt** (Lorenz 2006), zeigt sich im Beispiel mit gleichabständigem Start und 400 Betrieben; bei zufälligem Start steigt der Anteil der Läufe mit Konsens im Ganzen mit ε. Alle Ergebnisse sind **Modellbefunde**, keine Aussagen über die Wirklichkeit; „Polarisierung“ ist hier ein Modellbegriff.

## Befunde und Korrekturen gegenüber dem Plan

- **Die Treppe im vollständigen Graphen** (bestätigt): bei zufälligem Start mit 200 Betrieben bleiben im Median 4 / 2,5 / 2 / 1 Lager bei ε = 0,10 / 0,15 / 0,20 / 0,25; Konsens (größtes Lager mindestens 99 %) gibt es in 12,5 % der Läufe bei ε = 0,20, in 87,5 % bei 0,25 und in allen ab 0,30 (nur 8 Läufe je Zelle, die Prozentwerte sind Achtel mit etwa ±12 Prozentpunkten Unsicherheit; eine Nachprüfung mit 60 Läufen gab 7 % bei 0,20, 82 % bei 0,25 und 100 % bei 0,30). Im Einzelfall ist die Lagerzahl nicht monoton in ε.
- **Im dünnen Netz zerfällt die Meinung in einen Block und viele Splitter** (neu gegenüber dem Plan): bei ε = 0,10 hat das Netz mit *c* = 6 im Median 61,5 bis 96,5 Gruppen (der vollständige Graph 4), die meisten (im Gitter etwa die Hälfte) sind einzelne Betriebe, die im Radius niemand erreicht. Das gilt für kleines ε: bei ε = 0,10 ist das größte Lager nur 7 bis 33 % der Betriebe groß (Nachprüfung), erst ab ε ≈ 0,2 gibt es einen großen Block (bei 0,25 größtes Lager 80,9 bis 96,2 %). Bei ε = 0,25 hat das größte Lager 80,9 bis 96,2 % der Betriebe, aber **in keinem der sechs Netztypen** mindestens in der Hälfte der Netze Konsens; der gibt es erst ab ε = 0,4 (Zufallsnetz, Verbünde, Ring) bzw. 0,5 (Potenzgesetz-Netz, skalenfrei, Gitter); im Potenzgesetz-Netz selbst bei 0,5 nur in 62,5 % der Netze.
- **Die Reihenfolge der Meinungen bleibt nur im vollständigen Graphen erhalten** (Plan-Vermutung „zu prüfen“: falsch für Netze): bei ε = 0,20 und 120 Betrieben kehrt sie sich im vollständigen Graphen in 0 von 8 Läufen um, in jedem der sechs Netztypen in 8 von 8 Läufen, im Median schon im ersten Schritt.
- **Der Konsens kehrt bei sinkendem Radius zurück (Lorenz 2006), im Beispiel mit gleichabständigem Start und 400 Betrieben:** im vollständigen Graphen gibt es bei ε = 0,1900 Konsens, obwohl bei 0,1925 bis 0,2050 zwei Lager bleiben (und ab 0,2075 wieder Konsens ist); die Lage hängt stark an der Betriebszahl (in Nachprüfungsläufen: bei 100 Betrieben Konsens bei 0,1775 bis 0,1925 und zwei Lager bis 0,225, bei 200 Betrieben im Bereich 0,185 bis 0,21 nirgends, bei 500 erst bei 0,21). Bei zufälligem Start steigt der Anteil der Läufe mit Konsens im Ganzen mit ε: in den 12 Läufen je Radius monoton; bei 80 Läufen je Radius (Nachprüfung, 400 Betriebe) nicht streng, mit Konsens in 1 von 80 Läufen bei ε = 0,17 und 2 von 80 bei 0,19, aber 0 von 80 bei 0,18 (17,5 % bei 0,20, 91 % bei 0,24).
- **Verbünde halten Lager nur bei sehr wenigen Querkanten** (Plan: „Verbundstruktur stabilisiert Cluster“, eingeschränkt): bei ε = 0,10 und zufälligem Start hat das Netz mit 240 Betrieben im Median 3 Lager bei 50 % Kanten innen und 8 bei 99 %; beginnt jeder Verbund bei seiner eigenen Meinung, bleiben schon ab 80 % innen sechs Lager. Die Ausrichtung der Meinung am Verbund wirkt also früher als die Netzstruktur.
- **Brücke zu Stück 9:** ist ε größer als die Spanne der Anfangsmeinungen, ist das die DeGroot-Mittelung mit Selbstgewicht 1/(*d* + 1); der Endwert weicht in allen Netztypen um höchstens 1,4 · 10⁻¹¹ von Σ (*d* + 1) *x*(0) / Σ (*d* + 1) ab.
- **Das Netz steht in allen Läufen still:** in allen 49 Zellen der Messreihe (je 8 Netze) vor der Obergrenze von 20000 Schritten; die längsten Läufe hat „Gitter“ bei ε = 0,15 (4038 Schritte im Median, gegen 7 im vollständigen Graphen).

## Modell

Netz ungerichtet (größte zusammenhängende Gruppe) oder vollständiger Graph; jeder Betrieb *i* hat eine Meinung *x*<sub>*i*</sub> ∈ [0, 1]. **Hegselmann–Krause, synchron:** *x*<sub>*i*</sub>(*t* + 1) = Mittelwert aller *x*<sub>*j*</sub>(*t*) mit *j* = *i* oder *j* Partner von *i* und |*x*<sub>*j*</sub>(*t*) − *x*<sub>*i*</sub>(*t*)| ≤ ε (Gleichheit an der Grenze zählt als vertraut, Toleranz 10<sup>−15</sup>). **Stillstand:** größte Änderung eines Schritts unter 10<sup>−12</sup>. **Lager:** Gruppen mit gleicher Endmeinung (Abstand höchstens 10<sup>−6</sup>) und mindestens 5 % der Betriebe; kleinere Gruppen sind **Splitter**; **Konsens:** das größte Lager hat mindestens 99 %. **Anfangsverteilungen:** zufällig gleichverteilt, gleichabständig, nach Verbünden ausgerichtet (Mitte des Verbunds plus Rauschen 0,04), zwei Lager (um 0,25 und 0,75).

## Methodik

| Baustein | Inhalt |
|---|---|
| **Netze** | Generatoren aus `k-core-demo` (Stück 1) als Kopie: Zufallsnetz, Potenzgesetz-Netz, skalenfrei (BA), Verbünde, Ring mit Abkürzungen, Gitter; dazu der vollständige Graph; für Experiment 4 ein Blockmodell mit einstellbarem Anteil innen (Kopie aus Stück 9) |
| **Hauptansicht** | Netz mit Meinungen als Farbe, Regler „Schritt“, Bahnen der Meinungen über die Schritte, Kennzahlen (Lager, größtes Lager, Splitter, Gruppen, Schritte) |
| **Experiment 1** | Lager, größtes Lager und Anteil der Netze mit Konsens über ε = 0,10, 0,15, 0,20, 0,25, 0,30, 0,40, 0,50 je Netztyp (zufälliger Start, Median über die festen Netze) |
| **Experiment 2** | Läufe, in denen sich die Reihenfolge der Meinungen umkehrt (ε = 0,20); ε = 2 gegen die DeGroot-Formel |
| **Experiment 3** | vollständiger Graph mit 400 Betrieben: Lager über ein feines ε-Raster (0,10 bis 0,25 in Schritten von 0,0025) bei gleichabständigem Start; Anteil der Läufe mit Konsens bei zufälligem Start (12 Läufe, Raster 0,01) |
| **Experiment 4** | Verbünde (240 Betriebe, *c* = 12), Anteil der Kanten innen 50 bis 99 %, ε = 0,10, 0,25, zufälliger Start gegen Start nach Verbünden |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`. Netze der Messreihen: die acht festen Netze `SWEEP_SEEDS` je Zelle, *n* = 200 (Experiment 2: 120), *c* = 6, zufälliger Start, Median über die Netze; Gitter-Netze haben 196 Betriebe.

| Frage | Befund |
|---|---|
| **Stimmen die Bausteine?** | ein Schritt gegen eine unabhängige Schleifenfassung auf 120 Zufallsnetzen (auch an der Grenze \|Δ\| = ε); ε über der Spanne gegen die Matrix *D̃*<sup>−1</sup>*Ã* und gegen die Formel Σ (*d* + 1) *x* / Σ (*d* + 1); Meinungen bleiben im Bereich, die Spanne wächst nie, der Stillstand ist ein Fixpunkt; im vollständigen Graphen bleibt die Reihenfolge erhalten (120 Läufe) und die Lager liegen mehr als ε auseinander (`tests/test_oracle_begrenztes_vertrauen.py`) |
| **Wie viele Lager, wo kippt das Netz?** | Tabellen zu Experiment 1 |
| **Bleibt die Reihenfolge?** | Tabelle zu Experiment 2 |
| **Kehrt der Konsens zurück?** | Tabellen zu Experiment 3 |
| **Halten Verbünde Lager?** | Tabelle zu Experiment 4 |
| **Standardlauf (Vollständiger Graph: die Treppe)** | 100 Betriebe, 4950 Partnerschaften; Stillstand nach 4 Schritten: 2 Lager (größtes 62,0 %), 0 Splitter, 2 Gruppen |
| **Preset Dünnes Netz: ein Block und viele Splitter** | 150 Betriebe, 450 Partnerschaften; Stillstand nach 102 Schritten: 1 Lager (größtes 96,0 %), 6 Splitter, 7 Gruppen; Reihenfolge kehrt sich in Schritt 1 um |
| **Preset Gleichabständig: der Konsens kehrt zurück** | 100 Betriebe, 4950 Partnerschaften; Stillstand nach 73 Schritten: Konsens |
| **Preset Zwei Lager bleiben** | 100 Betriebe, 4950 Partnerschaften; Stillstand nach 1 Schritten: 2 Lager (größtes 50,0 %), 0 Splitter, 2 Gruppen |
| **Preset Verbünde halten Lager** | 120 Betriebe, 720 Partnerschaften; Stillstand nach 34 Schritten: 6 Lager (größtes 16,7 %), 0 Splitter, 6 Gruppen; Reihenfolge kehrt sich in Schritt 1 um |
| **Preset Reihenfolge kehrt sich um** | 100 Betriebe, 271 Partnerschaften; Stillstand nach 122 Schritten: 1 Lager (größtes 97,0 %), 3 Splitter, 4 Gruppen; Reihenfolge kehrt sich in Schritt 1 um |

**Experiment 1: Lager** (Gruppen mit gleicher Meinung und mindestens 5 % der Betriebe; Median):

| Netztyp | ε = 0,10 | ε = 0,15 | ε = 0,20 | ε = 0,25 | ε = 0,30 | ε = 0,40 | ε = 0,50 |
|---|---|---|---|---|---|---|---|
| Vollständig (jeder kennt jeden) | 4 | 2,5 | 2 | 1 | 1 | 1 | 1 |
| Zufallsnetz | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| Potenzgesetz-Netz | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| Skalenfreies Netz (BA) | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| Verbünde | 3 | 2 | 1 | 1 | 1 | 1 | 1 |
| Ring mit Abkürzungen | 2 | 3,5 | 1 | 1 | 1 | 1 | 1 |
| Gitter | 2 | 3,5 | 2 | 2 | 1 | 1 | 1 |

**Größtes Lager** (Prozent der Betriebe; Median):

| Netztyp | ε = 0,10 | ε = 0,15 | ε = 0,20 | ε = 0,25 | ε = 0,30 | ε = 0,40 | ε = 0,50 |
|---|---|---|---|---|---|---|---|
| Vollständig (jeder kennt jeden) | 31,2 | 50,5 | 54,8 | 100,0 | 100,0 | 100,0 | 100,0 |
| Zufallsnetz | 34,8 | 65,8 | 93,0 | 96,2 | 97,7 | 99,2 | 100,0 |
| Potenzgesetz-Netz | 22,2 | 45,0 | 77,8 | 85,8 | 90,5 | 96,5 | 100,0 |
| Skalenfreies Netz (BA) | 26,8 | 50,2 | 90,8 | 94,0 | 96,2 | 98,5 | 100,0 |
| Verbünde | 33,5 | 68,4 | 90,8 | 93,5 | 97,0 | 99,5 | 100,0 |
| Ring mit Abkürzungen | 8,8 | 30,0 | 82,5 | 90,2 | 95,5 | 99,0 | 100,0 |
| Gitter | 9,4 | 26,3 | 63,8 | 80,9 | 93,6 | 99,0 | 100,0 |

**Anteil der Netze mit Konsens** (größtes Lager mindestens 99 %; Prozent):

| Netztyp | ε = 0,10 | ε = 0,15 | ε = 0,20 | ε = 0,25 | ε = 0,30 | ε = 0,40 | ε = 0,50 |
|---|---|---|---|---|---|---|---|
| Vollständig (jeder kennt jeden) | 0,0 | 0,0 | 12,5 | 87,5 | 100,0 | 100,0 | 100,0 |
| Zufallsnetz | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 50,0 | 100,0 |
| Potenzgesetz-Netz | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 12,5 | 62,5 |
| Skalenfreies Netz (BA) | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 25,0 | 100,0 |
| Verbünde | 0,0 | 0,0 | 0,0 | 0,0 | 12,5 | 75,0 | 100,0 |
| Ring mit Abkürzungen | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 50,0 | 100,0 |
| Gitter | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 37,5 | 100,0 |

**Experiment 2: Läufe, in denen sich die Reihenfolge der Meinungen umkehrt** (ε = 0,20, 120 Betriebe, 8 Netze):

| Netztyp | Läufe mit Umkehr | Schritt der ersten Umkehr (Median) |
|---|---|---|
| Vollständig (jeder kennt jeden) | 0 von 8 | – |
| Zufallsnetz | 8 von 8 | 1 |
| Potenzgesetz-Netz | 8 von 8 | 1 |
| Skalenfreies Netz (BA) | 8 von 8 | 1 |
| Verbünde | 8 von 8 | 1 |
| Ring mit Abkürzungen | 8 von 8 | 1 |
| Gitter | 8 von 8 | 1 |

**Brücke zu Stück 9: ε = 2 gegen die Formel Σ (*d* + 1) *x*(0) / Σ (*d* + 1)** (größte Abweichung des Endwerts über 8 Netze):

| Netztyp | größte Abweichung |
|---|---|
| Vollständig (jeder kennt jeden) | 6,7 · 10⁻¹⁶ |
| Zufallsnetz | 4,8 · 10⁻¹³ |
| Potenzgesetz-Netz | 1,9 · 10⁻¹² |
| Skalenfreies Netz (BA) | 5,3 · 10⁻¹³ |
| Verbünde | 2,0 · 10⁻¹² |
| Ring mit Abkürzungen | 9,6 · 10⁻¹² |
| Gitter | 1,4 · 10⁻¹¹ |

**Experiment 3: gleichabständiger Start im vollständigen Graphen mit 400 Betrieben** (Lager über das Raster; zusammengefasst nach gleichem Ergebnis):

| ε | Lager | Konsens |
|---|---|---|
| 0,1000 bis 0,1025 | 4 | nein |
| 0,1050 | 3 | nein |
| 0,1075 | 4 | nein |
| 0,1100 bis 0,1750 | 3 | nein |
| 0,1775 bis 0,1875 | 2 | nein |
| 0,1900 | 1 | ja |
| 0,1925 bis 0,2050 | 2 | nein |
| 0,2075 bis 0,2500 | 1 | ja |

**Zufälliger Start** (12 Läufe je Radius):

| ε | Läufe mit Konsens | mittlere Zahl der Lager |
|---|---|---|
| 0,10 | 0,0 | 3,75 |
| 0,11 | 0,0 | 3,50 |
| 0,12 | 0,0 | 3,17 |
| 0,13 | 0,0 | 2,92 |
| 0,14 | 0,0 | 2,83 |
| 0,15 | 0,0 | 2,67 |
| 0,16 | 0,0 | 2,42 |
| 0,17 | 0,0 | 2,17 |
| 0,18 | 0,0 | 2,00 |
| 0,19 | 0,0 | 2,00 |
| 0,20 | 8,3 | 1,92 |
| 0,21 | 16,7 | 1,83 |
| 0,22 | 33,3 | 1,67 |
| 0,23 | 66,7 | 1,33 |
| 0,24 | 83,3 | 1,17 |
| 0,25 | 83,3 | 1,17 |

**Experiment 4: Lager (größtes Lager in Klammern) in Verbünden** (240 Betriebe, *c* = 12, Median über 8 Netze):

| Kanten innen | ε = 0,10, zufälliger Start | ε = 0,10, Start nach Verbünden | ε = 0,25, zufälliger Start | ε = 0,25, Start nach Verbünden |
|---|---|---|---|---|
| 50 % | 3 (49 %) | 4 (33 %) | 1 (100 %) | 1 (100 %) |
| 80 % | 3 (48 %) | 6 (17 %) | 1 (99 %) | 1 (100 %) |
| 90 % | 3 (40 %) | 6 (17 %) | 1 (99 %) | 1 (100 %) |
| 95 % | 4 (32 %) | 6 (17 %) | 1 (99 %) | 1 (100 %) |
| 99 % | 8 (16 %) | 6 (17 %) | 2 (85 %) | 3 (67 %) |

### Hypothesen des Einzelplans

| | Hypothese | Ergebnis |
|---|---|---|
| H1 | Im vollständigen Graphen ist die Lagerzahl eine Treppe in ε, Konsens ab ε ≈ 0,25 | ✅ 4 → 1 Lager (ε = 0,10 → 0,25), Konsens in 87,5 % der Läufe bei 0,25 (8 Läufe; Nachprüfung mit 60 Läufen: 82 %) |
| H2 | In dünnen Netzen zerfällt die Meinung in einen großen Block und viele Splitter; der Konsens braucht ein viel größeres ε | ✅ 61,5 bis 96,5 Gruppen bei ε = 0,10; Konsens erst ab 0,4 bis 0,5 |
| H3 | Die Reihenfolge der Meinungen bleibt erhalten | ❌ nur im vollständigen Graphen (0 von 8 Läufen mit Umkehr); in allen sechs Netztypen 8 von 8 |
| H4 | Der Konsens kehrt bei sinkendem ε kurz zurück (Lorenz 2006) | ⚠ im Beispiel mit gleichabständigem Start (400 Betriebe, ε = 0,1900); bei zufälligem Start in den 12 Läufen je Radius nicht, die Lage hängt an der Betriebszahl |
| H5 | Verbünde halten Lager | ⚠ nur bei sehr wenigen Querkanten (99 % innen: 8 Lager gegen 3 bei 50 %); ein nach Verbünden ausgerichteter Start hält sechs Lager schon ab 80 % innen |
| H6 | ε größer als die Spanne ist DeGroot mit Selbstgewicht 1/(*d* + 1) (Brücke zu Stück 9) | ✅ Abweichung höchstens 1,4 · 10⁻¹¹ |
| H7 | Das Netz steht in endlich vielen Schritten still | ✅ beobachtet in allen 49 Zellen der Messreihe (Obergrenze nie erreicht); als Satz nur im vollständigen Graphen bekannt |
| H8 | Im Endzustand liegen die Lager mehr als ε auseinander | ✅ im vollständigen Graphen (120 Läufe im Orakel-Test); in Netzen nicht geprüft |

## Ehrliche Grenzen

- **Eine Dimension, gleicher Radius für alle, synchrone Schritte, gleiche Gewichte:** mit mehreren Dimensionen, verschiedenem Radius, asynchronen Schritten oder ungleichen Gewichten ändern sich Lager und Verlauf.
- **Festes Netz:** das Netz ändert sich nicht mit den Meinungen (Stück 12).
- **Lagerzählung hängt an Schwellen:** 5 % für ein Lager, 99 % für Konsens, 10<sup>−6</sup> für gleiche Meinung, 10<sup>−12</sup> für den Stillstand. Andere Schwellen zählen anders.
- **Stichproben:** Mediane über acht (App: vier) feste Netze; die Streuung zwischen den Netzen ist nicht ausgewiesen. Der Konsens-Rückkehr-Befund hängt am Raster (0,0025) und an der Netzgröße (400 Betriebe) und gilt für den gleichabständigen Start; für andere Größen verschiebt sich das Band.
- **Dichte Rechnung:** bis 200 Betriebe in der App (Experiment 3: 400 im vollständigen Graphen).
- **Modellbefund:** die Demo zeigt Verhalten im Modell, nicht die Wirkung in der Wirklichkeit. Ob der Kontakt mit anderen Meinungen echte Polarisierung verstärkt oder mildert, ist empirisch umstritten (Bail u. a. 2018); wie weit Meinungsmodelle echte Daten treffen, ist offen (Flache u. a. 2017). Kein politisches Beispiel.
- **Literatur (nachgeschlagen am 2026-10-20, nur Zusammenfassungen gesehen):** Hegselmann und Krause, JASSS 5(3), 2002; Lorenz, JASSS 9(1), Artikel 8, 2006; Blondel, Hendrickx und Tsitsiklis, IEEE Trans. Autom. Control 54(11), 2009, S. 2586–2597; Bail u. a., PNAS 115(37), 2018, S. 9216–9221; Flache u. a., JASSS 20(4), 2017. Die Arbeiten selbst sind nicht vollständig gelesen.

## Verifikation

- **Kern:** Handwerte auf Mini-Instanzen (`tests/conftest.py`, `tests/test_algorithm.py`): Pfad (0; 0,4; 1,0) mit ε = 0,5 (zwei Lager), Dreieck, DeGroot-Fall (2,7/7), Ordnungsumkehr auf dem Pfad, Gleichheit an der Grenze, Lagerzählung, Anfangsverteilungen, Bilder des Schritt-Reglers.
- **Orakel:** `tests/test_oracle_begrenztes_vertrauen.py` – Schritt gegen eine Schleifenfassung, DeGroot-Fall gegen die Matrix und die Formel, Eigenschaften (Bereich, Spanne, Fixpunkt), Ordnungserhalt und Lagerabstand im vollständigen Graphen, Umkehr in Netzen.
- **Netze und Läufe:** gültig in allen Ecken der Regler, deterministisch je Seed (auch über Prozesse mit verschiedenem Hash-Seed), Blockmodell mit dem verlangten Anteil innen (`tests/test_scenario.py`).
- **Verdikte:** jede Schwelle und jede Zahl im Text an von Hand gesetzten Werten (`tests/test_verdicts.py`), Randfälle (Regler-Ecken für alle Netztypen und Modi, Obergrenze der Schritte, kleinster und größter Radius, alle Abbildungen) in `tests/test_edge_cases.py`.
- **Befunde:** jede Zahl dieser README in `tests/test_claims.py`.
- **Mutationsprüfung des Kerns:** (`bvt_algorithm.py`, 57 Stellen, ohne die langsamen Aussagen-Tests in der Suite der Überlebenden): 29 Stellen sind durch wortgleiche Zeilen in Nachbar-Demos gesichert, 27 Mutanten gefangen (4 davon erst nach Ergänzung von Tests: die Lückengrenze der Gruppen und das Vorzeichen des Rauschens in den Anfangsverteilungen), 1 als äquivalent festgehalten (die Toleranzgrenze der Ordnungsprüfung). Zustand in `tests/mutation_state.json`.
- **Presets:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, jedes Preset zeigt, wofür es benannt ist.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum, jeder Netztyp und jede Anfangsverteilung, Schritt-Regler, neuer Lauf, Permalink, alle vier Experimente) und Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `bvt_algorithm.py` | Kern: Schritt und Lauf nach Hegselmann–Krause, Lagerzählung, Ordnungsumkehr, DeGroot-Formel, Anfangsverteilungen, Netz-Hilfen, Blockmodell |
| `bvt_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `bvt_evaluation.py` | Analyse, Verdikt-Logik, Messreihen über feste Netze |
| `bvt_layout.py` | Fester Kopf (Stylesheet) |
| `bvt_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `bvt_scenario.py` | Netze: Generatoren (Kopie aus `k-core-demo`), Anordnung |
| `bvt_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest, networkx, scipy (nur für die Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Instanzen und Handwerte, Orakel, Netze, Verdikte, Randfälle, Presets, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe, Befunde |

## Bewusst nicht umgesetzt

- **Mehrere Dimensionen, verschiedener Radius je Betrieb, asynchrone Schritte:** eigene Fragen.
- **Zufälliges Übernehmen** (Stück 10), **Mittelung mit allen Partnern** (Stück 9), **Standortwahl nach Nachbarn** (Stück 12): eigene Demos der Reihe.
- **Politische Beispiele und Daten aus der Wirklichkeit:** nicht Teil der Demo.
- **Netze über 200 Betriebe live:** die Matrizen sind dicht.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
