import type { Attachment, Scan } from "./patientRecord.data";

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

export type UploadKind = "scan" | "document";

export async function uploadAttachment(
  patientId: string,
  entryId: string,
  file: File
): Promise<Attachment> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `${BASE_URL}/api/patients/${patientId}/history/${entryId}/attachments/`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status}`);
  }

  return res.json();
}

export async function uploadScan(
  patientId: string,
  entryId: string,
  file: File
): Promise<Scan> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(
    `${BASE_URL}/api/patients/${patientId}/history/${entryId}/scans/`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!res.ok) {
    const errorBody = await res.json().catch(() => null);
    const message = errorBody?.detail ?? `Scan-Upload failed: ${res.status}`;
    throw new Error(message);
  }

  return res.json();
}

export async function deleteAttachment(
  patientId: string,
  entryId: string,
  attachmentId: string
): Promise<void> {
  const res = await fetch(
    `${BASE_URL}/api/patients/${patientId}/history/${entryId}/attachments/${attachmentId}/`,
    { method: "DELETE" }
  );

  if (!res.ok) {
    throw new Error(`Delete failed: ${res.status}`);
  }
}