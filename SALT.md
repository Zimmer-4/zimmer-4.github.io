# StaticCrypt-Salt

Der Salt liegt **nicht** in diesem Repo, sondern im Projektordner:

```
Financial Statement\.staticrypt.json
```

`_tools/publish.py` liest ihn dort und übergibt ihn StaticCrypt ausdrücklich
per `--salt`.

## Warum das wichtig ist

Ohne ausdrückliche Angabe sucht StaticCrypt sich selbst eine `.staticrypt.json`
im aktuellen Arbeitsverzeichnis — und **erzeugt einen neuen Zufallssalt**, wenn
dort keine liegt. Damit würden alle gespeicherten Anmeldungen der Mandanten
("Angemeldet bleiben", 7 Tage) auf einen Schlag ungültig.

Früher lag hier eine zweite `.staticrypt.json` mit einem abweichenden Wert. Sie
wurde nie verwendet, hat aber den Eindruck erweckt, sie sei massgeblich. Deshalb
ist sie entfernt: es soll nur **eine** Quelle geben.

## Falls der Salt verloren geht

Bereits veröffentlichte Dateien funktionieren weiter — jede trägt ihren Salt in
sich. Nur die gespeicherten Anmeldungen brechen, und die Mandanten müssen das
Passwort einmal neu eingeben. Kein Datenverlust, aber vermeidbarer Ärger.
