import styles from "./patientRecord.module.css";
import type { Patient } from "./patientRecord.data";

type PatientContactCardProps = {
  patient: Patient;
};

export default function PatientContactCard({
  patient,
}: PatientContactCardProps) {
  return (
    <div className={styles.panel}>
      <p className={styles.sectionLabel}>Address & Contact</p>
      <div className={styles.stack}>
        <InfoRow
          label="Address"
          value={`${patient.address.street}, ${patient.address.zip} ${patient.address.city}`}
        />
        <InfoRow
          label="Emergency Contact"
          value={`${patient.emergencyContact.name} · ${patient.emergencyContact.relation} · ${patient.emergencyContact.phone}`}
        />
        <InfoRow
          label="Insurance"
          value={`${patient.insurance.provider} · ${patient.insurance.policyNumber}`}
        />
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