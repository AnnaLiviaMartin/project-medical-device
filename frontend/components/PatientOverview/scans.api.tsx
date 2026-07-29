import type { Patient } from "../patient-record/patientRecord.data";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

export async function fetchPatients(): Promise<Patient[]> {
  const res = await fetch(`${BASE_URL}/api/patients/`);
  if (!res.ok) throw new Error(`Fehler beim Laden der Patienten: ${res.status}`);
  return res.json();
}

export async function fetchPatientById(id: string): Promise<Patient> {
  const res = await fetch(`${BASE_URL}/api/patients/${id}/`);
  if (!res.ok) throw new Error(`Fehler beim Laden des Patienten: ${res.status}`);
  return res.json();
}