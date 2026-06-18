import "./globals.css";
import SideMenu from "./components/sideMenu/sideMenu";

import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body>
        <div style={{ display: "flex", height: "100vh", width: "100vw" }}>
          <div style={{ width: "256px", background: "blue", color: "white" }}>
          <SideMenu />
          </div>

          <div style={{ flex: 1, width: "33%"}}>
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}