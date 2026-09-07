# Zulassung als Medizinprodukt
- unterschiedliche Phasen: 
      1) wissenschaftliche Phase, 
      2) Entwicklungsphase beim Hersteller, (MDR) -> Produktentwicklung, Zulassung, Produktion
      3) Betriebsphase durch Anbieter (MDR) -> Inbetriebnahme, Betrieb

# Akteure
- MDR mit EU
- Bundesinstitut für Arzneimittel und Medizinprodukte (BfArM): Genehmigung von klinischen Prüfungen sowie der Risikoüberwachung von Medizinprodukten verantwortlich
- Deutsche Institut für Medizinische Dokumentation und Information (DIMDI): Informationssystem über alle in Deutschland zugelassenen Medizinprodukte und deren Hersteller
- Zentralstelle der Länder für Gesundheitsschutz bei Arzneimittel und Medizinprodukten (ZLG): Benennung und Überwachung von Benannten Stellen in Deutschland zuständig

# Definitionen
1. Medizinprodukt: Art. 2, 1.
-> zeigt dass Software ein Medizinprodukt sein kann (sofern die Kriterien erfüllt sind).
-> zur Bestimmung, ob die Software unter die Definition fällt wird eine Zweckbestimmung benötigt
2. Zweckbestimmung: Art. 2, 12.
-> „Verwendung, für die ein Produkt entsprechend den Angaben des Herstellers auf der Kennzeichnung, in der Gebrauchsanweisung oder dem Werbe- oder Verkaufsmaterial beziehungsweise den Werbe- oder Verkaufsangaben und seinen Angaben bei der klinischen Bewertung bestimmt ist.
3. Klassifizierung: Art. 51 "Klassifizierung von Produkten" gemäß Anhang VIII, Kapitel 3
-> Kapitel 2: "Die Anwendung der Klassifizierungsregeln richtet sich nach der Zweckbestimmung der Produkte."
4. aktive Medizinprodukte:
-> Software ist ein aktives Medizinprodukt, da zum Betreiben eine aktive Hardware benötigt wird
5. Unique Device Identification: eindeutigen Kennung für Medizinprodukte
6. Usability
-> Usability beziehungsweise Gebrauchstauglichkeit ist definiert als das Ausmaß, in dem ein System, ein Produkt oder eine Dienstleistung durch bestimmte Benutzer in einem bestimmten Nutzungskontext genutzt werden können, um festgelegte Ziele effektiv, effizient und zufriedenstellend zu erreichen. Effektivität ist dabei die Genauigkeit und Vollständigkeit, mit denen Benutzer bestimmte Ziele erreichen. Effizienz bezeichnet dabei die im Verhältnis zu den erreichten Ergebnissen eingesetzten Ressourcen. (Quelle: ISO 9241)

# Softwarespezifisches
- Software unterscheidet sich von physikalischen Produkten: immateriell, nicht produkziert, keine direkte Gefährdung durch Software, (Software-)Fehler sind systematisch, haben höhere Änderungsfrequenz, komplexer 

# Medical Device Regulation (MDR)
- Basis für Zulassung von Medizinprodukten in EU
- Abdeckung Entwicklung + Betriebsphase
- Zulassungsschritte:
      - klare Definition der Zweckbestimmung
      - Entscheidung, ob das Produkt in den Geltungsbereich der MDR fällt
      - wenn ja, Klassifizierung des Produkts
      - Durchführung eines Konformitätsbewertungsverfahrens
      - Ausstellung einer Konformitätserklärung durch den Hersteller
      - Anbringen des CE-Zeichens
      - Inverkehrbringen des Medizinprodukts
- "MDR verweist auf die Anwendung harmonisierter Normen. Werden diese angewendet und erfüllt, wird die Konformität mit der MDR angenommen. Normen machen konkretere Umsetzungsvorgaben der oft abstrakten rechtlichen Forderungen."

# Zweckbestimmung
- etwas 1 DIN A4 Seite
- initiale Einstufung als Medizinprodukt, für darauffolgende Klassifizierung/Risikobewertung/klinische Bewertung/Usability-Bewertung Grundlage
- Wir: Überwachung und Prognose wird durch unsere KI ermöglicht. Daher ist die Software ein Medizinprodukt -> Dient die Software zur reinen Speicherung oder Kommunikation von Daten, ist diese nicht als Medizinprodukt einzustufen, das ist bei uns aber nicht der Fall -> Enthält die Zweckbestimmung Begriffe wie alarmieren, analysieren, berechnen, detektieren, diagnostizieren, interpretieren, konvertieren, messen, steuern, überwachen, verstärken, kann davon ausgegangen werden, dass die Software ein Medizinprodukt darstellt. -> wichtig ist die konkrete Verwendung
- Wir: Patientenakte, Historie, Medikation, Allergien, DSGVO-Seiten → wahrscheinlich kein Medizinprodukt (reine Verwaltung/Dokumentation).
- Wir: ml-service + MlAnalysisService/RestMlAnalysisService → das ist der kritische Teil. Software wird laut BfArM als Medizinprodukt gewertet, wenn sie medizinische Wissensdatenbanken und Algorithmen mit patientenspezifischen Daten kombiniert und dazu bestimmt ist, medizinischem Fachpersonal Empfehlungen zur Diagnose, Prognose, Überwachung oder Behandlung eines einzelnen Patienten zu gebe

# Klassifizierung für Medizinprodukte
- erfolgt risikobasiert
- 4 Klassen: I, IIa, IIb, III
- Einstufung auf Basis von 22 Regeln
- Wir: fallen in IIa, IIb oder III, je nachdem wie streng man Regel 11 aulegen möchte: III ist es dann, wenn "Tod oder eine irreversible Verschlechterung des Gesundheitszustands einer Person", IIb wenn "eine schwerwiegende Verschlechterung des Gesundheitszustands einer Person", allgemein IIa wenn "Software, die dazu bestimmt ist, Informationen zu liefern, die zu Entscheidungen für diagnostische oder therapeutische Zwecke herangezogen werden"
- Wir: Einschätzung für ML-Modul: Mindestens Klasse IIa, mit guten Argumenten für Klasse IIb:
      - Die 14 Zielpathologien enthalten potenziell akut-lebensbedrohliche Befunde (z. B. Pneumothorax → kann eine notfallmäßige Drainage/chirurgische Intervention erfordern) und Befunde mit hoher Tragweite bei Fehlklassifikation (Mass/Nodule → Malignomverdacht, verzögerte Diagnose).
      - Die UI-Gestaltung ("AI Analysis Results", Ampel-Status, Confidence in %) suggeriert mehr als bloße "Information" – sie geht in Richtung "klinisches Management steuern", was bei kritischen Konstellationen bereits IIb auslöst.
      - Eine seriöse Zweckbestimmung müsste den ungünstigsten abgedeckten Fall mitdenken – ihr deckt mit einem einzigen Schwellenwert alle 14 Pathologien gleichzeitig ab, könnt euch also nicht auf die harmlosesten davon zurückziehen.

# Allgemeine Pflichten der Hersteller (unabhängig von Produktklasse)
- Art. 10
- verpflichten zu Forderungen: Risikomanagementsystem, klinische Bewertung, technische Dokumentation, Konformitätserklärung, eindeutige Bezeichner UDI, Qualitätsmangement, System zur ÜBerwachung nach Inverkehrbringen, Berücksichtigung der Amtssprache des Landes, Vigilanzsystem
- Dies definiert im Grund weitere zu folgende Normen:
      - Qualitätsmangementsystem nach ISO 13485 -> angewendet im Rahmen der Konformitätsbewertung
      - Konformitätsbewertungsverfahren nach Art. 52: Nachweis der Erfüllung der sogenannten Grundlegenden Sicherheits- und Leistungsanforderungen und damit der Nachweis über „Sicherheit und Leistungsfähigkeit“ des Medizinprodukts sowei der sonstigen allgemeinen Herstellerpflichten. -> um dies umzusetzen wird normalerweise ein zertifiziertes, vollständiges Qualitätsmanagementsystem (MDR, Anhang IX) angesetzt, welches die harmonisierte Norm ISO 13485 verwendet

# Grundlegenden Sicherheits- und Leistungsanforderungen (GSLA)
- Anhang I
- Nr. 14, 15, 17, 18, 22, 23 sind potenziell für Software interessant
- vom Hersteller einzuhalten und mittels technischer Dokumentation nachzuweisen.
- aufgeteilt in Allgemeine Anforderungen (GSLA 1–9), Anforderungen an Auslegung und Herstellung (GSLA 10–22) und Anforderungen an die vom Hersteller gelieferten Informationen (GSLA 23)
- u.a. 
      - GSLA 1: Nutzen > Risiken -> klinische Bewertung
      - GSLA 3 und 4 fordert ein Risikomanagementsystem
      - GSLA 5: sollen auch ergonomische Merkmale betrachtete werden sowie der Erfahrungsstand der Anwender, die Anwendungsumgebung berücksichtigt werden sollen. -> Forderung nach nutzerzentrierten Entwicklungsprozess bzw. der Betrachtung von Usability-Aspekten
      - 14.2: Der Hersteller hat festzulegen, ob eine Software allgemein freigegeben wird oder an eine bestimmte Hardware oder Laufzeitumgebung gebunden ist
      - 17.1: "Produkte in Form einer Software werden so ausgelegt, dass Wiederholbarkeit, Zuverlässigkeit und Leistung entsprechend ihrer bestimmungsgemäßen Verwendung gewährleistet sind"
      - 17.2: "bei Produkten in Form einer Software wird die Software entsprechend dem Stand der Technik entwickelt und hergestellt, wobei die Grundsätze des Software-Lebenszyklus, des Risikomanagements einschließlich der Informationssicherheit, der Verifizierung und der Validierung zu berücksichtigen sind." 
      -> Software-Lebenszyklus und Stand der Technik werden konkretisiert durch:
      -> IEC 82304-1 „Health software – Part 1: General requirements for product safety“: beinhaltet Spezifikation der Produktanforderungen, Produktvalidierung, Aktivitäten nach dem Inverkehrbringen sowie die zum Produkt gehörenden Kennzeichnungen und Begleitdokumente.
      -> IEC 62304 „Health software – Software life cycle processes“: Software-Lebenszyklus-Prozesse
      - 17.4.: "Die Hersteller legen Mindestanforderungen bezüglich Hardware, Eigenschaften von IT-Netzen und IT- Sicherheitsmaßnahmen einschließlich des Schutzes vor unbefugtem Zugriff fest, die für den bestimmungsgemäßen Einsatz der Software erforderlich sind"
      - GSLA 22.2: „Produkte zur Anwendung durch Laien werden so ausgelegt und hergestellt, dass – gewährleistet ist, dass das Produkt vom vorgesehenen Anwender – erforderlichenfalls nach angemessener Schulung und/oder Aufklärung – in allen Bedienungsphasen sicher und fehlerfrei verwendet werden kann,…. - das Risiko einer falschen Handhabung des Produkts oder gegebenenfalls einer falschen Interpretation der Ergebnisse durch den vorgesehenen Anwender so gering wie möglich gehalten wird.“ -> Buch befragt dazu einen Radiologen hinsichtlich Risiken in Bezug auf med. Software zur Befundung radiologische Bilddaten: „Die meisten Probleme sehen wir durch mangelnde Usability der Software. Die Software macht zwar alles richtig, aber durch die Vielzahl an Konfigurationsmöglichkeiten und Informationsdarstellung übersehen wir wichtige Dinge.“

# Risikomanagement
- harmonisierte Norm ISO 14971 „Anwendung des Risikomanagements auf Medizinprodukte“ konkretisiert Forderungen
- Wir: man müsste sich hier angucken -> Automatisierungsgrad, Konsistenz Doku/Default-Konfiguration/UI, Tranings-Validierungsdaten, Performance-Kennzahlen wie Threshold immer bei 0.7 (warum? validiert?), Sicherheitsklassen

# Klinische Bewertung
- klinischen Bewertung wird mittels klinischer Daten der klinische Nutzen des Produkts identifiziert

# Technische Dokumentation
- dadurch: Nachweis der Erfüllung der grundlegenden Sicherheits- und Leistungsanforderungen
- Anforderungen findbar in Anhang II „Technische Dokumentation“ und Anhang III „Technische Dokumentation über die Überwachung nach dem Inverkehrbringen“ -> dazu gehören Produktbescheibung und Spezifikation, Gebrauchsanweisung und Kennzeichnungen, Entwicklungsdokumente und Produktionsspezifikationen, Nachweis der Grundlegenden Sicherheits- und Leistungsanforderungen, Nutzen-Risiko-Analyse und Risikomanagement, Produktverifizierung, Produktvalidierung

# Vigilanzsystem
- MDR, Artikel 83–86 und Anhang III
- verpflichtende Einführung eines Systems zur Überwachung nach dem Inverkehrbringen (Post-Market Surveillance, PMS) ist eine weitere grundlegende Errungenschaft der MDR

# Prozessnormen
- beschreiben Anforderungen an Tätigkeiten bei der Durchführung eines Prozesses
- DIN EN ISO 13485 „Medizinprodukte – Qualitätsmanagementsysteme – Anforderungen für regulatorische Zwecke“ -> Hilfe bei der Validierung von Tools liefert der Technical Report ISO TR 80002-­2:2017, Medical device software – Part 2: Validation of software for medical device quality
- DIN EN 62366-1 „Medizinprodukte – Teil 1: Anwendung der Gebrauchstauglichkeit auf Medizinprodukte“ -> beschreibt gebrauchstauglichkeitsorientierten Entwicklungsprozess
- DIN EN 62304 „Medizingeräte-Software – Software-Lebenszyklus-Prozesse“
      - einzelne Forderungen nicht von allen Softwaren zu erfüllen -> abhängig von Sicherheitsklassen A, B oder C
      - Sicherheitsklasse A: keine Verletzung oder Schädigung der Gesundheit möglich
      - Sicherheitsklasse B: keine schwere Verletzung möglich
      - Sicherheitsklasse C: Tod oder schwere Verletzung möglich
      - siehe [Zusammenfassung der Anforderungen nach Sicherheitsklasse](./Tabelle1.png)
- DIN EN ISO 14971 „Medizinprodukte – Anwendung des Risikomanagements auf Medizinprodukte“ -> wird gefordert von DIN EN 62366-1
- DIN EN ISO 141-  „Klinische Prüfung von Medizinprodukten an Menschen – Gute klinische Praxis“
- Usability (DIN EN 62366)

# EU AI Act
- gilt als Hochrisiko-KI-System, Kapitel 3, Abschnitt II, Artikel 6
- Wir: Art. 6 Abs. 1 + Anhang I: KI-Systeme, die Sicherheitskomponente eines bereits regulierten Produkts sind oder selbst ein solches Produkt darstellen
- damit gelten spezielle Anforderungen, Kapitel 3, Abschnitt II, Artikel 8 -> Ausforumliert wird dies in Art. 9-15

# Beispiele von KI-Sytemen
- Viz.ai: automatisierte Bildanalyse mittels künstlicher Intelligenz, siehe viz.ai
- Arterys: automatisierte Bildanalyse mittels künstlicher Intelligenz, siehe arterys.­com

# Offene Fragen in Bezug auf KI
- Es stellt sich nun die Frage, ab wann eine trainierte Software eine neue, zulassungspflichtige Version darstellt. -> da dann die Reproduzierbarkeit und Wiederholbarkeit von Befunden nicht mehr gegeben ist
- Validierung von Tools nach ISO 13485 -> was fällt da alles drunter?