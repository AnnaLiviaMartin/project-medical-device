import { notFound } from "next/navigation";
import AnalysisPageClient from "./AnalysisPageClient";
import { fetchPatientById } from "components/PatientOverview/patients.api";
import { fetchHistoryByPatient } from "components/PatientOverview/patients.api";

type PageProps = {
  params: Promise<{ id: string; entryId: string }>;
};

export default async function PatientAnalysisPage({ params }: PageProps) {
  const { id, entryId } = await params;

  let patient;
  let history;
  try {
    patient = await fetchPatientById(id);
    history = await fetchHistoryByPatient(id);
  } catch {
    notFound();
  }

  const historyEntry = history.find((entry) => String(entry.id) === entryId);

  if (!patient || !historyEntry || !historyEntry.analysis) {
    notFound();
  }

  return (
    <AnalysisPageClient patient={patient} analysis={historyEntry.analysis} />
  );
}