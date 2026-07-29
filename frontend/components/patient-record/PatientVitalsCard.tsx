import styles from "./patientRecord.module.css";
import type { Patient } from "./patientRecord.data";

type PatientVitalsCardProps = {
  patient: Patient;
};

export default function PatientVitalsCard({ patient }: PatientVitalsCardProps) {
  return (
    <div className={styles.panel}>
      <p className={styles.sectionLabel}>Latest Vitals</p>
      <div className={styles.stack}>
        <InfoRow label="Blood Pressure" value={patient.vitals.bloodPressure} />
        <InfoRow label="Heart Rate" value={patient.vitals.heartRate} />
        <InfoRow
          label="Oxygen Saturation"
          value={patient.vitals.oxygenSaturation}
        />
        <InfoRow label="Temperature" value={patient.vitals.temperature} />
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.infoRow}>
      <span className={styles.infoRowLabel}>{label}</span>
      <span className={styles.infoRowValue}>{value}</span>
    </div>
  );
}