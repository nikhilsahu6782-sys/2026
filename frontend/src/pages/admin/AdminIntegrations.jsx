import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { FaSearch, FaChartLine, FaExternalLinkAlt, FaSave, FaSitemap, FaRobot, FaGoogle, FaWhatsapp, FaTelegram, FaYoutube, FaInstagram, FaMobileAlt, FaComments, FaPalette } from "react-icons/fa";
import { adminApi } from "./adminAuth";
import { BACKEND_URL } from "@/lib/api";

const inputCls =
  "w-full px-3 py-2 rounded border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm text-slate-900 bg-white";

const AdminIntegrations = () => {
  const [form, setForm] = useState({
    ga4_id: "", gsc_verification: "",
    channel_whatsapp: "", channel_telegram: "", channel_arattai: "",
    channel_youtube: "", channel_instagram: "", channel_app: "",
    default_theme: "light", default_primary: "",
  });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    adminApi.get("/site-settings")
      .then((r) => setForm((prev) => ({ ...prev, ...r.data })))
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

      {/* Site Default Theme */}
      <div className="bg-white rounded border border-slate-200 shadow-sm mb-5" data-testid="default-theme-card">
        <div className="px-4 py-3 border-b border-slate-200 font-semibold text-slate-800 flex items-center gap-2"><FaPalette className="text-emerald-600" /> Site Default Theme</div>
        <div className="p-4 space-y-3">
          <p className="text-xs text-slate-500">Naye visitors ko yeh theme default milegi (jab tak woh khud koi theme na chunein). Save karte hi live ho jayegi.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[13px] font-semibold text-slate-700 mb-1">Default Theme</label>
              <select value={form.default_theme || "light"} onChange={(e) => setForm({ ...form, default_theme: e.target.value })} className={inputCls} data-testid="default-theme-select">
                {["light", "dark", "system", "luxury", "retro", "arctic", "nature", "ember", "dracula", "midnight"].map((k) => (
                  <option key={k} value={k}>{k.charAt(0).toUpperCase() + k.slice(1)}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[13px] font-semibold text-slate-700 mb-1">Default Primary Color</label>
              <div className="flex items-center gap-2">
                <input type="color" value={form.default_primary || "#059669"} onChange={(e) => setForm({ ...form, default_primary: e.target.value })} className="w-11 h-10 rounded border border-slate-300 p-0.5 bg-white cursor-pointer" data-testid="default-primary-color" />
                <input value={form.default_primary || ""} onChange={(e) => setForm({ ...form, default_primary: e.target.value })} placeholder="#059669 (blank = theme default)" className={inputCls} data-testid="default-primary-hex" />
                <button type="button" onClick={() => setForm({ ...form, default_primary: "" })} className="px-3 py-2 rounded-lg text-xs font-semibold border border-slate-300 text-slate-600 hover:bg-slate-100 shrink-0" data-testid="default-primary-clear">Clear</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Your Channel Links */}
      <div className="bg-white rounded border border-slate-200 shadow-sm mb-5" data-testid="channel-links-card">
        <div className="px-4 py-3 border-b border-slate-200 font-semibold text-slate-800 flex items-center gap-2"><FaComments className="text-emerald-600" /> Your Channel Links</div>
        <div className="p-4 space-y-3">
          <p className="text-xs text-slate-500">Yeh aapke apne channels hain — har vacancy & post ke neeche "Join Our Channels" me dikhenge. Jo khaali chhodenge woh nahi dikhega. (FreeJobAlert ke promo links ab hata diye gaye hain.)</p>
          {[
            { k: "channel_whatsapp", label: "WhatsApp Channel", icon: FaWhatsapp, ph: "https://whatsapp.com/channel/..." },
            { k: "channel_telegram", label: "Telegram Channel", icon: FaTelegram, ph: "https://t.me/yourchannel" },
            { k: "channel_arattai", label: "Arattai Channel", icon: FaComments, ph: "https://arattai.in/..." },
            { k: "channel_youtube", label: "YouTube Channel", icon: FaYoutube, ph: "https://youtube.com/@yourchannel" },
            { k: "channel_instagram", label: "Instagram", icon: FaInstagram, ph: "https://instagram.com/yourpage" },
            { k: "channel_app", label: "Mobile App Link", icon: FaMobileAlt, ph: "https://play.google.com/store/apps/..." },
          ].map(({ k, label, icon: Icon, ph }) => (
            <div key={k}>
              <label className="block text-[13px] font-semibold text-slate-700 mb-1 flex items-center gap-1.5"><Icon className="text-emerald-600" /> {label}</label>
              <input value={form[k] || ""} onChange={(e) => setForm({ ...form, [k]: e.target.value })} placeholder={ph} className={inputCls} data-testid={`channel-input-${k}`} />
            </div>
          ))}
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
