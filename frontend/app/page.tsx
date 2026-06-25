"use client";

import { useRef, useState } from "react";
import ImagePanZoom from "./components/ImagePanZoom/ImagePanZoom";
import AnalysisResultCard from "./components/AnalysisResultCard/AnalysisResultCard";

export default function Home() {
  const [selectedImage] = useState<string | null>(null);

  const imageExportRef = useRef<HTMLDivElement | null>(null);
  const cardExportRef = useRef<HTMLDivElement | null>(null);

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
          src={selectedImage ?? "/test.png"}
          alt="Standardbild"
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
          status="Anomalies detected"
          confidence={94.8}
          score={75}
          findings={[
            {
              title: "Nodular Opacity",
              text: "Suspected lesion in the left lower lobe (Region Critical-03), irregular margins noted.",
              variant: "blue",
              icon: "i",
            },
            {
              title: "Pleural Effusion",
              text: "Minor blunting of the costophrenic angle observed in the right lung field.",
              variant: "gray",
              icon: "○",
            },
          ]}
          onViewAll={() => console.log("View all clicked")}
          onRequestReview={(doctor) => {
            console.log("Selected doctor:", doctor);
          }}
          imageExportRef={imageExportRef}
          cardExportRef={cardExportRef}
        />
      </div>
    </section>
  );
}