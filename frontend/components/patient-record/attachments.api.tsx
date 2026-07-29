import type { Attachment } from "./patientRecord.data";

export async function uploadAttachment(
  patientId: string,
  entryId: string,
  file: File
): Promise<Attachment> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `/api/patients/${patientId}/history/${entryId}/attachments`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) {
    throw new Error(`Upload fehlgeschlagen: ${res.status}`);
  }

  return res.json();
}

export async function deleteAttachment(
  patientId: string,
  entryId: string,
  attachmentId: string
): Promise<void> {
  const res = await fetch(
    `/api/patients/${patientId}/history/${entryId}/attachments/${attachmentId}`,
    { method: "DELETE" }
  );

  if (!res.ok) {
    throw new Error(`Löschen fehlgeschlagen: ${res.status}`);
  }
}