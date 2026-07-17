import PatientContactCard from "../../../components/patient-record/PatientContactCard";
import PatientHeader from "../../../components/patient-record/PatientHeader";
import PatientHistoryTimeline from "../../../components/patient-record/PatientHistoryTimeline";
import PatientInfoGrid from "../../../components/patient-record/PatientInfoGrid";
import PatientMedicationCard from "../../../components/patient-record/PatientMedicationCard";
import PatientVitalsCard from "../../../components/patient-record/PatientVitalsCard";
import {
  patientHistory,
  patients,
} from "../../../components/patient-record/patientRecord.data";
import styles from "../../../components/patient-record/patientRecord.module.css";

type PageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function PatientRecordPage({ params }: PageProps) {
  const { id } = await params;
  const patient = patients.find((entry) => entry.id === id);

  if (!patient) {
    return (
      <main className={styles.page}>
        <div className={styles.panel}>
          <p className={styles.eyebrow}>Patient Record</p>
          <h1 className={styles.title}>Patient not found</h1>
          <p className={styles.subtitle}>
            No record is available for the selected patient ID.
          </p>
        </div>
      </main>
    );
  }

  const history = patientHistory[patient.id] ?? [];

  return (
    <main className={styles.page}>
      <PatientHeader patient={patient} />

      <section className={styles.overviewGrid}>
        <PatientInfoGrid patient={patient} />
        <PatientContactCard patient={patient} />
      </section>

      <section className={styles.contentGrid}>
        <div className={styles.mainColumn}>
          <PatientHistoryTimeline history={history} patientId={patient.id} />
        </div>

        <aside className={styles.sideColumn}>
          <PatientMedicationCard patient={patient} />
          <PatientVitalsCard patient={patient} />
        </aside>
      </section>
    </main>
  );
}