** Magic the Gathering Desktop App**

Ziel: Eine funktionierende App, mit welcher 2 Spieler, welche sich an dem selben Rechner befinden, in dem Spiel "Magic the Gathering" gegeneinander antreten können. Die beiden Kontrahenten haben vor Spielbeginn die Möglichkeit ihr jeweils individuelles Deck zusammen zu stellen. Das Format des Spiels soll ein "Constructed Format" sein.
Die offiziellen Regeln von "Magic the Gathring" sollen vollständig implementiert sein. Diese befinden sich im Projectverzeichnis ("C:\\Users\\tombe\\PycharmProjects\\magic_tg_desktop_app") als "mtc_comprehensive_rules.txt".
Umsetzung:
Python: Pyside6 für das Interface
PonyORM für Datenenbank-Mapping
SQLite für Spieler mit Stats und Kartedaten etc. (Kartendaten referenzieren Images in einem Cards_Ordner.)
