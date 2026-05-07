import { useEffect, useState, useCallback } from "react";
import { useOutletContext } from "react-router-dom";
import { Calendar, Lock, CheckCircle, Clock, Save } from "lucide-react";
import { matchesApi, predictionsApi } from "@/api/client";
import type { Match } from "@/types";

interface OutletCtx { simulatedTime: string | null }

// ── FlagAvatar ────────────────────────────────────────────────────────────────
function FlagAvatar({ code, name }: { code: string | null; name: string }) {
  if (code) {
    return (
      <img
        src={`https://flagcdn.com/w80/${code.toLowerCase()}.png`}
        alt={name}
        className="w-16 h-16 object-cover rounded-full border-2 border-[#302840]"
        onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
      />
    );
  }
  return (
    <div className="w-16 h-16 rounded-full border-2 border-[#302840] bg-[#141422] flex items-center justify-center text-[#9b8ec4] text-xs font-bold">
      {name.slice(0, 3)}
    </div>
  );
}

// ── StatusBadge ───────────────────────────────────────────────────────────────
function StatusBadge({ status }: { status: Match["status"] }) {
  const map = {
    Open:           { label: "Open",          cls: "text-[#ff2d78] bg-[#ff2d78]/10 border-[#ff2d78]/30" },
    Locked:         { label: "Locked",        cls: "text-[#9b8ec4] bg-[#302840]/50 border-[#302840]" },
    Finished:       { label: "Final",         cls: "text-[#00ffcc] bg-[#00ffcc]/10 border-[#00ffcc]/30" },
    "Pending Teams":{ label: "Pending Teams", cls: "text-[#9b8ec4] bg-[#1e1e30]/50 border-[#302840]" },
  };
  const { label, cls } = map[status];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest border ${cls}`}
      style={{ fontFamily: "Space Grotesk, sans-serif" }}>
      {status === "Locked" && <Lock size={9} />}
      {status === "Finished" && <CheckCircle size={9} />}
      {status === "Open" && <span className="w-1.5 h-1.5 rounded-full bg-[#ff2d78] animate-pulse" />}
      {label}
    </span>
  );
}

// ── MatchCard ─────────────────────────────────────────────────────────────────
interface MatchCardProps {
  match: Match;
  simulatedTime: string | null;
  onSaved: () => void;
}

function MatchCard({ match, simulatedTime, onSaved }: MatchCardProps) {
  const [home, setHome] = useState<string>(match.my_prediction?.home_score_guess?.toString() ?? "");
  const [away, setAway] = useState<string>(match.my_prediction?.away_score_guess?.toString() ?? "");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const homeName = match.home_team ?? match.home_team_placeholder ?? "TBD";
  const awayName = match.away_team ?? match.away_team_placeholder ?? "TBD";
  const isOpen = match.status === "Open";

  const cardBorder =
    match.status === "Open"     ? "border-[#ff2d78]/40 shadow-[inset_0_0_20px_rgba(255,45,120,0.05)]"
  : match.status === "Finished" ? "border-[#00ffcc]/20"
  : "border-[#302840]/60";

  const handleSave = async () => {
    if (!isOpen || home === "" || away === "") return;
    setSaving(true);
    setError(null);
    try {
      await predictionsApi.upsert({
        match_id: match.id,
        home_score_guess: Number(home),
        away_score_guess: Number(away),
        ...(simulatedTime ? { simulated_time: simulatedTime } : {}),
      });
      setSaved(true);
      onSaved();
      setTimeout(() => setSaved(false), 2000);
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg ?? "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const inputCls = `w-14 h-14 text-center text-2xl font-bold rounded-t border-b-2 bg-[#28283e] focus:outline-none transition-colors
    ${isOpen ? "border-[#ff2d78] text-[#ff2d78] focus:bg-[#1a1a2e]" : "border-[#302840] text-[#9b8ec4] cursor-not-allowed"}`;

  return (
    <div className={`relative bg-[#141422] rounded-lg p-5 border overflow-hidden group transition-all duration-300 ${cardBorder} ${!isOpen ? "opacity-70" : ""}`}>
      {/* Hover gradient */}
      {isOpen && (
        <div className="absolute inset-0 bg-gradient-to-br from-[#ff2d78]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      )}
      {/* Saved glow animation */}
      {saved && (
        <div className="absolute inset-0 rounded-lg border border-[#00ffcc] shadow-[0_0_20px_rgba(0,255,204,0.3)] animate-pulse pointer-events-none transition-all" />
      )}

      {/* Group + status badges */}
      <div className="flex justify-between items-center mb-3">
        {match.group_name && (
          <span className="text-[10px] uppercase tracking-widest text-[#00ffcc]"
            style={{ fontFamily: "Space Grotesk, sans-serif" }}>
            {match.group_name}
          </span>
        )}
        <div className="ml-auto"><StatusBadge status={match.status} /></div>
      </div>

      {/* Teams + Score row */}
      <div className="flex items-center justify-between gap-2 mt-2">
        {/* Home team */}
        <div className="flex flex-col items-center gap-2 w-1/3">
          <FlagAvatar code={match.home_team_code} name={homeName} />
          <span className="font-bold text-sm text-white text-center" style={{ fontFamily: "Sora, sans-serif" }}>
            {homeName}
          </span>
          {match.status === "Finished" && (
            <span className="text-xs text-[#00ffcc] font-bold">{match.home_score_final}</span>
          )}
        </div>

        {/* Score inputs */}
        <div className="flex items-center gap-2 w-1/3 justify-center">
          <input
            id={`home-score-${match.id}`}
            type="number" min={0} max={99}
            value={home}
            onChange={(e) => isOpen && setHome(e.target.value)}
            placeholder="–"
            disabled={!isOpen}
            className={inputCls}
            style={{ fontFamily: "Sora, sans-serif" }}
          />
          <span className="text-[#9b8ec4] text-xs" style={{ fontFamily: "Space Grotesk, sans-serif" }}>VS</span>
          <input
            id={`away-score-${match.id}`}
            type="number" min={0} max={99}
            value={away}
            onChange={(e) => isOpen && setAway(e.target.value)}
            placeholder="–"
            disabled={!isOpen}
            className={inputCls.replace("border-[#ff2d78] text-[#ff2d78]", "border-[#00ffcc] text-[#00ffcc]")}
            style={{ fontFamily: "Sora, sans-serif" }}
          />
        </div>

        {/* Away team */}
        <div className="flex flex-col items-center gap-2 w-1/3">
          <FlagAvatar code={match.away_team_code} name={awayName} />
          <span className="font-bold text-sm text-white text-center" style={{ fontFamily: "Sora, sans-serif" }}>
            {awayName}
          </span>
          {match.status === "Finished" && (
            <span className="text-xs text-[#00ffcc] font-bold">{match.away_score_final}</span>
          )}
        </div>
      </div>

      {/* Footer: date + points + save */}
      <div className="flex justify-between items-center mt-4 pt-3 border-t border-[#302840]/50">
        <div className="flex items-center gap-1.5 text-[#9b8ec4] text-xs" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
          <Calendar size={12} />
          {new Date(match.start_time).toLocaleString("es-MX", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
        </div>

        <div className="flex items-center gap-2">
          {match.my_prediction?.points_earned != null && (
            <span className="text-xs font-bold text-[#00ffcc]">+{match.my_prediction.points_earned} pts</span>
          )}
          {isOpen && (
            <button
              id={`btn-save-${match.id}`}
              onClick={handleSave}
              disabled={saving || home === "" || away === ""}
              className={`flex items-center gap-1.5 px-4 py-1.5 border text-xs font-bold uppercase tracking-wider transition-all duration-200 rounded
                ${saved
                  ? "border-[#00ffcc]/50 text-[#00ffcc] bg-[#00ffcc]/10"
                  : "border-[#ff2d78]/50 text-[#ff2d78] bg-transparent hover:bg-[#ff2d78]/10 hover:shadow-[0_0_16px_rgba(255,45,120,0.3)] disabled:opacity-40"
                }`}
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              {saving ? <Clock size={12} className="animate-spin" /> : <Save size={12} />}
              {saved ? "Saved!" : "Save"}
            </button>
          )}
        </div>
      </div>

      {error && <p className="text-red-400 text-xs mt-2">{error}</p>}
    </div>
  );
}

// ── Matches Page ──────────────────────────────────────────────────────────────
export default function Matches() {
  const { simulatedTime } = useOutletContext<OutletCtx>();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [matchday, setMatchday] = useState(1);
  const [phase, setPhase] = useState("Groups");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = { phase };
      if (simulatedTime) params.simulated_time = simulatedTime;
      const { data } = await matchesApi.list(params);
      setMatches(data);
    } finally {
      setLoading(false);
    }
  }, [phase, simulatedTime]);

  useEffect(() => { load(); }, [load]);

  const grouped = matches.filter((m) => m.matchday === matchday);
  const phases = ["Groups", "R32", "R16", "QF", "SF", "ThirdPlace", "Final"];
  const phaseLabels: Record<string, string> = {
    Groups: "Fase de Grupos", R32: "Ronda de 32", R16: "Octavos", QF: "Cuartos", SF: "Semis", ThirdPlace: "3er Lugar", Final: "Final"
  };

  return (
    <div className="p-6 md:p-8 max-w-6xl mx-auto">
      {/* Ambient */}
      <div className="pointer-events-none fixed top-0 right-0 w-96 h-96 bg-[#ff2d78]/5 rounded-full blur-[100px] -z-10" />
      <div className="pointer-events-none fixed bottom-0 left-64 w-[500px] h-64 bg-[#00ffcc]/4 rounded-full blur-[120px] -z-10" />

      {/* Page header */}
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-white mb-1" style={{ fontFamily: "Sora, sans-serif" }}>
            {phaseLabels[phase] ?? phase}
          </h1>
          <p className="text-[#9b8ec4] text-sm" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
            Ingresa tus predicciones antes del cierre.
          </p>
        </div>

        {/* Phase selector */}
        <div className="flex flex-wrap gap-2">
          {phases.map((p) => (
            <button
              key={p}
              id={`phase-${p}`}
              onClick={() => { setPhase(p); setMatchday(1); }}
              className={`px-3 py-1.5 text-xs font-medium rounded border transition-all duration-150 ${
                phase === p
                  ? "border-[#ff2d78]/50 text-[#ff2d78] bg-[#ff2d78]/10 shadow-[inset_0_0_8px_rgba(255,45,120,0.2)]"
                  : "border-[#302840] text-[#9b8ec4] hover:border-[#ff2d78]/30 hover:text-white"
              }`}
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              {phaseLabels[p]}
            </button>
          ))}
        </div>
      </div>

      {/* Matchday tabs (Groups only) */}
      {phase === "Groups" && (
        <div className="flex gap-1 bg-[#1e1e30] p-1 rounded border border-[#302840]/30 w-fit mb-6">
          {[1, 2, 3].map((d) => (
            <button
              key={d}
              id={`matchday-${d}`}
              onClick={() => setMatchday(d)}
              className={`px-5 py-2 text-xs font-medium uppercase tracking-wider rounded transition-all duration-150 ${
                matchday === d
                  ? "bg-[#ff2d78]/15 text-[#ff2d78] border border-[#ff2d78]/30 shadow-[inset_0_0_8px_rgba(255,45,120,0.15)]"
                  : "text-[#9b8ec4] hover:text-white"
              }`}
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              Matchday {d}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-52 bg-[#141422] rounded-lg border border-[#302840]/40 animate-pulse" />
          ))}
        </div>
      ) : grouped.length === 0 ? (
        <div className="text-center py-24 text-[#9b8ec4]" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
          <p className="text-4xl mb-3">🏆</p>
          <p className="text-sm uppercase tracking-widest">No hay partidos para este filtro.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {grouped.map((m) => (
            <MatchCard key={m.id} match={m} simulatedTime={simulatedTime} onSaved={load} />
          ))}
        </div>
      )}
    </div>
  );
}
