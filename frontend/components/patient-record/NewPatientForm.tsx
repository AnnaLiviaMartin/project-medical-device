"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./NewPatientForm.module.css";
import type { Gender, PatientStatus } from "./patientRecord.data";
import { createPatient } from "../PatientOverview/patients.api";

type MedicationRow = {
  name: string;
  dosage: string;
  schedule: string;
};

export default function NewPatientForm() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [gender, setGender] = useState<Gender>("female");
  const [diagnosis, setDiagnosis] = useState("");
  const [status, setStatus] = useState<PatientStatus>("Outpatient");
  const [lastVisit, setLastVisit] = useState("");
  const [nextAppointment, setNextAppointment] = useState("");
  const [doctor, setDoctor] = useState("");
  const [ward, setWard] = useState("");

  const [street, setStreet] = useState("");
  const [zip, setZip] = useState("");
  const [city, setCity] = useState("");

  const [contactName, setContactName] = useState("");
  const [contactRelation, setContactRelation] = useState("");
  const [contactPhone, setContactPhone] = useState("");

  const [insuranceProvider, setInsuranceProvider] = useState("");
  const [policyNumber, setPolicyNumber] = useState("");

  const [allergyInput, setAllergyInput] = useState("");
  const [allergies, setAllergies] = useState<string[]>([]);

  const [medications, setMedications] = useState<MedicationRow[]>([]);

  const [bloodPressure, setBloodPressure] = useState("");
  const [heartRate, setHeartRate] = useState("");
  const [oxygenSaturation, setOxygenSaturation] = useState("");
  const [temperature, setTemperature] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function addAllergy() {
    const trimmed = allergyInput.trim();
    if (!trimmed) return;
    setAllergies((prev) => prev.concat([trimmed]));
    setAllergyInput("");
  }

  function removeAllergy(index: number) {
    setAllergies((prev) => prev.filter((_, i) => i !== index));
  }

  function addMedicationRow() {
    setMedications((prev) =>
      prev.concat([{ name: "", dosage: "", schedule: "" }])
    );
  }

  function updateMedicationRow(
    index: number,
    field: keyof MedicationRow,
    value: string
  ) {
    setMedications((prev) =>
      prev.map((row, i) => (i === index ? { ...row, [field]: value } : row))
    );
  }

  function removeMedicationRow(index: number) {
    setMedications((prev) => prev.filter((_, i) => i !== index));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!name.trim() || !dateOfBirth || !lastVisit || !diagnosis.trim() || !doctor.trim()) {
      setError("Please provide at least your name, date of birth, last visit date, diagnosis, and doctor's name.");
      return;
    }

    const [firstName, ...rest] = name.trim().split(" ");
    const lastName = rest.join(" ") || firstName;

    setIsSubmitting(true);
    try {
      const created = await createPatient({
        first_name: firstName,
        last_name: lastName,
        date_of_birth: dateOfBirth,
        sex: gender,
        diagnosis: diagnosis.trim(),
        status,
        last_visit: lastVisit,
        next_appointment: nextAppointment || null,
        doctor: doctor.trim(),
        ward: ward.trim(),
        address_street: street.trim(),
        address_zip: zip.trim(),
        address_city: city.trim(),
        emergency_contact_name: contactName.trim(),
        emergency_contact_relation: contactRelation.trim(),
        emergency_contact_phone: contactPhone.trim(),
        insurance_provider: insuranceProvider.trim(),
        insurance_policy_number: policyNumber.trim(),
        vitals_blood_pressure: bloodPressure.trim(),
        vitals_heart_rate: heartRate.trim(),
        vitals_oxygen_saturation: oxygenSaturation.trim(),
        vitals_temperature: temperature.trim(),
        allergies,
        medications,
      });

      router.push(`/patients/${created.id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Patient konnte nicht angelegt werden."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      {error ? <p className={styles.errorBanner}>{error}</p> : null}

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Basic Information</h2>
        <div className={styles.grid}>
          <Field label="Full Name" required>
            <input
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Anna Becker"
            />
          </Field>

          <Field label="Date of Birth" required>
            <input
              type="date"
              className={styles.input}
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
            />
          </Field>

          <Field label="Gender">
            <select
              className={styles.select}
              value={gender}
              onChange={(e) => setGender(e.target.value as Gender)}
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="diverse">Diverse</option>
            </select>
          </Field>

          <Field label="Status">
            <select
              className={styles.select}
              value={status}
              onChange={(e) => setStatus(e.target.value as PatientStatus)}
            >
              <option value="Outpatient">Outpatient</option>
              <option value="Inpatient">Inpatient</option>
            </select>
          </Field>

          <Field label="Diagnosis" required>
            <input
              className={styles.input}
              value={diagnosis}
              onChange={(e) => setDiagnosis(e.target.value)}
              placeholder="e.g. Hypertension"
            />
          </Field>

          <Field label="Attending Doctor" required>
            <input
              className={styles.input}
              value={doctor}
              onChange={(e) => setDoctor(e.target.value)}
              placeholder="e.g. Dr. Klein"
            />
          </Field>

          <Field label="Ward / Unit">
            <input
              className={styles.input}
              value={ward}
              onChange={(e) => setWard(e.target.value)}
              placeholder="e.g. Ward 3"
            />
          </Field>

          <Field label="Last Visit">
            <input
              type="date"
              className={styles.input}
              value={lastVisit}
              onChange={(e) => setLastVisit(e.target.value)}
            />
          </Field>

          <Field label="Next Appointment">
            <input
              type="date"
              className={styles.input}
              value={nextAppointment}
              onChange={(e) => setNextAppointment(e.target.value)}
            />
          </Field>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Address</h2>
        <div className={styles.grid}>
          <Field label="Street">
            <input
              className={styles.input}
              value={street}
              onChange={(e) => setStreet(e.target.value)}
            />
          </Field>
          <Field label="ZIP Code">
            <input
              className={styles.input}
              value={zip}
              onChange={(e) => setZip(e.target.value)}
            />
          </Field>
          <Field label="City">
            <input
              className={styles.input}
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </Field>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Emergency Contact</h2>
        <div className={styles.grid}>
          <Field label="Name">
            <input
              className={styles.input}
              value={contactName}
              onChange={(e) => setContactName(e.target.value)}
            />
          </Field>
          <Field label="Relation">
            <input
              className={styles.input}
              value={contactRelation}
              onChange={(e) => setContactRelation(e.target.value)}
              placeholder="e.g. Spouse"
            />
          </Field>
          <Field label="Phone">
            <input
              className={styles.input}
              value={contactPhone}
              onChange={(e) => setContactPhone(e.target.value)}
              placeholder="+49 ..."
            />
          </Field>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Insurance</h2>
        <div className={styles.grid}>
          <Field label="Provider">
            <input
              className={styles.input}
              value={insuranceProvider}
              onChange={(e) => setInsuranceProvider(e.target.value)}
            />
          </Field>
          <Field label="Policy Number">
            <input
              className={styles.input}
              value={policyNumber}
              onChange={(e) => setPolicyNumber(e.target.value)}
            />
          </Field>
        </div>
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Allergies</h2>
        <div className={styles.inlineAddRow}>
          <input
            className={styles.input}
            value={allergyInput}
            onChange={(e) => setAllergyInput(e.target.value)}
            placeholder="e.g. Penicillin"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addAllergy();
              }
            }}
          />
          <button
            type="button"
            className={styles.addButton}
            onClick={addAllergy}
          >
            + Add
          </button>
        </div>

        {allergies.length > 0 ? (
          <ul className={styles.tagList}>
            {allergies.map((allergy, index) => (
              <li key={`${allergy}-${index}`} className={styles.tag}>
                {allergy}
                <button
                  type="button"
                  className={styles.tagRemove}
                  onClick={() => removeAllergy(index)}
                  aria-label={`Remove ${allergy}`}
                >
                  x
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.emptyHint}>No allergies added yet.</p>
        )}
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeaderRow}>
          <h2 className={styles.sectionTitle}>Medications</h2>
          <button
            type="button"
            className={styles.addButton}
            onClick={addMedicationRow}
          >
            + Add Medication
          </button>
        </div>

        {medications.length === 0 ? (
          <p className={styles.emptyHint}>No medications added yet.</p>
        ) : (
          <div className={styles.medicationList}>
            {medications.map((row, index) => (
              <div key={index} className={styles.medicationRow}>
                <input
                  className={styles.input}
                  value={row.name}
                  onChange={(e) =>
                    updateMedicationRow(index, "name", e.target.value)
                  }
                  placeholder="Name (e.g. Metformin)"
                />
                <input
                  className={styles.input}
                  value={row.dosage}
                  onChange={(e) =>
                    updateMedicationRow(index, "dosage", e.target.value)
                  }
                  placeholder="Dosage (e.g. 1000 mg)"
                />
                <input
                  className={styles.input}
                  value={row.schedule}
                  onChange={(e) =>
                    updateMedicationRow(index, "schedule", e.target.value)
                  }
                  placeholder="Schedule (e.g. 2x daily)"
                />
                <button
                  type="button"
                  className={styles.rowRemoveButton}
                  onClick={() => removeMedicationRow(index)}
                  aria-label="Remove medication"
                >
                  x
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Vitals</h2>
        <div className={styles.grid}>
          <Field label="Blood Pressure">
            <input
              className={styles.input}
              value={bloodPressure}
              onChange={(e) => setBloodPressure(e.target.value)}
              placeholder="e.g. 120/80 mmHg"
            />
          </Field>
          <Field label="Heart Rate">
            <input
              className={styles.input}
              value={heartRate}
              onChange={(e) => setHeartRate(e.target.value)}
              placeholder="e.g. 72 bpm"
            />
          </Field>
          <Field label="Oxygen Saturation">
            <input
              className={styles.input}
              value={oxygenSaturation}
              onChange={(e) => setOxygenSaturation(e.target.value)}
              placeholder="e.g. 98%"
            />
          </Field>
          <Field label="Temperature">
            <input
              className={styles.input}
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              placeholder="e.g. 36.8°C"
            />
          </Field>
        </div>
      </section>

      <div className={styles.formActions}>
        <button
          type="button"
          className={styles.cancelButton}
          onClick={() => router.push("/")}
        >
          Cancel
        </button>
        <button
          type="submit"
          className={styles.submitButton}
          disabled={isSubmitting}
        >
          {isSubmitting ? "Saving..." : "Create Patient"}
        </button>
      </div>
    </form>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className={styles.field}>
      <span className={styles.fieldLabel}>
        {label}
        {required ? <span className={styles.requiredMark}> *</span> : null}
      </span>
      {children}
    </label>
  );
}