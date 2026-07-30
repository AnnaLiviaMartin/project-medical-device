export type PatientStatus = "Inpatient" | "Outpatient";
export type Gender = "female" | "male" | "diverse";

export type Patient = {
  id: string;
  name: string;
  age: number;
  gender: Gender;
  diagnosis: string;
  status: PatientStatus;
  lastVisit: string;
  nextAppointment: string;
  doctor: string;
  ward: string;
  address: {
    street: string;
    zip: string;
    city: string;
  };
  emergencyContact: {
    name: string;
    relation: string;
    phone: string;
  };
  insurance: {
    provider: string;
    policyNumber: string;
  };
  allergies: string[];
  medications: {
    name: string;
    dosage: string;
    schedule: string;
  }[];
  vitals: {
    bloodPressure: string;
    heartRate: string;
    oxygenSaturation: string;
    temperature: string;
  };
};

export type Scan = {
  id: string;
  title: string;
  date: string;
  modality: "X-Ray";
  href: string;
};

export type AnalysisFinding = {
  title: string;
  text: string;
  disease?: string;
  confidence?: number;
};

export type Analysis = {
  title?: string;
  engine?: string;
  status: string;
  confidence: number;
  score: number;
  imageSrc: string;
  findings: AnalysisFinding[];
};

export type Attachment = {
  id: string;
  fileName: string;
  fileType: string; // z.B. "application/pdf", "image/png"
  fileSize: number; // in bytes
  uploadedAt: string; // ISO date
  url: string; // Download-/Preview-Link vom Backend
};

export type HistoryEntry = {
  id: string;
  date: string;
  title: string;
  category: "Visit" | "Procedure" | "Finding" | "Medication" | "Follow-up";
  description: string;
  doctor: string;
  department: string;
  scans?: Scan[];
  analysis?: Analysis;
  attachments?: Attachment[];
};

export function getStatusLabel(status: PatientStatus) {
  if (status === "Inpatient") return "Inpatient";
  return "Outpatient";
}