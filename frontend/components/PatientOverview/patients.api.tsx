import type { Patient, HistoryEntry } from "../patient-record/patientRecord.data";

// Serverseitig (SSR/Server Components, laeuft im Next.js-Container) und
// clientseitig (Browser) muessen unterschiedliche URLs verwenden: der
// Browser erreicht das Backend nur ueber die oeffentliche URL, der
// Next.js-Server dagegen laeuft im selben Docker-/Container-Apps-Netzwerk
// wie das Backend und sollte es intern ansprechen. INTERNAL_API_URL ist
// bewusst NICHT NEXT_PUBLIC_-praefixiert, damit es nie ins Client-Bundle
// gelangt und zur Laufzeit (ohne Rebuild) im Container gesetzt werden kann.
const BASE_URL =
  typeof window === "undefined"
    ? process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
    : process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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