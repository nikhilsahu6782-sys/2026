import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import api from "@/lib/api";

/* Theme system for the public site. Re-maps the global CSS variables so the
   whole site re-skins instantly. Persists the visitor's choice in localStorage;
   first-time visitors get the admin-configured site default. */

export const THEME_KEYS = ["light", "dark", "system", "luxury", "retro", "arctic", "nature", "ember", "dracula", "midnight"];
const LIGHT_BASED = ["light", "luxury", "retro", "arctic", "nature"];
const THEME_CLASSES = ["theme-luxury", "theme-retro", "theme-arctic", "theme-nature", "theme-ember", "theme-dracula", "theme-midnight"];

const clamp = (n) => Math.max(0, Math.min(255, Math.round(n)));
const hexToRgb = (hex) => {
  const c = (hex || "").replace("#", "");
  const f = c.length === 3 ? c.split("").map((x) => x + x).join("") : c;
  return [parseInt(f.slice(0, 2), 16), parseInt(f.slice(2, 4), 16), parseInt(f.slice(4, 6), 16)];
};
const toHex = ([r, g, b]) => "#" + [r, g, b].map((x) => clamp(x).toString(16).padStart(2, "0")).join("");
const lighten = (hex, a) => { const [r, g, b] = hexToRgb(hex); return toHex([r + (255 - r) * a, g + (255 - g) * a, b + (255 - b) * a]); };
const darken = (hex, a) => { const [r, g, b] = hexToRgb(hex); return toHex([r * (1 - a), g * (1 - a), b * (1 - a)]); };
const rgba = (hex, a) => { const [r, g, b] = hexToRgb(hex); return `rgba(${r},${g},${b},${a})`; };
const isValidHex = (hex) => /^#?[0-9a-fA-F]{6}$/.test(hex || "") || /^#?[0-9a-fA-F]{3}$/.test(hex || "");

const resolveTheme = (theme) =>
  theme === "system"
    ? (typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    : theme;

const applyToBody = (theme, primary) => {
  if (typeof document === "undefined") return;
  const body = document.body;
  body.classList.remove("light-theme", ...THEME_CLASSES);
  const r = resolveTheme(theme);
  if (LIGHT_BASED.includes(r)) body.classList.add("light-theme");
  if (!["light", "dark"].includes(r)) body.classList.add(`theme-${r}`);

  // When a non-default theme OR a custom primary is active, remap hardcoded
  // emerald/green Tailwind utilities to the active accent (see themes.css).
  const themed = !["light", "dark"].includes(r) || (primary && isValidHex(primary));
  body.classList.toggle("has-theme", !!themed);

  // Primary color → override the emerald accent family (inline on body = wins over any rule)
  const s = body.style;
  if (primary && isValidHex(primary)) {
    const p = primary.startsWith("#") ? primary : `#${primary}`;
    s.setProperty("--emerald", p);
    s.setProperty("--emerald-glow", lighten(p, 0.18));
    s.setProperty("--emerald-deep", darken(p, 0.14));
    s.setProperty("--emerald-soft", rgba(p, 0.12));
  } else {
    s.removeProperty("--emerald");
    s.removeProperty("--emerald-glow");
    s.removeProperty("--emerald-deep");
    s.removeProperty("--emerald-soft");
  }
};

const ThemeContext = createContext(null);

export const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(() => {
    const saved = localStorage.getItem("appTheme");
    if (saved && THEME_KEYS.includes(saved)) return saved;
    // legacy key from the old light/dark toggle
    const legacy = localStorage.getItem("lightTheme");
    if (legacy === "0") return "dark";
    return "light";
  });
  const [primary, setPrimaryState] = useState(() => localStorage.getItem("appPrimary") || "");
  const [chosen] = useState(() => localStorage.getItem("appTheme") !== null);

  // First-time visitors: adopt the admin-configured site default.
  useEffect(() => {
    if (chosen) return;
    api.get("/site-settings")
      .then((r) => {
        const dt = r.data?.default_theme;
        const dp = r.data?.default_primary;
        if (dt && THEME_KEYS.includes(dt)) setThemeState(dt);
        if (dp) setPrimaryState(dp);
      })
      .catch(() => {});
  }, [chosen]);

  useEffect(() => { applyToBody(theme, primary); }, [theme, primary]);

  // react to OS change when on "system"
  useEffect(() => {
    if (theme !== "system" || !window.matchMedia) return undefined;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const h = () => applyToBody("system", primary);
    mq.addEventListener?.("change", h);
    return () => mq.removeEventListener?.("change", h);
  }, [theme, primary]);

  const setTheme = useCallback((t) => {
    setThemeState(t);
    localStorage.setItem("appTheme", t);
    localStorage.setItem("lightTheme", LIGHT_BASED.includes(resolveTheme(t)) ? "1" : "0");
  }, []);

  const setPrimary = useCallback((p) => {
    const val = p || "";
    setPrimaryState(val);
    localStorage.setItem("appPrimary", val);
  }, []);

  const toggleLightDark = useCallback(() => {
    setTheme(LIGHT_BASED.includes(resolveTheme(theme)) ? "dark" : "light");
  }, [theme, setTheme]);

  const isLight = LIGHT_BASED.includes(resolveTheme(theme));

  return (
    <ThemeContext.Provider value={{ theme, setTheme, primary, setPrimary, toggleLightDark, isLight }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) return { theme: "light", setTheme: () => {}, primary: "", setPrimary: () => {}, toggleLightDark: () => {}, isLight: true };
  return ctx;
};
