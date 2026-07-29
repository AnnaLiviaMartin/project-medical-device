import Link from "next/link";
import styles from "./patientRecord.module.css";
import type { Scan } from "./patientRecord.data";

type ScanLinkListProps = {
  scans?: Scan[];
  patientId: string;
  entryId: string;
};

export default function ScanLinkList({
  scans = [],
  patientId,
  entryId,
}: ScanLinkListProps) {
  if (scans.length === 0) {
    return (
      <p className={styles.scanEmpty}>
        No scans are linked to this history entry.
      </p>
    );
  }

  return (
    <div className={styles.scanList}>
      {scans.map((scan) => (
        <Link
          key={scan.id}
          href={`/patients/${patientId}/analysis/${entryId}`}
          className={styles.scanCard}
        >
          <div>
            <p className={styles.scanTitle}>{scan.title}</p>
            <p className={styles.scanMeta}>
              {scan.modality} · {scan.date}
            </p>
          </div>
          <span className={styles.scanLink}>Open Scan</span>
        </Link>
      ))}
    </div>
  );
}