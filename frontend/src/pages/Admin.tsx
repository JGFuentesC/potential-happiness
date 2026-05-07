import { useEffect, useState, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { CheckCircle, XCircle, Save, AlertTriangle } from "lucide-react";
import { adminApi, usersApi } from "@/api/client";
import type { AdminUser, Match } from "@/types";
import { matchesApi } from "@/api/client";

interface OutletCtx { simulatedTime: string | null }

// ── Confirmation modal ────────────────────────────────────────────────────────
interface ConfirmModalProps {
  match: Match;
  home: string;
  away: string;
  onConfirm: () => void;
  onCancel: () => void;
  affectedCount: number;
}
function ConfirmModal({ match, home, away, onConfirm, onCancel, affectedCount }: ConfirmModalProps) {
  const homeName = match.home_team ?? match.home_team_placeholder ?? "?";
  const awayName = match.away_team ?? match.away_team_placeholder ?? "?";
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#13111f] border border-[#ff2d78]/30 rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl">
        <div className="flex items-center gap-3 mb-4">
          <AlertTriangle className="text-[#ffe04a] shrink-0" size={22} />
          <h2 className="text-white font-bold text-lg" style={{ fontFamily: "Sora, sans-serif" }}>
            Confirmar corrección
          </h2>
        </div>
        <p className="text-[#9b8ec4] text-sm mb-4">
          Estás modificando el resultado de{" "}
          <span className="text-white font-medium">{homeName} vs {awayName}</span>{" "}
          a <span className="text-[#ff2d78] font-bold">{home} — {away}</span>.
        </p>
        <div className="bg-[#ffe04a]/10 border border-[#ffe04a]/20 rounded px-4 py-3 mb-6 text-sm text-[#ffe04a]">
          Esto recalculará los puntos de <strong>{affectedCount}</strong> participante(s). Esta acción no se puede deshacer.
        </div>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-5 py-2 border border-[#302840] text-[#9b8ec4] rounded text-sm hover:text-white transition-colors"
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            Cancelar
          </button>
          <button
            id="btn-confirm-result"
            onClick={onConfirm}
            className="px-5 py-2 bg-[#ff2d78] text-white rounded text-sm font-bold hover:bg-[#e0255e] transition-colors"
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            Confirmar y Recalcular
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Users Tab ─────────────────────────────────────────────────────────────────
function UsersTab() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [filter, setFilter] = useState<"Pending" | "Active" | "Rejected">("Pending");
  const [loading, setLoading] = useState(true);
  const [actioning, setActioning] = useState<number | null>(null);
  const [pendingCount, setPendingCount] = useState(0);

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([
      adminApi.listUsers(filter),
      adminApi.listUsers("Pending"),
    ]).then(([res, pending]) => {
      setUsers(res.data);
      setPendingCount(pending.data.length);
    }).finally(() => setLoading(false));
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  const approve = async (id: number) => {
    setActioning(id);
    try { await adminApi.approveUser(id); load(); }
    finally { setActioning(null); }
  };

  const reject = async (id: number) => {
    setActioning(id);
    try { await adminApi.rejectUser(id); load(); }
    finally { setActioning(null); }
  };

  const statusBadge = (s: string) => {
    const map: Record<string, string> = {
      Pending:  "bg-[#ffe04a]/10 text-[#ffe04a] border-[#ffe04a]/30",
      Active:   "bg-[#00ffcc]/10 text-[#00ffcc] border-[#00ffcc]/30",
      Rejected: "bg-red-500/10 text-red-400 border-red-500/20",
    };
    return (
      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${map[s] ?? ""}`}
        style={{ fontFamily: "Space Grotesk, sans-serif" }}>
        {s}
      </span>
    );
  };

  return (
    <div>
      {/* Filter tabs */}
      <div className="flex gap-2 mb-6">
        {(["Pending", "Active", "Rejected"] as const).map((f) => (
          <button
            key={f}
            id={`filter-${f}`}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 text-xs font-medium rounded border transition-all relative ${
              filter === f
                ? "border-[#ff2d78]/50 text-[#ff2d78] bg-[#ff2d78]/10"
                : "border-[#302840] text-[#9b8ec4] hover:text-white"
            }`}
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            {f}
            {f === "Pending" && pendingCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 h-4 w-4 bg-[#ff2d78] text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                {pendingCount}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-[#141422] rounded-xl border border-[#302840]/60 overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="text-[#9b8ec4] text-xs uppercase tracking-widest border-b border-[#302840]" style={{ background: "#1e1e30", fontFamily: "Space Grotesk, sans-serif" }}>
            <tr>
              <th className="p-4">Usuario</th>
              <th className="p-4 hidden md:table-cell text-center">Estado</th>
              <th className="p-4 hidden md:table-cell text-center">Puntos</th>
              <th className="p-4 hidden md:table-cell">Registro</th>
              <th className="p-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#302840]/30">
            {loading
              ? Array.from({ length: 3 }).map((_, i) => (
                  <tr key={i}><td colSpan={5} className="p-4"><div className="h-8 bg-[#1e1e30] rounded animate-pulse" /></td></tr>
                ))
              : users.length === 0
              ? (
                  <tr><td colSpan={5} className="p-12 text-center text-[#9b8ec4] text-xs uppercase tracking-widest">
                    Sin usuarios con estado {filter}.
                  </td></tr>
                )
              : users.map((u) => (
                  <tr key={u.id} className="hover:bg-[#1e1e30]/60 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-[#28283e] border border-[#302840] flex items-center justify-center text-white text-xs font-bold">
                          {u.username[0].toUpperCase()}
                        </div>
                        <span className="text-white font-medium" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                          {u.username}
                        </span>
                      </div>
                    </td>
                    <td className="p-4 hidden md:table-cell text-center">{statusBadge(u.status)}</td>
                    <td className="p-4 hidden md:table-cell text-center text-[#9b8ec4]">{u.total_points}</td>
                    <td className="p-4 hidden md:table-cell text-[#9b8ec4] text-xs">
                      {new Date(u.created_at).toLocaleDateString("es-MX")}
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex gap-2 justify-end">
                        {u.status !== "Active" && (
                          <button
                            id={`btn-approve-${u.id}`}
                            onClick={() => approve(u.id)}
                            disabled={actioning === u.id}
                            className="flex items-center gap-1 px-3 py-1.5 text-[#00ffcc] border border-[#00ffcc]/30 rounded text-xs hover:bg-[#00ffcc]/10 transition-colors disabled:opacity-50"
                          >
                            <CheckCircle size={12} /> Aprobar
                          </button>
                        )}
                        {u.status !== "Rejected" && (
                          <button
                            id={`btn-reject-${u.id}`}
                            onClick={() => reject(u.id)}
                            disabled={actioning === u.id}
                            className="flex items-center gap-1 px-3 py-1.5 text-red-400 border border-red-500/20 rounded text-xs hover:bg-red-500/10 transition-colors disabled:opacity-50"
                          >
                            <XCircle size={12} /> Rechazar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
            }
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Matches Tab ───────────────────────────────────────────────────────────────
function MatchesTab() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [scores, setScores] = useState<Record<number, { home: string; away: string }>>({});
  const [saving, setSaving] = useState<number | null>(null);
  const [confirm, setConfirm] = useState<{ match: Match; home: string; away: string } | null>(null);
  const [totalUsers, setTotalUsers] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [mRes, uRes] = await Promise.all([
        matchesApi.list({ phase: "Groups" }),
        usersApi.ranking(),
      ]);
      setMatches(mRes.data);
      setTotalUsers(uRes.data.length);
      const init: Record<number, { home: string; away: string }> = {};
      mRes.data.forEach((m) => {
        init[m.id] = {
          home: m.home_score_final?.toString() ?? "",
          away: m.away_score_final?.toString() ?? "",
        };
      });
      setScores(init);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSave = (match: Match) => {
    const s = scores[match.id];
    if (!s || s.home === "" || s.away === "") return;
    // If already has result, show confirmation
    if (match.home_score_final != null) {
      setConfirm({ match, home: s.home, away: s.away });
    } else {
      doSave(match, s.home, s.away);
    }
  };

  const doSave = async (match: Match, home: string, away: string) => {
    setSaving(match.id);
    setConfirm(null);
    try {
      if (match.home_score_final != null) {
        await adminApi.correctResult(match.id, { home_score_final: Number(home), away_score_final: Number(away) });
      } else {
        await adminApi.setResult(match.id, { home_score_final: Number(home), away_score_final: Number(away) });
      }
      load();
    } finally {
      setSaving(null);
    }
  };

  const statusDot = (m: Match) => {
    if (m.status === "Finished") return <span className="inline-flex items-center gap-1 text-[10px] text-[#9b8ec4] border border-[#302840] px-2 py-0.5 rounded-full"><CheckCircle size={10} />FT</span>;
    if (m.status === "Locked")   return <span className="inline-flex items-center gap-1 text-[10px] text-[#ff2d78] border border-[#ff2d78]/30 px-2 py-0.5 rounded-full"><span className="w-1.5 h-1.5 rounded-full bg-[#ff2d78] animate-pulse" />Locked</span>;
    return <span className="text-[10px] text-[#9b8ec4]">{new Date(m.start_time).toLocaleString("es-MX", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>;
  };

  return (
    <>
      {confirm && (
        <ConfirmModal
          match={confirm.match}
          home={confirm.home}
          away={confirm.away}
          affectedCount={totalUsers}
          onConfirm={() => doSave(confirm.match, confirm.home, confirm.away)}
          onCancel={() => setConfirm(null)}
        />
      )}

      <div className="bg-[#141422] rounded-xl border border-[#ff2d78]/20 overflow-hidden">
        {/* Top gradient line */}
        <div className="h-px w-full bg-gradient-to-r from-transparent via-[#ff2d78]/40 to-transparent" />

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-[#9b8ec4] text-xs uppercase tracking-widest border-b border-[#302840]"
              style={{ background: "#1e1e30", fontFamily: "Space Grotesk, sans-serif" }}>
              <tr>
                <th className="p-4">Estado</th>
                <th className="p-4">Partido</th>
                <th className="p-4 text-center">Resultado Final</th>
                <th className="p-4 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#302840]/20">
              {loading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i}><td colSpan={4} className="p-4"><div className="h-10 bg-[#1e1e30] rounded animate-pulse" /></td></tr>
                  ))
                : matches.map((m) => {
                    const homeName = m.home_team ?? m.home_team_placeholder ?? "TBD";
                    const awayName = m.away_team ?? m.away_team_placeholder ?? "TBD";
                    const s = scores[m.id] ?? { home: "", away: "" };
                    const isDone = m.status === "Finished";

                    return (
                      <tr key={m.id} className={`hover:bg-[#1e1e30]/60 transition-colors group ${isDone ? "opacity-60 hover:opacity-100" : ""}`}>
                        <td className="p-4">{statusDot(m)}</td>
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <span className="font-medium text-white group-hover:text-[#00ffcc] transition-colors w-20 text-right" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                              {homeName}
                            </span>
                            <span className="text-[#9b8ec4] text-xs">vs</span>
                            <span className="font-medium text-white group-hover:text-[#00ffcc] transition-colors w-20" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                              {awayName}
                            </span>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center justify-center gap-2">
                            {isDone && m.home_score_final != null ? (
                              // Editable even when finished (correction)
                              <>
                                <input
                                  id={`admin-home-${m.id}`}
                                  type="number" min={0}
                                  value={s.home}
                                  onChange={(e) => setScores((sc) => ({ ...sc, [m.id]: { ...sc[m.id], home: e.target.value } }))}
                                  className="w-12 h-9 bg-[#0e0d14] border-b border-[#5a5068] text-center text-lg font-bold text-white focus:border-[#ff2d78] focus:outline-none transition-colors rounded-t"
                                  style={{ fontFamily: "Sora, sans-serif" }}
                                />
                                <span className="text-[#9b8ec4]">–</span>
                                <input
                                  id={`admin-away-${m.id}`}
                                  type="number" min={0}
                                  value={s.away}
                                  onChange={(e) => setScores((sc) => ({ ...sc, [m.id]: { ...sc[m.id], away: e.target.value } }))}
                                  className="w-12 h-9 bg-[#0e0d14] border-b border-[#5a5068] text-center text-lg font-bold text-white focus:border-[#ff2d78] focus:outline-none transition-colors rounded-t"
                                  style={{ fontFamily: "Sora, sans-serif" }}
                                />
                              </>
                            ) : (
                              <>
                                <input
                                  id={`admin-home-${m.id}`}
                                  type="number" min={0}
                                  value={s.home}
                                  onChange={(e) => setScores((sc) => ({ ...sc, [m.id]: { ...sc[m.id], home: e.target.value } }))}
                                  placeholder="–"
                                  className="w-12 h-9 bg-[#0e0d14] border-b border-[#5a5068] text-center text-lg font-bold text-white focus:border-[#ff2d78] focus:outline-none transition-colors rounded-t placeholder:text-[#302840]"
                                  style={{ fontFamily: "Sora, sans-serif" }}
                                />
                                <span className="text-[#9b8ec4]">–</span>
                                <input
                                  id={`admin-away-${m.id}`}
                                  type="number" min={0}
                                  value={s.away}
                                  onChange={(e) => setScores((sc) => ({ ...sc, [m.id]: { ...sc[m.id], away: e.target.value } }))}
                                  placeholder="–"
                                  className="w-12 h-9 bg-[#0e0d14] border-b border-[#5a5068] text-center text-lg font-bold text-white focus:border-[#ff2d78] focus:outline-none transition-colors rounded-t placeholder:text-[#302840]"
                                  style={{ fontFamily: "Sora, sans-serif" }}
                                />
                              </>
                            )}
                          </div>
                        </td>
                        <td className="p-4 text-right">
                          <button
                            id={`btn-save-result-${m.id}`}
                            onClick={() => handleSave(m)}
                            disabled={saving === m.id || s.home === "" || s.away === ""}
                            className={`p-2 transition-colors disabled:opacity-30 ${isDone ? "text-[#9b8ec4] hover:text-[#00ffcc]" : "text-[#9b8ec4] hover:text-[#ff2d78]"}`}
                            title={isDone ? "Corregir resultado" : "Guardar resultado"}
                          >
                            <Save size={18} />
                          </button>
                        </td>
                      </tr>
                    );
                  })
              }
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

// ── Admin Page ────────────────────────────────────────────────────────────────
export default function Admin() {
  const { simulatedTime } = useOutletContext<OutletCtx>();
  const [tab, setTab] = useState<"users" | "matches">("users");

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto">
      {/* Ambient */}
      <div className="pointer-events-none fixed inset-0 bg-gradient-to-b from-[#ff2d78]/4 to-transparent -z-10" />

      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-1" style={{ fontFamily: "Sora, sans-serif" }}>
            Panel <span className="text-[#ff2d78]">Admin</span>
          </h1>
          <p className="text-[#9b8ec4] text-sm" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
            Gestión de usuarios y resultados.
            {simulatedTime && (
              <span className="ml-2 text-[#7b2ffb] font-medium">[Time Travel: {new Date(simulatedTime).toLocaleString("es-MX")}]</span>
            )}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#1e1e30] p-1 rounded border border-[#302840]/30 w-fit mb-6">
        {(["users", "matches"] as const).map((t) => (
          <button
            key={t}
            id={`admin-tab-${t}`}
            onClick={() => setTab(t)}
            className={`px-6 py-2 text-xs font-medium uppercase tracking-wider rounded transition-all duration-150 ${
              tab === t
                ? "bg-[#ff2d78]/15 text-[#ff2d78] border border-[#ff2d78]/30"
                : "text-[#9b8ec4] hover:text-white"
            }`}
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            {t === "users" ? "Usuarios" : "Partidos"}
          </button>
        ))}
      </div>

      {/* Content */}
      {tab === "users" ? <UsersTab /> : <MatchesTab />}
    </div>
  );
}
