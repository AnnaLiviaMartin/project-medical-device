// Das Backend liefert Medien-Pfade (Roentgenbilder, Grad-CAM-Overlays,
// Attachments) bewusst als relative Pfade ("/media/...") statt als
// absolute URLs zurueck. Absolute URLs, gebaut aus dem Host-Header des
// jeweiligen Requests, waeren falsch: serverseitige Next.js-Requests
// laufen ueber eine andere Basis-URL (internes Docker-/Container-
// Netzwerk) als das, was der Browser erreichen kann (oeffentliche
// Backend-URL). Der Browser laedt Bilder aber IMMER selbst nach - daher
// wird hier zentral und ausschliesslich die oeffentliche
// NEXT_PUBLIC_API_URL angehaengt, unabhaengig davon, ob die JSON-Antwort
// server- oder clientseitig geholt wurde.
const PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function resolveMediaUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path; // schon absolut (z.B. externe URL)
  return `${PUBLIC_API_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}
