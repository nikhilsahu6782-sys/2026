import React, { useEffect, useState } from "react";
import { FaBell } from "react-icons/fa";

/**
 * Webpushr push-notification subscribe button.
 * Clicks the dashboard-generated Webpushr widget (id: webpushr-subscription-button)
 * so the browser permission prompt + subscription stays owned by the Webpushr SDK.
 * Requires the Webpushr snippet in public/index.html with the real site key.
 */
const PushSubscribeButton = ({ lang = "hi", className = "" }) => {
  const [permission, setPermission] = useState(
    typeof Notification === "undefined" ? "unsupported" : Notification.permission
  );

  useEffect(() => {
    // Keep permission state in sync after the browser prompt resolves
    const timer = setInterval(() => {
      if (typeof Notification !== "undefined" && Notification.permission !== permission) {
        setPermission(Notification.permission);
      }
    }, 2000);
    return () => clearInterval(timer);
  }, [permission]);

  if (permission === "unsupported") return null;

  if (permission === "granted") {
    return (
      <span className={`inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-300 ${className}`} data-testid="push-subscribe-status">
        <FaBell /> {lang === "hi" ? "Push Alerts ON ✓" : "Push Alerts ON ✓"}
      </span>
    );
  }

  const subscribe = () => {
    const wbtn = document.getElementById("webpushr-subscription-button");
    if (wbtn) {
      wbtn.click();
    } else if (typeof window !== "undefined" && window.webpushr) {
      // Widget not injected yet — queue a retry once SDK finishes loading
      setTimeout(() => document.getElementById("webpushr-subscription-button")?.click(), 1500);
    }
  };

  return (
    <button
      type="button"
      onClick={subscribe}
      className={`inline-flex items-center gap-2 bg-white/15 hover:bg-white/25 border border-white/25 text-white text-xs font-bold px-4 py-2 rounded-full transition ${className}`}
      data-testid="push-subscribe-button"
      title={permission === "denied"
        ? (lang === "hi" ? "Browser settings mein notifications allow karein" : "Enable notifications in browser site settings")
        : (lang === "hi" ? "Nayi bharti ki push notification paayein" : "Get push notifications for new vacancies")}
    >
      <FaBell className={permission === "denied" ? "opacity-50" : "animate-pulse"} />
      {permission === "denied"
        ? (lang === "hi" ? "Push Blocked — Settings देखें" : "Push Blocked — see Settings")
        : (lang === "hi" ? "Push Alerts पाएँ" : "Get Push Alerts")}
    </button>
  );
};

export default PushSubscribeButton;
