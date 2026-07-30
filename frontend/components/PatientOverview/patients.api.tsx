import type { Patient, HistoryEntry } from "../patient-record/patientRecord.data";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchPatients(): Promise<Patient[]> {
  const res = await fetch(`${BASE_URL}/api/patients/`);
  if (!res.ok) throw new Error(`Error loading patients: ${res.status}`);
  return res.json();
}

export async function fetchPatientById(id: string): Promise<Patient> {
  const res = await fetch(`${BASE_URL}/api/patients/${id}/`);
  if (!res.ok) throw new Error(`Error loading the patient: ${res.status}`);
  return res.json();
}

export async function fetchHistoryByPatient(patientId: string): Promise<HistoryEntry[]> {
  const res = await fetch(`${BASE_URL}/api/history/?patient=${patientId}`);
  if (!res.ok) throw new Error(`Error loading history: ${res.status}`);
  return res.json();
}

export async function createPatient(payload: Record<string, unknown>): Promise<Patient> {
  const res = await fetch(`${BASE_URL}/api/patients/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    const message = errorBody
      ? Object.entries(errorBody)
          .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`)
          .join(" | ")
      : `Error creating patient: ${res.status}`;
    throw new Error(message);
  }

  return res.json();
}