import { useEffect } from "react";
import { BACKEND_URL } from "@/lib/api";

// Injects Google Search Console verification meta + Google Analytics (GA4)
// based on settings saved in the admin panel (Analytics & SEO).
const SeoHead = () => {
  useEffect(() => {
    let cancelled = false;
    fetch(`${BACKEND_URL}/api/site-settings`)
      .then((r) => r.json())
      .then((data) => {
        if (cancelled || !data) return;

        // Google Search Console verification meta tag
        if (data.gsc_verification) {
          const raw = String(data.gsc_verification);
          const content = raw.includes("<meta")
            ? (raw.match(/content=["']([^"']+)["']/)?.[1] || "")
            : raw.trim();
          if (content && !document.querySelector('meta[name="google-site-verification"]')) {
            const m = document.createElement("meta");
            m.name = "google-site-verification";
            m.content = content;
            document.head.appendChild(m);
          }
        }

        // Google Analytics (GA4)
        if (data.ga4_id && !window.__ga4Loaded) {
          window.__ga4Loaded = true;
          const s = document.createElement("script");
          s.async = true;
          s.src = `https://www.googletagmanager.com/gtag/js?id=${data.ga4_id}`;
          document.head.appendChild(s);
          window.dataLayer = window.dataLayer || [];
          window.gtag = function () { window.dataLayer.push(arguments); };
          window.gtag("js", new Date());
          window.gtag("config", data.ga4_id);
        }
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);
  return null;
};

export default SeoHead;
