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
};

export const patients: Patient[] = [
  {
    id: "P-1024",
    name: "Anna Becker",
    age: 47,
    gender: "female",
    diagnosis: "Hypertension",
    status: "Outpatient",
    lastVisit: "21.06.2026",
    nextAppointment: "30.06.2026",
    doctor: "Dr. Klein",
    ward: "Outpatient Unit A",
    address: {
      street: "Rheinstraße 12",
      zip: "65185",
      city: "Wiesbaden",
    },
    emergencyContact: {
      name: "Thomas Becker",
      relation: "Husband",
      phone: "+49 171 2345678",
    },
    insurance: {
      provider: "AOK Hessen",
      policyNumber: "AOK-7741-92",
    },
    allergies: ["Penicillin"],
    medications: [
      { name: "Ramipril", dosage: "5 mg", schedule: "1x daily" },
      { name: "Amlodipine", dosage: "5 mg", schedule: "1x daily" },
    ],
    vitals: {
      bloodPressure: "142/89 mmHg",
      heartRate: "78 bpm",
      oxygenSaturation: "98%",
      temperature: "36.8°C",
    },
  },
  {
    id: "P-1025",
    name: "Mehmet Yilmaz",
    age: 63,
    gender: "male",
    diagnosis: "Type 2 Diabetes",
    status: "Inpatient",
    lastVisit: "24.06.2026",
    nextAppointment: "26.06.2026",
    doctor: "Dr. Schneider",
    ward: "Ward 3",
    address: {
      street: "Bleichstraße 44",
      zip: "65183",
      city: "Wiesbaden",
    },
    emergencyContact: {
      name: "Aylin Yilmaz",
      relation: "Daughter",
      phone: "+49 176 9876543",
    },
    insurance: {
      provider: "TK",
      policyNumber: "TK-2204-18",
    },
    allergies: ["No known allergies"],
    medications: [
      { name: "Metformin", dosage: "1000 mg", schedule: "2x daily" },
      { name: "Insulin Glargine", dosage: "10 IU", schedule: "Nightly" },
    ],
    vitals: {
      bloodPressure: "136/84 mmHg",
      heartRate: "82 bpm",
      oxygenSaturation: "97%",
      temperature: "37.0°C",
    },
  },
  {
    id: "P-1026",
    name: "Laura Schmidt",
    age: 31,
    gender: "female",
    diagnosis: "Asthma",
    status: "Outpatient",
    lastVisit: "18.06.2026",
    nextAppointment: "05.07.2026",
    doctor: "Dr. Weber",
    ward: "Outpatient Unit B",
    address: {
      street: "Mainzer Straße 88",
      zip: "65189",
      city: "Wiesbaden",
    },
    emergencyContact: {
      name: "Julia Schmidt",
      relation: "Sister",
      phone: "+49 160 4567890",
    },
    insurance: {
      provider: "Barmer",
      policyNumber: "BAR-5190-33",
    },
    allergies: ["Pollen"],
    medications: [
      { name: "Salbutamol", dosage: "100 µg", schedule: "As needed" },
      { name: "Budesonide", dosage: "200 µg", schedule: "2x daily" },
    ],
    vitals: {
      bloodPressure: "118/76 mmHg",
      heartRate: "72 bpm",
      oxygenSaturation: "99%",
      temperature: "36.7°C",
    },
  },
  {
    id: "P-1027",
    name: "Jonas Hartmann",
    age: 56,
    gender: "male",
    diagnosis: "Suspected Pneumonia",
    status: "Inpatient",
    lastVisit: "25.06.2026",
    nextAppointment: "02.07.2026",
    doctor: "Dr. Fischer",
    ward: "Emergency Department",
    address: {
      street: "Schwalbacher Straße 31",
      zip: "65183",
      city: "Wiesbaden",
    },
    emergencyContact: {
      name: "Mara Hartmann",
      relation: "Wife",
      phone: "+49 152 7654321",
    },
    insurance: {
      provider: "DAK-Gesundheit",
      policyNumber: "DAK-9043-77",
    },
    allergies: ["Contrast agent"],
    medications: [
      { name: "Amoxicillin", dosage: "1000 mg", schedule: "3x daily" },
      { name: "Paracetamol", dosage: "500 mg", schedule: "As needed" },
    ],
    vitals: {
      bloodPressure: "138/88 mmHg",
      heartRate: "94 bpm",
      oxygenSaturation: "93%",
      temperature: "38.4°C",
    },
  },
  {
    id: "P-1028",
    name: "Sofia Wagner",
    age: 72,
    gender: "female",
    diagnosis: "Postoperative Follow-up",
    status: "Inpatient",
    lastVisit: "23.06.2026",
    nextAppointment: "27.06.2026",
    doctor: "Dr. Braun",
    ward: "Ward 1",
    address: {
      street: "Dotzheimer Straße 55",
      zip: "65197",
      city: "Wiesbaden",
    },
    emergencyContact: {
      name: "Daniel Wagner",
      relation: "Son",
      phone: "+49 170 1122334",
    },
    insurance: {
      provider: "BARMER",
      policyNumber: "BAR-8801-52",
    },
    allergies: ["Latex"],
    medications: [
      { name: "Ibuprofen", dosage: "400 mg", schedule: "3x daily" },
      { name: "Pantoprazole", dosage: "40 mg", schedule: "1x daily" },
    ],
    vitals: {
      bloodPressure: "129/79 mmHg",
      heartRate: "76 bpm",
      oxygenSaturation: "96%",
      temperature: "36.6°C",
    },
  },
  {
    id: "P-1029",
    name: "Alex Demir",
    age: 39,
    gender: "diverse",
    diagnosis: "Chronic Cough Evaluation",
    status: "Outpatient",
    lastVisit: "26.06.2026",
    nextAppointment: "08.07.2026",
    doctor: "Dr. Neumann",
    ward: "Pulmonology Outpatient Clinic",
    address: {
      street: "Luisenstraße 19",
      zip: "65185",
      city: "Wiesbaden",
    },
    emergencyContact: {
      name: "Selin Demir",
      relation: "Partner",
      phone: "+49 151 3344556",
    },
    insurance: {
      provider: "Techniker Krankenkasse",
      policyNumber: "TK-6612-40",
    },
    allergies: ["No known allergies"],
    medications: [
      { name: "Ambroxol", dosage: "30 mg", schedule: "3x daily" },
      { name: "Montelukast", dosage: "10 mg", schedule: "1x daily" },
    ],
    vitals: {
      bloodPressure: "121/80 mmHg",
      heartRate: "74 bpm",
      oxygenSaturation: "97%",
      temperature: "36.9°C",
    },
  },
];

export const patientHistory: Record<string, HistoryEntry[]> = {
  "P-1024": [
    {
      id: "H-1024-1",
      date: "12.06.2026",
      title: "Routine blood pressure check",
      category: "Visit",
      description:
        "Outpatient review completed. Elevated blood pressure values remained stable compared to the previous visit.",
      doctor: "Dr. Klein",
      department: "Outpatient Unit A",
      scans: [],
    },
    {
      id: "H-1024-2",
      date: "21.06.2026",
      title: "Chest X-ray screening",
      category: "Finding",
      description:
        "Chest imaging requested as part of routine cardiovascular risk screening.",
      doctor: "Dr. Klein",
      department: "Radiology",
      scans: [
        {
          id: "S-1024-1",
          title: "Chest X-Ray",
          date: "21.06.2026",
          modality: "X-Ray",
          href: "/scans/sample-cardiac-ct.pdf",
        },
      ],
      analysis: {
        title: "AI Analysis Results",
        engine: "V2.4 ENGINE",
        status: "No significant findings",
        confidence: 95.4,
        score: 14,
        imageSrc: "/test.png",
        findings: [
          {
            title: "Cardiac Silhouette",
            disease: "Mild Cardiomegaly",
            text: "Slightly enlarged cardiac silhouette, consistent with known hypertension.",
            confidence: 78.2,
          },
          {
            title: "Lung Fields",
            disease: "Clear",
            text: "No consolidation, nodules, or effusion detected in either lung field.",
            confidence: 95.4,
          },
        ],
      },
    },
  ],
  "P-1025": [
    {
      id: "H-1025-1",
      date: "20.06.2026",
      title: "Inpatient admission",
      category: "Visit",
      description:
        "Patient admitted for glucose stabilization and structured metabolic monitoring.",
      doctor: "Dr. Schneider",
      department: "Ward 3",
      scans: [],
    },
    {
      id: "H-1025-2",
      date: "24.06.2026",
      title: "Chest X-ray assessment",
      category: "Procedure",
      description:
        "Chest imaging ordered to exclude pulmonary complications during inpatient monitoring.",
      doctor: "Dr. Schneider",
      department: "Radiology",
      scans: [
        {
          id: "S-1025-1",
          title: "Chest X-Ray",
          date: "24.06.2026",
          modality: "X-Ray",
          href: "/scans/sample-chest-xray.pdf",
        },
      ],
      analysis: {
        title: "AI Analysis Results",
        engine: "V2.4 ENGINE",
        status: "Anomalies detected",
        confidence: 94.8,
        score: 75,
        imageSrc: "/test.png",
        findings: [
          {
            title: "Nodular Opacity",
            disease: "Pulmonary Nodule",
            text: "Suspected lesion in the left lower lobe (Region Critical-03), irregular margins noted.",
            confidence: 94.8,
          },
          {
            title: "Pleural Effusion",
            disease: "Pleural Fluid",
            text: "Minor blunting of the costophrenic angle observed in the right lung field.",
            confidence: 81.2,
          },
          {
            title: "Inflammatory Pattern",
            disease: "Possible Infection",
            text: "Diffuse lower-lung opacity may indicate an inflammatory process.",
            confidence: 76.5,
          },
        ],
      },
    },
  ],
  "P-1026": [
    {
      id: "H-1026-1",
      date: "18.06.2026",
      title: "Pulmonary follow-up",
      category: "Follow-up",
      description:
        "Lung function stable. No acute respiratory distress observed during the outpatient assessment.",
      doctor: "Dr. Weber",
      department: "Outpatient Unit B",
      scans: [
        {
          id: "S-1026-1",
          title: "Chest X-Ray",
          date: "18.06.2026",
          modality: "X-Ray",
          href: "/scans/sample-lung-xray.pdf",
        },
      ],
      analysis: {
        title: "AI Analysis Results",
        engine: "V2.4 ENGINE",
        status: "No significant findings",
        confidence: 96.2,
        score: 18,
        imageSrc: "/test.png",
        findings: [
          {
            title: "Airway Pattern",
            disease: "Mild Bronchial Wall Thickening",
            text: "Slight bronchial wall thickening consistent with known asthma history.",
            confidence: 88.4,
          },
          {
            title: "Lung Fields",
            disease: "Clear",
            text: "No consolidation, effusion, or nodules detected in either lung field.",
            confidence: 96.2,
          },
        ],
      },
    },
  ],
  "P-1027": [
    {
      id: "H-1027-1",
      date: "25.06.2026",
      title: "Emergency respiratory assessment",
      category: "Visit",
      description:
        "Patient presented with fever, productive cough, and shortness of breath. Initial inpatient workup was initiated.",
      doctor: "Dr. Fischer",
      department: "Emergency Department",
      scans: [],
    },
    {
      id: "H-1027-2",
      date: "25.06.2026",
      title: "Chest X-ray for suspected pneumonia",
      category: "Finding",
      description:
        "Imaging ordered due to fever and reduced oxygen saturation on admission.",
      doctor: "Dr. Fischer",
      department: "Radiology",
      scans: [
        {
          id: "S-1027-1",
          title: "Chest X-Ray",
          date: "25.06.2026",
          modality: "X-Ray",
          href: "/scans/sample-coronary-ct.pdf",
        },
      ],
      analysis: {
        title: "AI Analysis Results",
        engine: "V2.4 ENGINE",
        status: "Anomalies detected",
        confidence: 92.6,
        score: 84,
        imageSrc: "/test.png",
        findings: [
          {
            title: "Consolidation",
            disease: "Pneumonia",
            text: "Dense consolidation in the right lower lobe consistent with bacterial pneumonia.",
            confidence: 92.6,
          },
          {
            title: "Pleural Reaction",
            disease: "Small Pleural Effusion",
            text: "Mild blunting of the right costophrenic angle, likely reactive to infection.",
            confidence: 68.9,
          },
          {
            title: "Cardiac Silhouette",
            disease: "Normal",
            text: "Cardiac size and contour remain within normal limits.",
            confidence: 90.3,
          },
        ],
      },
    },
  ],
  "P-1028": [
    {
      id: "H-1028-1",
      date: "23.06.2026",
      title: "Postoperative ward review",
      category: "Follow-up",
      description:
        "Postoperative recovery remained stable with no signs of wound infection or acute complications.",
      doctor: "Dr. Braun",
      department: "Ward 1",
      scans: [],
    },
    {
      id: "H-1028-2",
      date: "23.06.2026",
      title: "Postoperative chest X-ray",
      category: "Procedure",
      description:
        "Chest imaging performed to exclude postoperative pulmonary complications such as atelectasis or effusion.",
      doctor: "Dr. Braun",
      department: "Radiology",
      scans: [
        {
          id: "S-1028-1",
          title: "Chest X-Ray",
          date: "23.06.2026",
          modality: "X-Ray",
          href: "/scans/sample-abdominal-ultrasound.pdf",
        },
      ],
      analysis: {
        title: "AI Analysis Results",
        engine: "V2.4 ENGINE",
        status: "Mild findings",
        confidence: 90.1,
        score: 34,
        imageSrc: "/test.png",
        findings: [
          {
            title: "Basal Atelectasis",
            disease: "Atelectasis",
            text: "Small areas of basal atelectasis in the right lower lobe, common postoperatively.",
            confidence: 85.7,
          },
          {
            title: "Pleural Space",
            disease: "No Effusion",
            text: "No significant pleural fluid accumulation detected.",
            confidence: 90.1,
          },
        ],
      },
    },
  ],
  "P-1029": [
    {
      id: "H-1029-1",
      date: "26.06.2026",
      title: "Pulmonology outpatient consultation",
      category: "Visit",
      description:
        "Evaluation performed for persistent chronic cough with occasional wheezing.",
      doctor: "Dr. Neumann",
      department: "Pulmonology Outpatient Clinic",
      scans: [],
    },
    {
      id: "H-1029-2",
      date: "26.06.2026",
      title: "Chest X-ray referral",
      category: "Procedure",
      description:
        "Imaging requested to exclude structural or infectious causes of the chronic cough.",
      doctor: "Dr. Neumann",
      department: "Radiology",
      scans: [
        {
          id: "S-1029-1",
          title: "Chest X-Ray",
          date: "26.06.2026",
          modality: "X-Ray",
          href: "/scans/sample-brain-mri.pdf",
        },
      ],
      analysis: {
        title: "AI Analysis Results",
        engine: "V2.4 ENGINE",
        status: "No significant findings",
        confidence: 97.6,
        score: 12,
        imageSrc: "/test.png",
        findings: [
          {
            title: "Lung Parenchyma",
            disease: "Unremarkable",
            text: "No infiltrates, nodules, or fibrotic changes identified.",
            confidence: 97.6,
          },
          {
            title: "Bronchovascular Markings",
            disease: "Normal",
            text: "Bronchovascular markings appear within normal limits, no signs of emphysema.",
            confidence: 93.8,
          },
        ],
      },
    },
  ],
};

export function getStatusLabel(status: PatientStatus) {
  if (status === "Inpatient") return "Inpatient";
  return "Outpatient";
}