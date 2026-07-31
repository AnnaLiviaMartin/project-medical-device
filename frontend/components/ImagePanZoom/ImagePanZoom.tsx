"use client";

import React, { useEffect, useRef, useState } from "react";
import styles from "./ImagePanZoom.module.css";

type Point = { x: number; y: number };

type ImagePanZoomProps = {
  src?: string;
  gradCamSrc?: string | null;
  alt?: string;
};

export default function ImagePanZoom({
  src = "/test.png",
  gradCamSrc = null,
  alt = "Medical image",
}: ImagePanZoomProps) {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState<Point>({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [viewMode, setViewMode] = useState<"normal" | "gradcam">("normal");

  const startRef = useRef<Point>({ x: 0, y: 0 });
  const startPosRef = useRef<Point>({ x: 0, y: 0 });

  useEffect(() => {
    if (!gradCamSrc) {
      setViewMode("normal");
    }
  }, [gradCamSrc]);

  const zoomIn = () => setScale((s) => Math.min(s + 0.2, 4));
  const zoomOut = () => setScale((s) => Math.max(s - 0.2, 0.5));

  const reset = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    setDragging(true);
    startRef.current = { x: e.clientX, y: e.clientY };
    startPosRef.current = position;
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragging) return;

    const dx = e.clientX - startRef.current.x;
    const dy = e.clientY - startRef.current.y;

    setPosition({
      x: startPosRef.current.x + dx,
      y: startPosRef.current.y + dy,
    });
  };

  const onPointerUp = () => {
    setDragging(false);
  };

  const activeSrc = viewMode === "gradcam" && gradCamSrc ? gradCamSrc : src;

  return (
    <div className={styles["image-pan-zoom"]}>
      <div className={styles["image-pan-zoom__toolbar"]}>
        <button type="button" className={styles["image-pan-zoom__button"]} onClick={zoomIn}>
          +
        </button>

        <button type="button" className={styles["image-pan-zoom__button"]} onClick={zoomOut}>
          −
        </button>

        <button type="button" className={styles["image-pan-zoom__button"]} onClick={reset}>
          Reset
        </button>

        {gradCamSrc ? (
          <button
            type="button"
            className={styles["image-pan-zoom__button"]}
            onClick={() =>
              setViewMode((mode) => (mode === "normal" ? "gradcam" : "normal"))
            }
          >
            {viewMode === "normal" ? "Grad-CAM" : "Original"}
          </button>
        ) : null}
      </div>

      <div
        className={styles["image-pan-zoom__viewport"]}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        <img
          src={activeSrc}
          alt={alt}
          draggable={false}
          className={`${styles["image-pan-zoom__image"]} ${
            dragging ? styles["is-dragging"] : ""
          }`}
          style={{
            transform: `translate(-50%, -50%) translate(${position.x}px, ${position.y}px) scale(${scale})`,
          }}
        />
      </div>
    </div>
  );
}