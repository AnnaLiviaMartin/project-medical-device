import type { Scan } from "../patient-record/patientRecord.data";

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