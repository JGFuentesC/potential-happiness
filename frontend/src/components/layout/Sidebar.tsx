import { NavLink, useNavigate } from "react-router-dom";
import {
  Swords,
  Trophy,
  Star,
  ShieldCheck,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";

const navItems = [
  { to: "/matches", label: "Partidos", icon: Swords },
  { to: "/leaderboard", label: "Clasificación", icon: Trophy },
  { to: "/bonus", label: "Bonus", icon: Star },
];

export default function Sidebar() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="px-6 pt-6 pb-4 border-b border-[#3d2f6e]/40">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">⚽</span>
          <div>
            <span
              className="text-base font-bold"
              style={{ fontFamily: "Sora, sans-serif", color: "#ff2d78" }}
            >
              Quiniela
            </span>
            <span
              className="text-base font-bold text-white ml-1"
              style={{ fontFamily: "Sora, sans-serif" }}
            >
              2026
            </span>
            <p className="text-[10px] text-[#9b8ec4] leading-none mt-0.5">
              Mundial Norteamérica
            </p>
          </div>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-all duration-150 ${
                isActive
                  ? "text-white border-l-2 border-[#ff2d78] bg-[#ff2d78]/10 pl-[10px]"
                  : "text-[#9b8ec4] hover:text-white hover:bg-white/5 border-l-2 border-transparent"
              }`
            }
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            <Icon size={16} strokeWidth={2} />
            {label}
          </NavLink>
        ))}

        {/* Admin section */}
        {user?.is_admin && (
          <>
            <div className="pt-4 pb-1 px-3">
              <span className="text-[10px] uppercase tracking-widest text-[#4a3f6b] font-medium">
                Admin
              </span>
            </div>
            <NavLink
              to="/admin"
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? "text-[#a78bfa] border-l-2 border-[#7b2ffb] bg-[#7b2ffb]/10 pl-[10px]"
                    : "text-[#9b8ec4] hover:text-[#a78bfa] hover:bg-white/5 border-l-2 border-transparent"
                }`
              }
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              <ShieldCheck size={16} strokeWidth={2} />
              Panel Admin
            </NavLink>
          </>
        )}
      </nav>

      {/* User footer */}
      <div className="px-4 py-4 border-t border-[#3d2f6e]/40">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p
              className="text-sm font-medium text-white truncate"
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              {user?.username}
            </p>
            <p className="text-[11px] text-[#9b8ec4]">
              {user?.total_points ?? 0} pts
            </p>
          </div>
          <button
            id="btn-logout"
            onClick={handleLogout}
            className="p-2 text-[#9b8ec4] hover:text-[#ff2d78] transition-colors rounded hover:bg-white/5"
            title="Cerrar sesión"
          >
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-64 shrink-0 h-screen sticky top-0 bg-[#0a0912] border-r border-[#3d2f6e]/30">
        <SidebarContent />
      </aside>

      {/* Mobile hamburger */}
      <button
        id="btn-mobile-menu"
        onClick={() => setMobileOpen(true)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-[#13111f] border border-[#3d2f6e]/60 rounded text-[#9b8ec4] hover:text-white"
      >
        <Menu size={18} />
      </button>

      {/* Mobile drawer */}
      {mobileOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="md:hidden fixed left-0 top-0 bottom-0 z-50 w-64 bg-[#0a0912] border-r border-[#3d2f6e]/30">
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-4 p-1 text-[#9b8ec4] hover:text-white"
            >
              <X size={18} />
            </button>
            <SidebarContent />
          </aside>
        </>
      )}
    </>
  );
}
