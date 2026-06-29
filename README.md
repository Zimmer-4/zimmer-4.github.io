# Zimmer 4 – Mandanten-Reporting-Portal

Passwortgeschützte, statische Finanzberichte pro Mandant — gehostet auf GitHub
Pages, verschlüsselt mit StatiCrypt (AES-256). Kein Server, kein Backend, kein Abo.

**Live:** `https://zimmer-4.github.io/<kürzel>/` → Login → Berichtsauswahl.

---

## 1. Architektur

```
Excel (Bexio-Daten)  ──build_*.py──►  HTML-Report (unverschlüsselt, in _src/)
                                          │
                                   staticrypt (AES-256, Salt)
                                          │
                                          ▼
                            <kürzel>/<report>.html (verschlüsselt)  ──git push──►  GitHub Pages (HTTPS)
```

- **Ein Report = eine self-contained HTML-Datei** (Daten eingebettet, Charts via
  CDN). Funktioniert offline, nichts wird nachgeladen ausser Schrift/Chart.js.
- **StatiCrypt** verschlüsselt die Datei und ersetzt sie durch eine Login-Seite
  im Zimmer-4-Design (`staticrypt-template.html`). Passwort = pro Mandant.
- **„Remember 7 Tage":** Nach einmaligem Login öffnen sich alle weiteren Reports
  desselben Mandanten ohne erneute Passworteingabe (gleicher Salt + Passwort).

---

## 2. Ordnerstruktur

```
zimmer-4.github.io/
├── _src/                      # NICHT in Git — unverschlüsselte Quell-Reports
│   └── zgg/{index,cockpit-2026-05,er-2026-05}.html
├── zgg/                       # verschlüsselt (öffentlich, aber unlesbar)
│   ├── index.html             #   Login → Berichtsauswahl
│   ├── cockpit-2026-05.html   #   Erfolgs-Cockpit (Dashboard)
│   └── er-2026-05.html        #   Monatsvergleich Erfolgsrechnung
├── kon/index.html             # Platzhalter „in Vorbereitung" (öffentlich)
├── kas/index.html             # Platzhalter „in Vorbereitung" (öffentlich)
├── staticrypt-template.html   # Login-Design (Mandantenname via Flag)
├── tools/check_safe.py        # Security-Gate vor jedem Push
├── index.html                 # Landing Page
├── passwords.env              # NICHT in Git — Mandanten-Passwörter
├── .staticrypt.json           # Salt (öffentlich, kein Geheimnis)
├── .gitignore  .nojekyll
└── README.md  TODO.md
```

## 3. Namenskonvention

| Typ | Dateiname | Beispiel |
|---|---|---|
| Cockpit Dashboard | `cockpit-YYYY-MM.html` | `cockpit-2026-05.html` |
| Monatsvergleich ER | `er-YYYY-MM.html` | `er-2026-05.html` |
| Berichtsauswahl (Login) | `index.html` | verschlüsselt |

> **Regel:** Die Berichtsauswahl (`_src/<kürzel>/index.html`) verlinkt **nur real
> vorhandene** Reports. Kein Eintrag für etwas, das noch nicht generiert wurde.

---

## 4. Publish-Workflow (neuer Monat für bestehenden Mandanten)

Generatoren liegen im Projekt
`…/Claude/Projects/Financial Statement/` (Excel-Quelle + `build_*.py`).

```bash
# 0) Voraussetzung einmalig: PATH für node/staticrypt aktiv (siehe Setup unten)

# 1) Reports aus der fertigen Mandanten-Excel erzeugen → in _src/<kürzel>/
cd ".../Financial Statement"
python build_dashboard.py "<Mandant>_..._v10_KPI.xlsx" ".../reporting/_src/<kürzel>/cockpit-2026-06.html" "<Mandantenname>"
python build_er_html.py    "<Mandant>_..._v10_KPI.xlsx" ".../reporting/_src/<kürzel>/er-2026-06.html"      "<Mandantenname>"

# 2) Verschlüsseln → in den Mandantenordner (Passwort aus passwords.env, NICHT hier eintippen)
cd ".../reporting"
staticrypt _src/<kürzel>/cockpit-2026-06.html --password "$KÜRZEL_PASSWORD" --directory <kürzel> \
  --short --remember 7 --template staticrypt-template.html \
  --template-title "Zimmer 4 · Finanz-Reporting" \
  --template-button "Berichte öffnen" --template-placeholder "Passwort" \
  --template-error "Falsches Passwort. Bitte erneut versuchen." --template-remember "Passwort merken (7 Tage)"
# (dito für er-2026-06.html)

# 3) Berichtsauswahl _src/zgg/index.html um die neuen Zeilen ergänzen, dann
#    index.html ebenfalls neu verschlüsseln (gleicher staticrypt-Aufruf, --directory zgg)

# 4) Sicherheits-Check + Push
python tools/check_safe.py            # muss „OK ✓" liefern
git add zgg/ kon/ kas/ index.html staticrypt-template.html tools/ README.md robots.txt .gitignore .nojekyll .staticrypt.json
git status                            # gegenprüfen: KEIN _src/, KEIN passwords.env
git commit -m "ZGG Reports 2026-06"
git push
```

> ⚠️ Der **Salt** in `.staticrypt.json` muss konstant bleiben — sonst gilt die
> 7-Tage-Anmeldung nicht mehr über alle Dateien hinweg.

## 5. Neuer Mandant

1. Mandanten-Excel erzeugen (`build_report.py` im Financial-Statement-Projekt,
   siehe `SETUP_Neuer_Mandant.md` dort).
2. `_src/<kürzel>/` anlegen, Reports generieren (Schritt 1 oben).
3. Passwort in `passwords.env` ergänzen (`<KÜRZEL>_PASSWORD=...`).
4. Berichtsauswahl `_src/<kürzel>/index.html` erstellen (vorhandene ZGG als Vorlage).
5. Verschlüsseln + pushen (Schritt 2–4 oben).

Aktuelle Mandanten-Kürzel: **zgg**, **kon**, **kas**. Die Klarnamen werden bewusst
NICHT im (öffentlichen) Repo geführt — die Zuordnung Kürzel→Mandant bleibt lokal.

---

## 6. Sicherheit

- **Öffentliches Repo, aber nur verschlüsselte Inhalte.** Reports sind AES-256 und
  ohne Passwort nur StatiCrypt-Kauderwelsch. Dateinamen sind neutral.
- **`passwords.env` und `_src/` sind in `.gitignore`** — Passwörter und
  unverschlüsselte Reports verlassen den lokalen Rechner nie.
- **`tools/check_safe.py` vor jedem Push ausführen** — blockiert, falls ein Report
  unverschlüsselt oder ein Geheimnis im Staging wäre.
- **HTTPS** über GitHub Pages; „Remember" speichert nur den Passphrase-Hash lokal.
- Platzhalterseiten (KON/KAS, Landing) enthalten **keine** Finanzdaten und sind als
  `PUBLIC-PLACEHOLDER` markiert.

## 7. Setup (einmalig auf neuem Rechner)

- **Node.js** (für StatiCrypt): `winget install OpenJS.NodeJS.LTS`
- **StatiCrypt:** `npm install -g staticrypt`
- **GitHub CLI:** `winget install GitHub.cli` → `gh auth login`
- **Python 3** (für die Generatoren; nutzt nur Standard-Library + die `build_*.py`).
- PATH ggf. neu laden (neue PowerShell-Session).
