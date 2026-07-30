import type { Scan } from "../patient-record/patientRecord.data";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function uploadXrayScan(
  patientId: string,
  entryId: string,
  file: File
): Promise<Scan> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `${BASE_URL}/api/patients/${patientId}/history/${entryId}/scans/`,
    { method: "POST", body: formData }
  );

  if (!res.ok) {
    throw new Error(`Roentgenaufnahme-Upload fehlgeschlagen: ${res.status}`);
  }
  return res.json();
}