import type { Patient } from "./patientRecord.data";

export type NewPatientInput = Omit<Patient, "id">;

export async function createPatient(input: NewPatientInput): Promise<Patient> {
  const res = await fetch("/api/patients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });

  if (!res.ok) {
    throw new Error(`Patient konnte nicht angelegt werden: ${res.status}`);
  }

  return res.json();
}