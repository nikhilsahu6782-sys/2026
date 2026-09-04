import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { FaSearch, FaChartLine, FaExternalLinkAlt, FaSave, FaSitemap, FaRobot, FaGoogle } from "react-icons/fa";
import { adminApi } from "./adminAuth";
import { BACKEND_URL } from "@/lib/api";

const inputCls =
  "w-full px-3 py-2 rounded border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm text-slate-900 bg-white";

const AdminIntegrations = () => {
  const [form, setForm] = useState({ ga4_id: "", gsc_verification: "" });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    adminApi.get("/site-settings")
      .then((r) => setForm({ ga4_id: r.data.ga4_id || "", gsc_verification: r.data.gsc_verification || "" }))
      .catch(() => {});
  }, []);

  const save = async () => {
    setBusy(true);
    try { await adminApi.put("/admin/site-settings", form); toast.success("Integration settings saved"); }
    catch (e) { toast.error(e?.response?.data?.detail || "Save failed"); }
    finally { setBusy(false); }
  };

  const LinkBtn = ({ href, icon: Icon, children, testid }) => (
    <a href={href} target="_blank" rel="noreferrer" data-testid={testid}
      className="inline-flex items-center gap-2 px-3 py-2 rounded border border-blue-600 text-blue-700 text-[13px] font-semibold hover:bg-blue-50">
      <Icon /> {children} <FaExternalLinkAlt className="text-[10px] opacity-70" />
    </a>
  );

  return (
    <div data-testid="admin-integrations-page" className="max-w-3xl">
      <h1 className="text-[23px] font-normal text-slate-800 mb-1 flex items-center gap-2"><FaGoogle className="text-blue-600" /> Analytics &amp; SEO</h1>
      <p className="text-sm text-slate-500 mb-5">Google Search Console aur Analytics connect karke site ko monitor karein.</p>

      {/* Google Search Console */}
      <div className="bg-white rounded border border-slate-200 shadow-sm mb-5">
        <div className="px-4 py-3 border-b border-slate-200 font-semibold text-slate-800 flex items-center gap-2"><FaSearch className="text-blue-600" /> Google Search Console</div>
        <div className="p-4 space-y-3">
          <div>
            <label className="block text-[13px] font-semibold text-slate-700 mb-1">Verification code / meta tag</label>
            <textarea rows={2} value={form.gsc_verification} onChange={(e) => setForm({ ...form, gsc_verification: e.target.value })}
              placeholder='Paste the full <meta name="google-site-verification" ...> tag OR just the content value'
              className={inputCls} data-testid="gsc-input" />
            <p className="text-xs text-slate-400 mt-1">Search Console → Add property → "HTML tag" method. Poora tag ya sirf content value paste karein — save ke baad site head me lag jaayega.</p>
          </div>
          <LinkBtn href="https://search.google.com/search-console" icon={FaSearch} testid="gsc-dashboard-link">Open Search Console</LinkBtn>
        </div>
      </div>

      {/* Google Analytics */}
      <div className="bg-white rounded border border-slate-200 shadow-sm mb-5">
        <div className="px-4 py-3 border-b border-slate-200 font-semibold text-slate-800 flex items-center gap-2"><FaChartLine className="text-blue-600" /> Google Analytics (GA4)</div>
        <div className="p-4 space-y-3">
          <div>
            <label className="block text-[13px] font-semibold text-slate-700 mb-1">Measurement ID</label>
            <input value={form.ga4_id} onChange={(e) => setForm({ ...form, ga4_id: e.target.value })}
              placeholder="G-XXXXXXXXXX" className={inputCls} data-testid="ga4-input" />
            <p className="text-xs text-slate-400 mt-1">Analytics → Admin → Data Streams → Web → Measurement ID (G-…). Save ke baad visitor tracking auto shuru ho jaayega.</p>
          </div>
          <LinkBtn href="https://analytics.google.com/" icon={FaChartLine} testid="ga-dashboard-link">Open Google Analytics</LinkBtn>
        </div>
      </div>

      <button onClick={save} disabled={busy}
        className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-60 mb-6"
        data-testid="integrations-save">
        <FaSave /> {busy ? "Saving…" : "Save settings"}
      </button>

      {/* SEO tools */}
      <div className="bg-white rounded border border-slate-200 shadow-sm">
        <div className="px-4 py-3 border-b border-slate-200 font-semibold text-slate-800 flex items-center gap-2"><FaSitemap className="text-blue-600" /> SEO Tools (auto-generated)</div>
        <div className="p-4 flex flex-wrap gap-2">
          <LinkBtn href={`${BACKEND_URL}/api/sitemap-vacancies.xml`} icon={FaSitemap} testid="sitemap-link">View sitemap.xml</LinkBtn>
          <LinkBtn href={`${BACKEND_URL}/api/robots.txt`} icon={FaRobot} testid="robots-link">View robots.txt</LinkBtn>
        </div>
        <p className="px-4 pb-4 text-xs text-slate-400">Search Console me sitemap submit karein: <b className="text-slate-600">{`${BACKEND_URL}/api/sitemap-vacancies.xml`}</b> — ismein saari vacancies auto add hoti hain.</p>
      </div>
    </div>
  );
};

export default AdminIntegrations;
