"use client";

import { useState } from "react";
import ImagePanZoom from "./components/ImagePanZoom/ImagePanZoom";

export default function Home() {
  const [selectedImage] = useState<string | null>(null);

  return (
    <section style={{ height: "100%", padding: "24px" }}>
      <div style={{ width: "50vw", height: "100%" }}>
        <ImagePanZoom
          src={selectedImage ?? "/test.png"}
          alt="Standardbild"
        />
      </div>
    </section>
  );
}