"use client";

import { useRef, useState } from "react";
import ImagePanZoom from "components/ImagePanZoom/ImagePanZoom";
import AnalysisResultCard from "components/AnalysisResultCard/AnalysisResultCard";
import type { Analysis, Patient } from "components/patient-record/patientRecord.data";

type Finding = Analysis["findings"][number];

type AnalysisPageClientProps = {
  patient: Patient;
  analysis: Analysis;
};

export default function AnalysisPageClient({
  patient,
  analysis,
}: AnalysisPageClientProps) {
  const imageExportRef = useRef<HTMLDivElement | null>(null);
  const cardExportRef = useRef<HTMLDivElement | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  return (
    <section
      style={{
        height: "100%",
        padding: "24px",
        display: "flex",
        gap: "24px",
        alignItems: "stretch",
      }}
    >
      <div
        ref={imageExportRef}
        style={{
          flex: "0 0 50vw",
          height: "100%",
          background: "#fff",
        }}
      >
        <ImagePanZoom
          src={analysis.imageSrc}
          gradCamSrc={selectedFinding?.gradCamSrc ?? null}
          alt={`${patient.name} scan`}
        />
      </div>

      <div
        ref={cardExportRef}
        style={{
          flex: 1,
          minWidth: 0,
          height: "100%",
          background: "#fff",
        }}
      >
        <AnalysisResultCard
          title={analysis.title}
          engine={analysis.engine}
          patient={{ id: patient.id, name: patient.name }}
          status={analysis.status}
          confidence={analysis.confidence}
          score={analysis.score}
          findings={analysis.findings}
          onRequestReview={(doctor) => {
            console.log("Selected doctor:", doctor);
          }}
          onSelectFinding={setSelectedFinding}
          imageExportRef={imageExportRef}
          cardExportRef={cardExportRef}
        />
      </div>
    </section>
  );
}