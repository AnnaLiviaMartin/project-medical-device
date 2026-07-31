"use client";

import Link from "next/link";
import { useEffect, useMemo, useState, type RefObject } from "react";
import styles from "./AnalysisResultCard.module.css";

type Finding = {
  title: string;
  text: string;
  disease?: string;
  variant?: "blue" | "gray";
  icon?: string;
  confidence?: number;
  gradCamSrc?: string | null;
};

type Doctor = {
  id: string;
  name: string;
  specialty: string;
};

type PatientLinkData = {
  id: string;
  name: string;
};

type AnalysisResultCardProps = {
  title?: string;
  engine?: string;
  status: string;
  confidence: number;
  score: number;
  findings: Finding[];
  patient?: PatientLinkData;
  onViewAll?: () => void;
  doctors?: Doctor[];
  onRequestReview?: (doctor: Doctor) => void;
  imageExportRef: RefObject<HTMLDivElement | null>;
  cardExportRef: RefObject<HTMLDivElement | null>;
  onSelectFinding?: (finding: Finding | null) => void;
};

export default function AnalysisResultCard({
  title = "AI Analysis Results",
  engine = "V2.4 ENGINE",
  status,
  confidence,
  score,
  findings,
  patient,
  doctors = [
    { id: "1", name: "Dr. Emily Carter", specialty: "Radiology" },
    { id: "2", name: "Dr. Michael Tan", specialty: "Pulmonology" },
    { id: "3", name: "Dr. Sarah Klein", specialty: "Oncology" },
  ],
  onRequestReview,
  imageExportRef,
  cardExportRef,
  onSelectFinding,
}: AnalysisResultCardProps) {
  const [isDoctorModalOpen, setIsDoctorModalOpen] = useState(false);
  const [selectedDoctorId, setSelectedDoctorId] = useState<string>(doctors[0]?.id ?? "");
  const [isExporting, setIsExporting] = useState(false);

  const sortedFindings = useMemo(() => {
    return [...findings].sort((a, b) => {
      const confA = a.confidence ?? -1;
      const confB = b.confidence ?? -1;
      return confB - confA;
    });
  }, [findings]);

  const [selectedFindingIndex, setSelectedFindingIndex] = useState<number | null>(
    sortedFindings.length > 0 ? 0 : null
  );

  useEffect(() => {
    if (sortedFindings.length === 0) {
      setSelectedFindingIndex(null);
      return;
    }

    setSelectedFindingIndex((prev) => {
      if (prev === null || prev >= sortedFindings.length) return 0;
      return prev;
    });
  }, [sortedFindings]);

  const clampedScore = Math.max(0, Math.min(score, 100));

  const riskLevel = useMemo(() => {
    if (clampedScore >= 70) return "High";
    if (clampedScore >= 40) return "Medium";
    return "Low";
  }, [clampedScore]);

  const isNoFinding = useMemo(() => {
    if (sortedFindings.length === 0) return true;
    return sortedFindings.every((finding) => finding.title === "No Finding");
  }, [sortedFindings]);

  const selectedDoctor = doctors.find((doctor) => doctor.id === selectedDoctorId);
  const selectedFinding =
    selectedFindingIndex !== null ? sortedFindings[selectedFindingIndex] : null;
  const displayedConfidence = selectedFinding?.confidence ?? confidence;

  useEffect(() => {
    onSelectFinding?.(selectedFinding ?? null);
  }, [selectedFinding, onSelectFinding]);

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
          <div className={styles.headerInfo}>
            <div className={styles.titleRow}>
              <h2 className={styles.title}>{title}</h2>

              {patient && (
                <Link
                  href={`/patients/${encodeURIComponent(patient.id)}`}
                  className={styles.patientLink}
                >
                  {patient.name}
                </Link>
              )}
            </div>
          </div>

          <span className={styles.engine}>{engine}</span>
        </div>

        <div className={styles.stats}>
          <div
            className={`${styles.statBox} ${
              isNoFinding ? styles.statusBoxOk : styles.statusBox
            }`}
          >
            <p className={isNoFinding ? styles.statLabelOk : styles.statLabel}>
              STATUS
            </p>
            <div className={styles.statusRow}>
              <span
                className={`${styles.statusDot} ${
                  isNoFinding ? styles.statusDotOk : ""
                }`}
              />
              <p className={isNoFinding ? styles.statusTextOk : styles.statusText}>
                {status}
              </p>
            </div>
          </div>

          <div className={`${styles.statBox} ${styles.confidenceBox}`}>
            <p className={styles.statLabelBlue}>CONFIDENCE</p>
            <p className={styles.confidenceValue}>
              {displayedConfidence.toFixed(1)} <span>%</span>
            </p>
          </div>
        </div>

        <div className={styles.section}>
          <p className={styles.sectionLabel}>SUGGESTED CLINICAL FINDINGS</p>

          <div className={styles.findings}>
            {sortedFindings.map((finding, index) => {
              const isActive = index === selectedFindingIndex;
              const isFindingOk = finding.title === "No Finding";

              return (
                <button
                  key={`${finding.title}-${index}`}
                  type="button"
                  className={`${styles.findingCard} ${
                    isActive
                      ? isFindingOk
                        ? styles.findingCardActiveOk
                        : styles.findingCardActive
                      : ""
                  }`}
                  onClick={() => setSelectedFindingIndex(index)}
                >
                  <div className={styles.findingContent}>
                    <h3 className={styles.findingTitle}>
                      {isFindingOk ? "✓ " : ""}
                      {finding.title}
                    </h3>

                    {finding.disease && (
                      <p
                        className={
                          isFindingOk
                            ? styles.findingDiseaseOk
                            : styles.findingDisease
                        }
                      >
                        {finding.disease}
                        {typeof finding.confidence === "number" && (
                          <span
                            className={
                              isFindingOk
                                ? styles.findingConfidenceOk
                                : styles.findingConfidence
                            }
                          >
                            {" "}
                            · {finding.confidence.toFixed(1)}%
                          </span>
                        )}
                      </p>
                    )}

                    {!finding.disease && typeof finding.confidence === "number" && (
                      <p
                        className={
                          isFindingOk
                            ? styles.findingDiseaseOk
                            : styles.findingDisease
                        }
                      >
                        <span
                          className={
                            isFindingOk
                              ? styles.findingConfidenceOk
                              : styles.findingConfidence
                          }
                        >
                          {finding.confidence.toFixed(1)}%
                        </span>
                      </p>
                    )}

                    <p className={styles.findingText}>{finding.text}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className={styles.divider} />

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
          <div className={styles.modal} onClick={(event) => event.stopPropagation()}>
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