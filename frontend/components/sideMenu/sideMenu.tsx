"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./SideMenu.module.css";

const navItems = [
  { label: "Patient Management", href: "/" },
];

export default function SideMenu() {
  const pathname = usePathname();

  return (
    <aside className={styles.sideMenu}>
      
      <div className={styles.logo}>
        ALM-DR-AI
      </div>

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