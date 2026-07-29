import styles from "./patientRecord.module.css";
import type { Patient } from "./patientRecord.data";

type PatientInfoGridProps = {
  patient: Patient;
};

export default function PatientInfoGrid({ patient }: PatientInfoGridProps) {
  return (
    <div className={styles.panel}>
      <p className={styles.sectionLabel}>Patient Details</p>
      <div className={styles.infoGrid}>
        <InfoCard label="Patient ID" value={patient.id} />
        <InfoCard label="Age" value={`${patient.age} years`} />
        <InfoCard label="Gender" value={patient.gender} />
        <InfoCard label="Diagnosis" value={patient.diagnosis} />
        <InfoCard label="Doctor" value={patient.doctor} />
        <InfoCard label="Ward / Unit" value={patient.ward} />
        <InfoCard label="Last Visit" value={patient.lastVisit} />
        <InfoCard label="Next Appointment" value={patient.nextAppointment} />
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.infoCard}>
      <span className={styles.infoLabel}>{label}</span>
      <strong className={styles.infoValue}>{value}</strong>
    </div>
  );
}