import type { Scan } from "../patient-record/patientRecord.data";

export async function uploadXrayScan(
  patientId: string,
  entryId: string,
  file: File
): Promise<Scan> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `/api/patients/${patientId}/history/${entryId}/scans`,
    { method: "POST", body: formData }
  );

  if (!res.ok) {
    throw new Error(`Roentgenaufnahme-Upload fehlgeschlagen: ${res.status}`);
  }
  return res.json();
}