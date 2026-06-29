#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# Pre-Push Security-Gate für das Reporting-Portal
# ---------------------------------------------------------------------
# Prüft VOR jedem Push, dass keine unverschlüsselten Finanzdaten und
# keine Passwörter ins öffentliche Repo gelangen. Exit-Code != 0 = STOP.
#
# Regeln:
#  1. passwords.env / *.env darf NICHT im Git-Staging/Tracking sein.
#  2. _src/ darf NICHT getrackt sein (unverschlüsselte Quellen).
#  3. Jede getrackte HTML in einem Mandantenordner (zgg|kon|kas/...) muss
#     ENTWEDER StatiCrypt-verschlüsselt sein (enthält "staticrypt")
#     ODER explizit als "PUBLIC-PLACEHOLDER" markiert sein.
#  4. Report-Dateien (cockpit-*.html, er-*.html) MÜSSEN verschlüsselt sein.
#
# Aufruf:  python tools/check_safe.py        (im Repo-Root)
# =====================================================================
import subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANDANT_DIRS = ("zgg/", "kon/", "kas/")
REPORT_RE = re.compile(r"(^|/)(cockpit|er|ytd)-.*\.html$", re.I)

def tracked_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    return [f.strip() for f in out.stdout.splitlines() if f.strip()]

def staged_files():
    # --diff-filter=ACMR: nur Added/Copied/Modified/Renamed – KEINE Löschungen
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                         cwd=ROOT, capture_output=True, text=True)
    return [f.strip() for f in out.stdout.splitlines() if f.strip()]

def read(path):
    try:
        with open(os.path.join(ROOT, path), encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""

def main():
    errors = []
    files = set(tracked_files()) | set(staged_files())

    for f in sorted(files):
        # Nicht (mehr) vorhandene Dateien (z.B. gestagte Löschungen) überspringen
        if not os.path.exists(os.path.join(ROOT, f)):
            continue
        # 1./2. Geheimnisse & Quellen
        if f == "passwords.env" or f.endswith(".env"):
            errors.append(f"GEHEIMNIS getrackt: {f}")
        if f.startswith("_src/"):
            errors.append(f"UNVERSCHLÜSSELTE QUELLE getrackt: {f}")

        # 3./4. HTML in Mandantenordnern
        if f.lower().endswith(".html") and any(f.startswith(d) for d in MANDANT_DIRS):
            content = read(f)
            is_crypt = "staticrypt" in content.lower()
            is_placeholder = "PUBLIC-PLACEHOLDER" in content
            is_report = bool(REPORT_RE.search(f))
            if is_report and not is_crypt:
                errors.append(f"REPORT NICHT VERSCHLÜSSELT: {f}")
            elif not is_crypt and not is_placeholder:
                errors.append(f"KLARTEXT-HTML ohne Marker: {f} "
                              f"(verschlüsseln oder als PUBLIC-PLACEHOLDER markieren)")

    if errors:
        print("SECURITY-CHECK FEHLGESCHLAGEN:")
        for e in errors:
            print("  [FAIL] " + e)
        print(f"\n{len(errors)} Problem(e) - Push abbrechen und beheben.")
        sys.exit(1)

    print("SECURITY-CHECK OK")
    print(f"  {len(files)} getrackte/gestagte Dateien geprüft – keine Klartext-Finanzdaten, keine Geheimnisse.")
    sys.exit(0)

if __name__ == "__main__":
    main()
