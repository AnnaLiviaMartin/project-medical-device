import styles from "./patientRecord.module.css";
import type { Patient } from "./patientRecord.data";

type PatientMedicationCardProps = {
  patient: Patient;
};

export default function PatientMedicationCard({
  patient,
}: PatientMedicationCardProps) {
  return (
    <div className={styles.panel}>
      <p className={styles.sectionLabel}>Current Medication</p>
      <div className={styles.stack}>
        {patient.medications.map((medication) => (
          <div key={medication.name} className={styles.listCard}>
            <strong className={styles.listCardTitle}>{medication.name}</strong>
            <p className={styles.listCardText}>
              {medication.dosage} · {medication.schedule}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}