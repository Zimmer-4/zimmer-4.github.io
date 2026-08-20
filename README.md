# Zimmer 4 – Mandanten-Reporting-Portal

Passwortgeschützte, statische Finanzberichte pro Mandant — gehostet auf GitHub
Pages, verschlüsselt mit StatiCrypt (AES-256). Kein Server, kein Backend, kein Abo.

**Live:** `https://zimmer-4.github.io/<kürzel>/` → Login → Berichtsauswahl.

> **Dieses Repo ist nur die Auslieferung.** Generatoren, Mandanten-Excel,
> Konfiguration und die ausführliche Doku liegen im internen Projektordner
> („Financial Statement", auf OneDrive). Wer hier etwas von Hand ändert, arbeitet
> am falschen Ort — publiziert wird ausschliesslich über das dortige
> `_tools/publish.py` bzw. den Launcher. Ablauf: `_docs/ALLTAG.md` dort.

---

## 1. Architektur

```
Excel (Bexio-Daten)  ──build_*.py──►  HTML-Report (unverschlüsselt, temporär)
                                          │
                                   staticrypt (AES-256, Salt)
                                          │
                                          ▼
                            <kürzel>/<report>.html (verschlüsselt)  ──git push──►  GitHub Pages (HTTPS)
```

- **Ein Report = eine self-contained HTML-Datei.** Alle Zahlen sind eingebettet,
  es wird nichts nachgeladen — mit einer Ausnahme: das Cockpit holt Chart.js von
  `cdnjs.cloudflare.com`. Ohne Netz zeigt es die Zahlen, aber keine Diagramme.
  Der Monatsvergleich kommt ganz ohne externe Ressourcen aus.
- **StatiCrypt** verschlüsselt die Datei und ersetzt sie durch eine Login-Seite
  im Zimmer-4-Design (`staticrypt-template.html`). Passwort = pro Mandant.
- **„Remember 7 Tage":** Nach einmaligem Login öffnen sich alle weiteren Reports
  desselben Mandanten ohne erneute Passworteingabe (gleicher Salt + Passwort).

---

## 2. Ordnerstruktur

```
zimmer-4.github.io/
├── zgg/                       # verschlüsselt (öffentlich, aber unlesbar)
│   ├── index.html             #   Login → Berichtsauswahl
│   ├── cockpit.html           #   Erfolgs-Cockpit (Dashboard)
│   └── er.html                #   Monatsvergleich Erfolgsrechnung
├── kon/                       # gleiche drei Dateien
├── kas/                       # gleiche drei Dateien
├── staticrypt-template.html   # Login-Design (Mandantenname via Flag)
├── tools/check_safe.py        # Security-Gate vor jedem Push
├── index.html                 # Landing Page
├── status.json                # was wann publiziert wurde (der Launcher liest es)
├── SALT.md                    # wo der Salt liegt und warum nicht hier
├── robots.txt  .nojekyll  .gitignore
└── README.md
```

**Was hier bewusst NICHT liegt:** der StatiCrypt-Salt (`.staticrypt.json`), die
Passwörter (`passwords.env`) und die unverschlüsselten Quell-Reports. Alle drei
gehören ins interne Projekt. `.gitignore` sperrt sie zusätzlich aus, falls doch
einmal eine Kopie im Arbeitsverzeichnis landet. Zum Salt siehe `SALT.md`.

---

## 3. Namenskonvention

| Typ | Datei | Bedeutung |
|---|---|---|
| aktueller Report | `cockpit.html` · `er.html` | wird bei jedem Publish überschrieben — **diese URL bekommt der Mandant** |
| Archiv-Schnappschuss | `cockpit-2026-06.html` · `er-2026-06.html` | eingefrorener Stand, bleibt unverändert liegen |
| Berichtsauswahl | `index.html` | verschlüsselt, wird mitgeneriert |

> **Merksatz:** Die Datei *ohne* Datum ist immer die aktuelle. Dateien *mit*
> Datum sind Momentaufnahmen und werden nie überschrieben.

Ob Archivstände entstehen, steuert `_archiv_erstellen` in der Konfiguration des
internen Projekts. Die Berichtsauswahl wird aus den real vorhandenen Dateien
gebaut — sie kann nicht auf einen Report zeigen, den es nicht gibt.

---

## 4. Publizieren

**Nicht in diesem Repo von Hand.** Der Ablauf läuft im internen Projekt:

```
Mandanten-Excel aktualisieren  →  Launcher starten  →  Mandant + Periode wählen
                               →  [Generieren & Publizieren]
```

`publish.py` erledigt dann alles in einem Zug: Reports bauen, mit dem
festgelegten Salt verschlüsseln, in den Mandantenordner dieses Repos schreiben,
Berichtsauswahl und `status.json` nachziehen, `tools/check_safe.py` ausführen und
erst danach committen und pushen.

Der lokale Klon dieses Repos steht in `%APPDATA%\Zimmer4\config.json` unter
`berichte_path` — es gibt genau einen. Details in `_docs/ALLTAG.md` des Projekts.

---

## 5. Neuer Mandant

Alles im internen Projekt, hier ist nichts vorzubereiten — der Mandantenordner
entsteht beim ersten Publish von selbst. Nötig sind dort: Eintrag in
`_config/mandants.json`, Passwort in `_config/passwords.env`, Mandantenordner mit
den Bexio-Rohdaten. Schritt für Schritt in `_docs/ALLTAG.md`, Kapitel „Neuen
Mandanten aufnehmen".

**Der einzige Handgriff in diesem Repo:** das neue Kürzel in
`tools/check_safe.py` bei `MANDANT_DIRS` ergänzen — sonst prüft das Gate den
neuen Ordner nicht.

Aktuelle Mandanten-Kürzel: **zgg**, **kon**, **kas**. Die Klarnamen werden
bewusst NICHT im (öffentlichen) Repo geführt — die Zuordnung Kürzel→Mandant
bleibt lokal. Auch die Login-Seite nennt den Namen erst nach dem Entschlüsseln.

---

## 6. Sicherheit

- **Öffentliches Repo, aber nur verschlüsselte Inhalte.** Reports sind AES-256 und
  ohne Passwort nur StatiCrypt-Kauderwelsch. Dateinamen sind neutral.
- **Weder Passwörter noch Salt noch unverschlüsselte Reports liegen hier** — siehe
  Kapitel 2. `.gitignore` sperrt `*.env` und `_src/` zusätzlich aus.
- **`tools/check_safe.py` läuft vor jedem Push** (aus `publish.py` heraus) und
  blockiert bei Exit-Code ≠ 0. Es prüft vier Regeln: keine `.env` getrackt, kein
  `_src/` getrackt, jede HTML in einem Mandantenordner entweder verschlüsselt
  oder ausdrücklich als `PUBLIC-PLACEHOLDER` markiert, und Report-Dateien
  (aktuelle wie datierte) ausnahmslos verschlüsselt.
- **`noindex` + `robots.txt`** halten die Seiten aus Suchmaschinen heraus.
- **HTTPS** über GitHub Pages; „Remember" speichert nur den Passphrase-Hash lokal.

Von Hand prüfen lässt sich das jederzeit:

```bash
python tools/check_safe.py
```

---

## 7. Setup auf einem neuen Rechner

Nicht dieses Repo klonen, sondern im internen Projekt `python _tools/setup.py`
ausführen — das prüft die Abhängigkeiten, klont dieses Repo an die richtige
Stelle und legt die Desktop-Verknüpfung an. Anleitung:
`_docs/SETUP_Neues_Geraet.md` im Projekt.

Voraussetzungen: Python 3.10+, Git, Node.js 18+ und `npm install -g staticrypt`.
