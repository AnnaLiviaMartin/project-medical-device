"use client";

import { useMemo, useState, type RefObject } from "react";
import styles from "./AnalysisResultCard.module.css";

type Finding = {
  title: string;
  text: string;
  disease?: string;
  variant?: "blue" | "gray";
  icon?: string;
};

type Doctor = {
  id: string;
  name: string;
  specialty: string;
};

type AnalysisResultCardProps = {
  title?: string;
  engine?: string;
  status: string;
  confidence: number;
  score: number;
  findings: Finding[];
  onViewAll?: () => void;
  doctors?: Doctor[];
  onRequestReview?: (doctor: Doctor) => void;
  imageExportRef: RefObject<HTMLDivElement | null>;
  cardExportRef: RefObject<HTMLDivElement | null>;
};

export default function AnalysisResultCard({
  title = "AI Analysis Results",
  engine = "V2.4 ENGINE",
  status,
  confidence,
  score,
  findings,
  onViewAll,
  doctors = [
    { id: "1", name: "Dr. Emily Carter", specialty: "Radiology" },
    { id: "2", name: "Dr. Michael Tan", specialty: "Pulmonology" },
    { id: "3", name: "Dr. Sarah Klein", specialty: "Oncology" },
  ],
  onRequestReview,
  imageExportRef,
  cardExportRef,
}: AnalysisResultCardProps) {
  const [isDoctorModalOpen, setIsDoctorModalOpen] = useState(false);
  const [selectedDoctorId, setSelectedDoctorId] = useState<string>(doctors[0]?.id ?? "");
  const [isExporting, setIsExporting] = useState(false);

  const clampedScore = Math.max(0, Math.min(score, 100));

  const riskLevel = useMemo(() => {
    if (clampedScore >= 70) return "High";
    if (clampedScore >= 40) return "Medium";
    return "Low";
  }, [clampedScore]);

  const selectedDoctor = doctors.find((doctor) => doctor.id === selectedDoctorId);

  const handleConfirmDoctor = () => {
    if (!selectedDoctor) return;
    onRequestReview?.(selectedDoctor);
    console.log("Human review requested for:", selectedDoctor);
    setIsDoctorModalOpen(false);
  };

  const handleExportPdf = async () => {
    if (!imageExportRef.current || !cardExportRef.current) return;

    try {
      setIsExporting(true);

      const html2canvas = (await import("html2canvas")).default;
      const { jsPDF } = await import("jspdf");

      const [imageCanvas, cardCanvas] = await Promise.all([
        html2canvas(imageExportRef.current, {
          scale: 2,
          useCORS: true,
          backgroundColor: "#ffffff",
        }),
        html2canvas(cardExportRef.current, {
          scale: 2,
          useCORS: true,
          backgroundColor: "#ffffff",
        }),
      ]);

      const pdf = new jsPDF("p", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 10;
      const contentWidth = pageWidth - margin * 2;
      let currentY = margin;

      const addCanvasToPdf = (canvas: HTMLCanvasElement) => {
        const imgData = canvas.toDataURL("image/png");
        const renderHeight = (canvas.height * contentWidth) / canvas.width;

        if (currentY + renderHeight > pageHeight - margin) {
          pdf.addPage();
          currentY = margin;
        }

        pdf.addImage(imgData, "PNG", margin, currentY, contentWidth, renderHeight);
        currentY += renderHeight + 8;
      };

      addCanvasToPdf(imageCanvas);
      addCanvasToPdf(cardCanvas);

      pdf.save("analysis-report.pdf");
    } catch (error) {
      console.error("PDF export failed:", error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <>
      <div className={styles.card}>
        <div className={styles.header}>
          <h2 className={styles.title}>{title}</h2>
          <span className={styles.engine}>{engine}</span>
        </div>

        <div className={styles.stats}>
          <div className={`${styles.statBox} ${styles.statusBox}`}>
            <p className={styles.statLabel}>STATUS</p>
            <div className={styles.statusRow}>
              <span className={styles.statusDot} />
              <p className={styles.statusText}>{status}</p>
            </div>
          </div>

          <div className={`${styles.statBox} ${styles.confidenceBox}`}>
            <p className={styles.statLabelBlue}>CONFIDENCE</p>
            <p className={styles.confidenceValue}>
              {confidence.toFixed(1)} <span>%</span>
            </p>
          </div>
        </div>

        <div className={styles.section}>
          <p className={styles.sectionLabel}>SUGGESTED CLINICAL FINDINGS</p>

          <div className={styles.findings}>
            {findings.map((finding, index) => (
              <div key={`${finding.title}-${index}`} className={styles.findingCard}>
                <div
                  className={
                    finding.variant === "gray"
                      ? styles.findingIconGray
                      : styles.findingIconBlue
                  }
                >
                  <span>{finding.icon ?? "i"}</span>
                </div>

                <div>
                  <h3 className={styles.findingTitle}>{finding.title}</h3>

                  {finding.disease && (
                    <p className={styles.findingDisease}>{finding.disease}</p>
                  )}

                  <p className={styles.findingText}>{finding.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.divider} />

        <div className={styles.historyHeader}>
          <p className={styles.sectionLabel}>PATIENT HISTORY</p>
          {onViewAll && (
            <button className={styles.viewAll} onClick={onViewAll}>
              View All
            </button>
          )}
        </div>

        <div className={styles.progressTrack}>
          <div
            className={styles.progressFill}
            style={{ width: `${clampedScore}%` }}
          />
        </div>

        <p className={styles.historyText}>
          Historical risk alignment: {riskLevel} ({clampedScore}%)
        </p>

        <button className={styles.primaryButton}>
          <span className={styles.primaryIcon}>✓</span>
          Validate Result
        </button>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.secondaryButton}
            onClick={() => setIsDoctorModalOpen(true)}
          >
            <span className={styles.secondaryIcon}>⌁</span>
            <span>
              Request
              <br />
              Review
            </span>
          </button>

          <button
            type="button"
            className={styles.secondaryButton}
            onClick={handleExportPdf}
            disabled={isExporting}
          >
            <span className={styles.secondaryIcon}>⎘</span>
            <span>
              {isExporting ? (
                <>
                  Exporting
                  <br />
                  PDF
                </>
              ) : (
                <>
                  Export
                  <br />
                  Report
                </>
              )}
            </span>
          </button>
        </div>
      </div>

      {isDoctorModalOpen && (
        <div className={styles.modalOverlay} onClick={() => setIsDoctorModalOpen(false)}>
          <div
            className={styles.modal}
            onClick={(event) => event.stopPropagation()}
          >
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>Request Review</h3>
              <button
                type="button"
                className={styles.modalClose}
                onClick={() => setIsDoctorModalOpen(false)}
              >
                ✕
              </button>
            </div>

            <p className={styles.modalText}>
              Select a doctor for secondary review.
            </p>

            <div className={styles.doctorList}>
              {doctors.map((doctor) => (
                <label key={doctor.id} className={styles.doctorOption}>
                  <input
                    type="radio"
                    name="doctor"
                    value={doctor.id}
                    checked={selectedDoctorId === doctor.id}
                    onChange={() => setSelectedDoctorId(doctor.id)}
                  />
                  <div>
                    <div className={styles.doctorName}>{doctor.name}</div>
                    <div className={styles.doctorSpecialty}>{doctor.specialty}</div>
                  </div>
                </label>
              ))}
            </div>

            <div className={styles.modalActions}>
              <button
                type="button"
                className={styles.modalSecondaryButton}
                onClick={() => setIsDoctorModalOpen(false)}
              >
                Cancel
              </button>

              <button
                type="button"
                className={styles.modalPrimaryButton}
                onClick={handleConfirmDoctor}
                disabled={!selectedDoctor}
              >
                Send Request
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}