"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./SideMenu.module.css";

const navItems = [
  { label: "Dashboard", href: "/" },
  { label: "Scan Results", href: "/scan-results" },
  { label: "Patient Management", href: "/patients" },
  { label: "System Monitors", href: "/system" },
];

export default function SideMenu() {
  const pathname = usePathname();

  return (
    <aside className={styles.sideMenu}>
      
      {/* Logo */}
      <div className={styles.logo}>
        MedImage AI
      </div>

      {/* Navigation */}
      <nav className={styles.nav}>
        {navItems.map((item) => {
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`${styles.navItem} ${
                isActive ? styles.navItemActive : styles.navItemHover
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className={styles.bottom}>
        <Link href="/support" className={styles.navItem}>
          Support
        </Link>

        <Link href="/settings" className={styles.navItem}>
          Settings
        </Link>
      </div>

    </aside>
  );
}