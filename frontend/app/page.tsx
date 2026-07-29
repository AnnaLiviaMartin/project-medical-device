import PatientOverview from "../components/PatientOverview/PatientOverview";

type SearchParams = Promise<{
  patientId?: string | string[];
}>;

export default async function PatientsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const patientId = Array.isArray(params.patientId)
    ? params.patientId[0]
    : params.patientId;

  return <PatientOverview initialPatientId={patientId} />;
}