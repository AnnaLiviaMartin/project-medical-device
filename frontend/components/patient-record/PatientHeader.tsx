import Link from "next/link";
import styles from "./patientRecord.module.css";
import type { Patient } from "./patientRecord.data";
import { getStatusLabel } from "./patientRecord.data";

type PatientHeaderProps = {
  patient: Patient;
};

export default function PatientHeader({ patient }: PatientHeaderProps) {
  return (
    <>

      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>Patient Record</p>
          <h1 className={styles.title}>{patient.name}</h1>
          <p className={styles.subtitle}>
            Complete patient information, treatment history, medications, and scan access.
          </p>
        </div>

        <div className={styles.heroMeta}>
          <span
            className={`${styles.badge} ${
              patient.status === "Outpatient"
                ? styles.statusStable
                : styles.statusObservation
            }`}
          >
            {patient.status}
          </span>
        </div>
      </section>
    </>
  );
}