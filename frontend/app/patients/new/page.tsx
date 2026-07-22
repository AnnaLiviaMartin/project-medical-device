import Link from "next/link";
import NewPatientForm from "../../../components/patient-record/NewPatientForm";
import styles from "./page.module.css";

export default function NewPatientPage() {
  return (
    <main className={styles.page}>
      <div className={styles.topBar}>
        <Link href="/patientmanagement" className={styles.backLink}>
          ← Back to Patient Overview
        </Link>
      </div>

      <section className={styles.hero}>
        <p className={styles.eyebrow}>Patient Management</p>
        <h1 className={styles.title}>New Patient</h1>
        <p className={styles.subtitle}>
          Enter the patient&apos;s master data, contacts, and clinical baseline information.
        </p>
      </section>

      <NewPatientForm />
    </main>
  );
}