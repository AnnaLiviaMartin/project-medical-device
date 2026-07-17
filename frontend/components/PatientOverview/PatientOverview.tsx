"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import styles from "./PatientOverview.module.css";
import {
  patients as defaultPatients,
  type Patient,
  type PatientStatus,
} from "components/patient-record/patientRecord.data";

type PatientOverviewProps = {
  patients?: Patient[];
  initialPatientId?: string;
};


export default function PatientOverview({
  patients = defaultPatients,
  initialPatientId,
}: PatientOverviewProps) {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"All" | PatientStatus>("All");
  const [selectedPatientId, setSelectedPatientId] = useState(() => {
    const matchedPatient = patients.find((patient) => patient.id === initialPatientId);
    return matchedPatient?.id ?? patients[0]?.id ?? "";
  });

  useEffect(() => {
    const matchedPatient = patients.find((patient) => patient.id === initialPatientId);

    if (matchedPatient) {
      setSelectedPatientId(matchedPatient.id);
      return;
    }

    setSelectedPatientId((currentSelectedId) => {
      const currentStillExists = patients.some(
        (patient) => patient.id === currentSelectedId
      );

      if (currentStillExists) return currentSelectedId;
      return patients[0]?.id ?? "";
    });
  }, [patients, initialPatientId]);

  const filteredPatients = useMemo(() => {
    return patients.filter((patient) => {
      const normalizedQuery = query.toLowerCase();

      const matchesQuery =
        patient.name.toLowerCase().includes(normalizedQuery) ||
        patient.id.toLowerCase().includes(normalizedQuery) ||
        patient.address.street.toLowerCase().includes(normalizedQuery) ||
        patient.address.city.toLowerCase().includes(normalizedQuery) ||
        patient.emergencyContact.name.toLowerCase().includes(normalizedQuery) ||
        patient.emergencyContact.phone.toLowerCase().includes(normalizedQuery);

      const matchesStatus =
        statusFilter === "All" || patient.status === statusFilter;

        return matchesQuery && matchesStatus;
    });
  }, [patients, query, statusFilter]);

  const selectedPatient =
    patients.find((patient) => patient.id === selectedPatientId) ?? null;

  return (
    <main className={styles.page}>
      <section className={styles.header}>
        <div className={styles.headerContent}>
          <p className={styles.eyebrow}>Patient Management</p>
          <h1 className={styles.title}>Patient Overview</h1>
          <p className={styles.subtitle}>
            Overview of master data, address information, and emergency contacts.
          </p>
        </div>

        <button className={styles.primaryButton}>+ New Patient</button>
      </section>

      <section className={styles.contentGrid}>
        <div className={styles.leftColumn}>
          <div className={styles.panel}>
            <div className={styles.toolbar}>
              <input
                className={styles.searchInput}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search by name, ID, city, or emergency contact"
              />

              <select
                className={styles.select}
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(event.target.value as "All" | PatientStatus)
                }
              >
                <option value="All">All</option>
                <option value="Inpatient">Inpatient</option>
                <option value="Outpatient">Outpatient</option>
              </select>
            </div>

            <div className={styles.tableHeader}>
              <span>Patient</span>
              <span>Address</span>
              <span>Emergency Contact</span>
            </div>

            <div className={styles.list}>
              {filteredPatients.map((patient) => {
                const active = patient.id === selectedPatientId;

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
                        <span
                          className={`${styles.statusBadge} ${getStatusClass(
                            patient.status
                          )}`}
                        >
                          {patient.status}
                        </span>
                      </div>
                      <span className={styles.metaText}>
                        {patient.age} years · {patient.gender}
                      </span>
                    </div>

                    <div className={styles.nameBlock}>
                      <strong className={styles.patientName}>
                        {patient.address.street}
                      </strong>
                      <span className={styles.metaText}>
                        {patient.address.zip} {patient.address.city}
                      </span>
                    </div>

                    <div className={styles.nameBlock}>
                      <strong className={styles.patientName}>
                        {patient.emergencyContact.name}
                      </strong>
                      <span className={styles.metaText}>
                        {patient.emergencyContact.relation} ·{" "}
                        {patient.emergencyContact.phone}
                      </span>
                    </div>
                  </button>
                );
              })}

              {filteredPatients.length === 0 && (
                <div className={styles.emptyState}>
                  No patients found for this search.
                </div>
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
                    <p className={styles.eyebrow}>Selected Record</p>
                    <h2 className={styles.detailName}>{selectedPatient.name}</h2>
                    <p className={styles.subtitleSmall}>
                      {selectedPatient.id} · attending physician:{" "}
                      {selectedPatient.doctor}
                    </p>
                  </div>

                  <div className={styles.badgeStack}>
                    <span
                      className={`${styles.statusBadge} ${getStatusClass(
                        selectedPatient.status
                      )}`}
                    >
                      {selectedPatient.status}
                    </span>
                  </div>
                </div>

                <div className={styles.detailGrid}>
                  <DetailCard label="Status" value={selectedPatient.status} />
                  <DetailCard
                    label="Last Visit"
                    value={selectedPatient.lastVisit}
                  />
                  <DetailCard
                    label="Next Appointment"
                    value={selectedPatient.nextAppointment}
                  />
                  <DetailCard
                    label="Ward / Unit"
                    value={selectedPatient.ward}
                  />
                  <DetailCard
                    label="Care Type"
                    value={selectedPatient.status}
                  />
                  <DetailCard
                    label="Address"
                    value={`${selectedPatient.address.street}, ${selectedPatient.address.zip} ${selectedPatient.address.city}`}
                  />
                  <DetailCard
                    label="Emergency Contact"
                    value={`${selectedPatient.emergencyContact.name} · ${selectedPatient.emergencyContact.relation} · ${selectedPatient.emergencyContact.phone}`}
                  />
                </div>

                <div className={styles.actionRow}>
                  <Link
                    href={`/patients/${selectedPatient.id}`}
                    className={styles.primaryButtonFullLink}
                  >
                    Open Record
                  </Link>
                </div>
              </>
            ) : (
              <div className={styles.emptyState}>
                Please select a person from the list.
              </div>
            )}
          </div>
        </aside>
      </section>
    </main>
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

function getStatusClass(status: Patient["status"]) {
  if (status === "Outpatient") return styles.statusStable;
  return styles.statusObservation;
}