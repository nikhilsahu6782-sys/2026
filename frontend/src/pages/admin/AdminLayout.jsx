import React, { useState } from "react";
import { Outlet, Link, NavLink, useNavigate, Navigate } from "react-router-dom";
import {
  FaTachometerAlt, FaThumbtack, FaSearch, FaEdit, FaSignOutAlt, FaHome,
  FaExternalLinkAlt, FaBriefcase, FaNewspaper, FaFileAlt, FaBars, FaWordpress, FaUserCircle, FaChartLine, FaImages, FaStar
} from "react-icons/fa";
import { getAdminToken, clearAdminToken } from "./adminAuth";

const AdminLayout = () => {
  const nav = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  if (!getAdminToken()) return <Navigate to="/admin/login" replace />;

  const logout = () => {
    clearAdminToken();
    nav("/admin/login", { replace: true });
  };

  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-2.5 text-[13px] font-medium transition-colors border-l-[3px] ${
      isActive
        ? "bg-[#059669] text-white border-white"
        : "text-[#c3c4c7] border-transparent hover:text-white hover:bg-white/5"
    }`;

  const items = [
    { to: "/admin", end: true, label: "Dashboard", icon: FaTachometerAlt, testid: "admin-nav-dashboard" },
    { to: "/admin/blogs", label: "Posts", icon: FaThumbtack, testid: "admin-nav-blogs" },
    { to: "/admin/reviews", label: "Reviews", icon: FaStar, testid: "admin-nav-reviews" },
    { to: "/admin/slides", label: "News Slider", icon: FaImages, testid: "admin-nav-slides" },
    { to: "/admin/vacancies", label: "Vacancies", icon: FaBriefcase, testid: "admin-nav-vacancies" },
    { to: "/admin/job-seo", label: "Job SEO", icon: FaSearch, testid: "admin-nav-job-seo" },
    { to: "/admin/resumes", label: "CV Templates", icon: FaFileAlt, testid: "admin-nav-resumes" },
    { to: "/admin/seo", label: "Site SEO", icon: FaNewspaper, testid: "admin-nav-seo" },
    { to: "/admin/integrations", label: "Analytics & SEO", icon: FaChartLine, testid: "admin-nav-integrations" },
    { to: "/admin/content", label: "Front-page Text", icon: FaEdit, testid: "admin-nav-content" },
  ];

  return (
    <div className="min-h-screen bg-[#f0f0f1]" data-testid="admin-layout">
      {/* Top admin bar */}
      <header className="fixed top-0 inset-x-0 h-11 bg-[#1d2327] text-[#c3c4c7] flex items-center px-3 gap-3 z-50 text-[13px]">
        <button onClick={() => setCollapsed((c) => !c)} className="p-1.5 rounded hover:bg-white/10 md:hidden" data-testid="admin-sidebar-toggle">
          <FaBars />
        </button>
        <span className="flex items-center gap-2 font-semibold text-white">
          <FaWordpress className="text-lg" /> HR Digital Services
        </span>
        <a href="/" target="_blank" rel="noreferrer" className="hidden sm:inline-flex items-center gap-1.5 hover:text-white" data-testid="admin-topbar-view-site">
          <FaHome /> Visit Site
        </a>
        <div className="ml-auto flex items-center gap-2">
          <span className="hidden sm:inline">Howdy, <b className="text-white">Admin</b></span>
          <FaUserCircle className="text-xl text-white/80" />
        </div>
      </header>

      <div className="flex pt-11">
        {/* Sidebar */}
        <aside className={`${collapsed ? "hidden" : "flex"} md:flex flex-col fixed md:sticky top-11 left-0 h-[calc(100vh-2.75rem)] w-[200px] bg-[#1e293b] shrink-0 z-40 overflow-y-auto`}>
          <nav className="flex-1 py-3" data-testid="admin-nav">
            {items.map((it) => (
              <NavLink key={it.to} to={it.to} end={it.end} className={linkClass} data-testid={it.testid} onClick={() => setCollapsed(false)}>
                <it.icon className="text-[15px] w-4 shrink-0" /> {it.label}
              </NavLink>
            ))}
          </nav>
          <div className="border-t border-white/10 py-2">
            <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-2.5 text-[13px] font-medium text-red-300 hover:text-white hover:bg-red-500/20 transition-colors" data-testid="admin-logout">
              <FaSignOutAlt className="w-4" /> Logout
            </button>
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 min-w-0 p-4 md:p-6" data-testid="admin-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
