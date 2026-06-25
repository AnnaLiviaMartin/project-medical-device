"use client";

import { useMemo, useState } from "react";
import styles from "./PatientOverview.module.css";

export type Patient = {
  id: string;
  name: string;
  age: number;
  gender: string;
  diagnosis: string;
  risk: "Niedrig" | "Mittel" | "Hoch";
  status: "Stabil" | "Beobachtung" | "Akut";
  lastVisit: string;
  nextAppointment: string;
  doctor: string;
  ward: string;
};

type PatientOverviewProps = {
  patients?: Patient[];
};

const defaultPatients: Patient[] = [
  {
    id: "P-1024",
    name: "Anna Becker",
    age: 47,
    gender: "w",
    diagnosis: "Hypertonie",
    risk: "Mittel",
    status: "Stabil",
    lastVisit: "21.06.2026",
    nextAppointment: "30.06.2026",
    doctor: "Dr. Klein",
    ward: "Ambulanz A",
  },
  {
    id: "P-1025",
    name: "Mehmet Yilmaz",
    age: 63,
    gender: "m",
    diagnosis: "Diabetes Typ II",
    risk: "Hoch",
    status: "Beobachtung",
    lastVisit: "24.06.2026",
    nextAppointment: "26.06.2026",
    doctor: "Dr. Schneider",
    ward: "Station 3",
  },
  {
    id: "P-1026",
    name: "Laura Schmidt",
    age: 31,
    gender: "w",
    diagnosis: "Asthma",
    risk: "Niedrig",
    status: "Stabil",
    lastVisit: "18.06.2026",
    nextAppointment: "05.07.2026",
    doctor: "Dr. Weber",
    ward: "Ambulanz B",
  },
  {
    id: "P-1027",
    name: "Jonas Hartmann",
    age: 56,
    gender: "m",
    diagnosis: "KHK-Verdacht",
    risk: "Hoch",
    status: "Akut",
    lastVisit: "25.06.2026",
    nextAppointment: "Heute 16:00",
    doctor: "Dr. Fischer",
    ward: "Notaufnahme",
  },
  {
    id: "P-1028",
    name: "Sofia Wagner",
    age: 72,
    gender: "w",
    diagnosis: "Postoperative Kontrolle",
    risk: "Mittel",
    status: "Beobachtung",
    lastVisit: "23.06.2026",
    nextAppointment: "27.06.2026",
    doctor: "Dr. Braun",
    ward: "Station 1",
  },
];

export default function PatientOverview({ patients = defaultPatients }: PatientOverviewProps) {
  const [query, setQuery] = useState("");
  const [riskFilter, setRiskFilter] = useState<"Alle" | Patient["risk"]>("Alle");
  const [selectedPatientId, setSelectedPatientId] = useState<string>(patients[0]?.id ?? "");

  const filteredPatients = useMemo(() => {
    return patients.filter((patient) => {
      const matchesQuery =
        patient.name.toLowerCase().includes(query.toLowerCase()) ||
        patient.id.toLowerCase().includes(query.toLowerCase()) ||
        patient.diagnosis.toLowerCase().includes(query.toLowerCase());

      const matchesRisk = riskFilter === "Alle" || patient.risk === riskFilter;
      return matchesQuery && matchesRisk;
    });
  }, [patients, query, riskFilter]);

  const selectedPatient =
    filteredPatients.find((patient) => patient.id === selectedPatientId) ??
    filteredPatients[0] ??
    null;

  const totalCount = patients.length;
  const highRiskCount = patients.filter((patient) => patient.risk === "Hoch").length;
  const observationCount = patients.filter((patient) => patient.status === "Beobachtung").length;
  const acuteCount = patients.filter((patient) => patient.status === "Akut").length;

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <div className={styles.headerContent}>
          <p className={styles.eyebrow}>Patientenmanagement</p>
          <h1 className={styles.title}>Patientenübersicht</h1>
          <p className={styles.subtitle}>
            Überblick über Status, Risiken, letzte Kontakte und nächste Maßnahmen.
          </p>
        </div>

        <button className={styles.primaryButton}>+ Neuer Patient</button>
      </section>

      <section className={styles.kpiGrid}>
        <StatCard label="Gesamt" value={String(totalCount)} hint="aktive Einträge" />
        <StatCard label="Hohes Risiko" value={String(highRiskCount)} hint="benötigen Priorisierung" danger />
        <StatCard label="Beobachtung" value={String(observationCount)} hint="mit laufender Nachverfolgung" />
        <StatCard label="Akut" value={String(acuteCount)} hint="sofortige Aufmerksamkeit" danger />
      </section>

      <section className={styles.contentGrid}>
        <div className={styles.leftColumn}>
          <div className={styles.panel}>
            <div className={styles.toolbar}>
              <input
                className={styles.searchInput}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Suche nach Name, ID oder Diagnose"
              />

              <select
                className={styles.select}
                value={riskFilter}
                onChange={(event) => setRiskFilter(event.target.value as "Alle" | Patient["risk"])}
              >
                <option value="Alle">Alle Risiken</option>
                <option value="Niedrig">Niedrig</option>
                <option value="Mittel">Mittel</option>
                <option value="Hoch">Hoch</option>
              </select>
            </div>

            <div className={styles.tableHeader}>
              <span>Patient</span>
              <span>Diagnose</span>
              <span>Status</span>
              <span>Nächster Termin</span>
            </div>

            <div className={styles.list}>
              {filteredPatients.map((patient) => {
                const active = patient.id === selectedPatient?.id;

                return (
                  <button
                    key={patient.id}
                    type="button"
                    className={`${styles.row} ${active ? styles.rowActive : ""}`}
                    onClick={() => setSelectedPatientId(patient.id)}
                  >
                    <div className={styles.nameBlock}>
                      <div className={styles.nameRow}>
                        <strong className={styles.patientName}>{patient.name}</strong>
                        <span className={styles.idBadge}>{patient.id}</span>
                      </div>
                      <span className={styles.metaText}>
                        {patient.age} Jahre · {patient.gender} · {patient.ward}
                      </span>
                    </div>

                    <span className={styles.cellText}>{patient.diagnosis}</span>
                    <span className={`${styles.statusBadge} ${getStatusClass(patient.status)}`}>
                      {patient.status}
                    </span>
                    <span className={styles.cellText}>{patient.nextAppointment}</span>
                  </button>
                );
              })}

              {filteredPatients.length === 0 && (
                <div className={styles.emptyState}>Keine Patient:innen für diese Suche gefunden.</div>
              )}
            </div>
          </div>
        </div>

        <aside className={styles.rightColumn}>
          <div className={styles.panel}>
            {selectedPatient ? (
              <>
                <div className={styles.detailTop}>
                  <div>
                    <p className={styles.eyebrow}>Ausgewählter Datensatz</p>
                    <h2 className={styles.detailName}>{selectedPatient.name}</h2>
                    <p className={styles.subtitleSmall}>
                      {selectedPatient.id} · behandelnde Ärztin / behandelnder Arzt: {selectedPatient.doctor}
                    </p>
                  </div>

                  <span className={`${styles.riskBadge} ${getRiskClass(selectedPatient.risk)}`}>
                    Risiko: {selectedPatient.risk}
                  </span>
                </div>

                <div className={styles.detailGrid}>
                  <DetailCard label="Diagnose" value={selectedPatient.diagnosis} />
                  <DetailCard label="Status" value={selectedPatient.status} />
                  <DetailCard label="Letzter Besuch" value={selectedPatient.lastVisit} />
                  <DetailCard label="Nächster Termin" value={selectedPatient.nextAppointment} />
                  <DetailCard label="Station / Bereich" value={selectedPatient.ward} />
                  <DetailCard label="Zuständig" value={selectedPatient.doctor} />
                </div>

                <div className={styles.notesCard}>
                  <p className={styles.sectionLabel}>Kurznotiz</p>
                  <p className={styles.noteText}>
                    Patient befindet sich aktuell in {selectedPatient.status.toLowerCase()} mit {selectedPatient.risk.toLowerCase()}em
                    Risikoprofil. Empfohlen wird die strukturierte Nachverfolgung vor dem Termin am {selectedPatient.nextAppointment}.
                  </p>
                </div>

                <div className={styles.actionRow}>
                  <button type="button" className={styles.primaryButtonFull}>Akte öffnen</button>
                  <button type="button" className={styles.secondaryButton}>Termin anpassen</button>
                  <button type="button" className={styles.secondaryButton}>Nachricht senden</button>
                </div>
              </>
            ) : (
              <div className={styles.emptyState}>Bitte eine Person aus der Liste auswählen.</div>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function StatCard({
  label,
  value,
  hint,
  danger = false,
}: {
  label: string;
  value: string;
  hint: string;
  danger?: boolean;
}) {
  return (
    <div className={styles.kpiCard}>
      <span className={styles.kpiLabel}>{label}</span>
      <strong className={`${styles.kpiValue} ${danger ? styles.kpiValueDanger : ""}`}>{value}</strong>
      <span className={styles.kpiHint}>{hint}</span>
    </div>
  );
}

function DetailCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.detailCard}>
      <span className={styles.detailLabel}>{label}</span>
      <strong className={styles.detailValue}>{value}</strong>
    </div>
  );
}

function getRiskClass(risk: Patient["risk"]) {
  if (risk === "Hoch") return styles.riskHigh;
  if (risk === "Mittel") return styles.riskMedium;
  return styles.riskLow;
}

function getStatusClass(status: Patient["status"]) {
  if (status === "Akut") return styles.statusAcute;
  if (status === "Beobachtung") return styles.statusObservation;
  return styles.statusStable;
}