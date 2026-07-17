import { notFound } from "next/navigation";
import AnalysisPageClient from "./AnalysisPageClient";
import {
  patients,
  patientHistory,
} from "components/patient-record/patientRecord.data";

type PageProps = {
  params: Promise<{ id: string; entryId: string }>;
};

export default async function PatientAnalysisPage({ params }: PageProps) {
  const { id, entryId } = await params;

  const patient = patients.find((entry) => entry.id === id);
  const history = patientHistory[id] ?? [];
  const historyEntry = history.find((entry) => entry.id === entryId);

  if (!patient || !historyEntry || !historyEntry.analysis) {
    notFound();
  }

  return (
    <AnalysisPageClient patient={patient} analysis={historyEntry.analysis} />
  );
}