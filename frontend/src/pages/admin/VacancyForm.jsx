import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { FaSave, FaTimes } from "react-icons/fa";
import { adminApi } from "./adminAuth";
import { computeSeoScore } from "@/lib/utils-seo";
import { buildWhatsAppSummary } from "@/lib/whatsapp";

const CATEGORIES = [
  { key: "haryana", label: "Haryana" },
  { key: "ssc", label: "SSC" },
  { key: "bank", label: "Bank" },
  { key: "railway", label: "Railway" },
  { key: "upsc", label: "UPSC" },
  { key: "police", label: "Police / Defence" },
  { key: "teaching", label: "Teaching" },
  { key: "medical", label: "Medical" },
  { key: "engineering", label: "Engineering" },
  { key: "admit_card", label: "Admit Card" },
  { key: "result", label: "Result" },
  { key: "other", label: "Other" },
];

const STATES = [
  "", "haryana", "delhi", "punjab", "rajasthan", "chandigarh",
  "himachal-pradesh", "uttarakhand", "uttar-pradesh", "madhya-pradesh",
  "bihar", "jharkhand", "gujarat", "maharashtra", "karnataka", "tamil-nadu",
  "kerala", "andhra-pradesh", "telangana", "west-bengal", "odisha",
  "chhattisgarh", "assam", "jammu-kashmir",
];

const QUALIFICATIONS = ["", "10th", "12th", "ITI", "Diploma", "Graduate", "B.Tech/B.E", "Post Graduate"];

const EMPTY = {
  title: "", organization: "", post_name: "", qualification: "",
  category: "other", application_mode: "", state: "",
  last_date_text: "", apply_url: "", description: "",
  total_posts: "", seo_title: "", focus_keyword: "", seo_description: "",
};

/**
 * Slide-over form used for both Create and Edit. `initial` is null when creating,
 * or the existing vacancy object when editing.
 */
const VacancyForm = ({ initial, onClose, onSaved }) => {
  const [f, setF] = useState(EMPTY);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (initial) {
      setF({
        title: initial.title || "",
        organization: initial.organization || "",
        post_name: initial.post_name || "",
        qualification: initial.qualification || "",
        category: initial.category || "other",
        application_mode: initial.application_mode || "",
        state: initial.state || "",
        last_date_text: initial.last_date_text || "",
        apply_url: initial.apply_url || "",
        description: initial.structured?.description || initial.content_html || "",
        total_posts: initial.structured?.total_posts || "",
        seo_title: initial.seo_title || "",
        focus_keyword: initial.focus_keyword || "",
        seo_description: initial.seo_description || "",
      });
    } else {
      setF(EMPTY);
    }
  }, [initial]);

  const upd = (k, v) => setF((prev) => ({ ...prev, [k]: v }));

  const seo = computeSeoScore(f);
  const waPreview = buildWhatsAppSummary({
    title: f.title,
    post_name: f.post_name || f.title,
    qualification: f.qualification,
    last_date_text: f.last_date_text,
    structured: { total_posts: f.total_posts },
    id: initial?.id,
    apply_url: f.apply_url,
  });

  const submit = async (e) => {
    e.preventDefault();
    if (!f.title || f.title.length < 3) {
      toast.error("Title is required (min 3 chars)");
      return;
    }
    setBusy(true);
    try {
      if (initial?.id) {
        await adminApi.put(`/admin/vacancies/${initial.id}`, f);
        toast.success("Vacancy updated");
      } else {
        await adminApi.post("/admin/vacancies", f);
        toast.success("Vacancy created");
      }
      onSaved?.();
      onClose?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Save failed");
    } finally {
      setBusy(false);
    }
  };

  const Field = ({ label, children }) => (
    <label className="block">
      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">{label}</span>
      {children}
    </label>
  );

  const inputCls = "mt-1 w-full px-3 py-2 rounded-lg border border-slate-300 focus:border-emerald-500 outline-none text-sm text-slate-900 bg-white";

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex justify-end" data-testid="vacancy-form-overlay">
      <form
        onSubmit={submit}
        className="w-full max-w-2xl bg-white h-full overflow-y-auto shadow-2xl flex flex-col"
        data-testid="vacancy-form"
      >
        <div className="sticky top-0 bg-white border-b border-slate-200 p-5 flex items-center justify-between z-10">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              {initial ? "Edit Vacancy" : "Add Vacancy"}
            </h2>
            <p className="text-xs text-slate-500">Shown alongside auto-scraped feed</p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50 inline-flex items-center gap-1.5"
              data-testid="vacancy-form-cancel"
            >
              <FaTimes className="text-[10px]" /> Cancel
            </button>
            <button
              type="submit"
              disabled={busy}
              className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 text-white text-xs font-semibold inline-flex items-center gap-1.5"
              data-testid="vacancy-form-save"
            >
              <FaSave className="text-[10px]" /> {busy ? "Saving…" : "Save"}
            </button>
          </div>
        </div>

        <div className="p-5 space-y-4">
          <Field label="Title (required)">
            <input required minLength={3} value={f.title} onChange={(e) => upd("title", e.target.value)}
              className={inputCls} data-testid="vacancy-form-title" />
          </Field>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field label="Organization / Department">
              <input value={f.organization} onChange={(e) => upd("organization", e.target.value)}
                className={inputCls} data-testid="vacancy-form-organization" />
            </Field>
            <Field label="Post Name (defaults to title)">
              <input value={f.post_name} onChange={(e) => upd("post_name", e.target.value)}
                className={inputCls} data-testid="vacancy-form-post_name" />
            </Field>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Category">
              <select value={f.category} onChange={(e) => upd("category", e.target.value)}
                className={inputCls} data-testid="vacancy-form-category">
                {CATEGORIES.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
              </select>
            </Field>
            <Field label="Application Mode">
              <select value={f.application_mode} onChange={(e) => upd("application_mode", e.target.value)}
                className={inputCls} data-testid="vacancy-form-application_mode">
                <option value="">Unknown</option>
                <option value="online">Online</option>
                <option value="offline">Offline</option>
              </select>
            </Field>
            <Field label="State">
              <select value={f.state} onChange={(e) => upd("state", e.target.value)}
                className={inputCls} data-testid="vacancy-form-state">
                {STATES.map((s) => (
                  <option key={s || "any"} value={s}>{s || "— any / none —"}</option>
                ))}
              </select>
            </Field>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Field label="Qualification">
              <select value={f.qualification} onChange={(e) => upd("qualification", e.target.value)}
                className={inputCls} data-testid="vacancy-form-qualification">
                {QUALIFICATIONS.map((q) => (
                  <option key={q || "any"} value={q}>{q || "— any —"}</option>
                ))}
              </select>
            </Field>
            <Field label="Last Date (free-form text, e.g. 15 Sep 2026)">
              <input value={f.last_date_text} onChange={(e) => upd("last_date_text", e.target.value)}
                className={inputCls} data-testid="vacancy-form-last_date_text" />
            </Field>
            <Field label="Total Posts (कुल पद)">
              <input value={f.total_posts} onChange={(e) => upd("total_posts", e.target.value)}
                className={inputCls} placeholder="e.g. 1200" data-testid="vacancy-form-total-posts" />
            </Field>
          </div>
          <Field label="Apply URL (external)">
            <input type="url" value={f.apply_url} onChange={(e) => upd("apply_url", e.target.value)}
              className={inputCls} placeholder="https://example.com/apply" data-testid="vacancy-form-apply_url" />
          </Field>
          <Field label="Description / Notes (plain text or simple HTML)">
            <textarea value={f.description} onChange={(e) => upd("description", e.target.value)}
              rows={8} className={inputCls} data-testid="vacancy-form-description" />
          </Field>

          {/* Rank Math style SEO settings */}
          <div className="rounded-xl border-2 border-slate-200 bg-slate-50 p-4 space-y-3" data-testid="vacancy-form-seo-card">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">SEO Settings (Rank Math Style)</span>
              <span className={`text-sm font-extrabold ${seo.score >= 75 ? "text-green-600" : seo.score >= 45 ? "text-amber-600" : "text-red-500"}`} data-testid="vacancy-form-seo-score">{seo.score}/100</span>
            </div>
            <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className={`h-full transition-all ${seo.score >= 75 ? "bg-green-500" : seo.score >= 45 ? "bg-amber-500" : "bg-red-500"}`} style={{ width: `${seo.score}%` }} />
            </div>
            <Field label="Custom SEO Title">
              <input value={f.seo_title} onChange={(e) => upd("seo_title", e.target.value)}
                className={inputCls} placeholder={f.title || "50-60 chars ideal"} data-testid="vacancy-form-seo-title" />
            </Field>
            <Field label="Focus Keyword">
              <input value={f.focus_keyword} onChange={(e) => upd("focus_keyword", e.target.value)}
                className={inputCls} placeholder="e.g. Haryana Police Bharti 2026" data-testid="vacancy-form-focus-keyword" />
            </Field>
            <Field label="Meta Description">
              <textarea value={f.seo_description} onChange={(e) => upd("seo_description", e.target.value)}
                rows={2} className={inputCls} placeholder="120-160 chars ideal" data-testid="vacancy-form-seo-description" />
            </Field>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-1">
              {seo.checks.map((c, i) => (
                <li key={i} className={`text-[11px] flex items-center gap-1.5 ${c.ok ? "text-green-700" : "text-slate-500"}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${c.ok ? "bg-green-500" : "bg-slate-300"}`} /> {c.label}
                </li>
              ))}
            </ul>
          </div>

          {/* WhatsApp auto-summary preview */}
          <div className="rounded-xl border-2 border-dashed border-[#25D366]/50 bg-green-50 p-4" data-testid="vacancy-form-whatsapp-preview">
            <span className="text-[11px] font-bold uppercase tracking-wider text-green-700">WhatsApp Summary Preview (save par auto-generate hogi)</span>
            <pre className="mt-2 whitespace-pre-wrap font-mono text-xs text-slate-800 leading-relaxed">{waPreview}</pre>
          </div>
        </div>
      </form>
    </div>
  );
};

export default VacancyForm;
