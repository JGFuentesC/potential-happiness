import { Clock, FlaskConical } from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";

interface AppHeaderProps {
  /** ISO 8601 string or null when time travel is disabled */
  simulatedTime: string | null;
  onSimulatedTimeChange: (val: string | null) => void;
}

export default function AppHeader({ simulatedTime, onSimulatedTimeChange }: AppHeaderProps) {
  const user = useAuthStore((s) => s.user);
  const isTimeTraveling = simulatedTime !== null;
  const [inputVal, setInputVal] = useState(simulatedTime ?? "");

  const toggleTimeTravel = () => {
    if (isTimeTraveling) {
      onSimulatedTimeChange(null);
      setInputVal("");
    } else {
      // default to now as a starting point
      const now = new Date().toISOString().slice(0, 16);
      setInputVal(now);
      onSimulatedTimeChange(now);
    }
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputVal(e.target.value);
    if (e.target.value) onSimulatedTimeChange(e.target.value);
  };

  return (
    <header
      className={`h-14 shrink-0 border-b flex items-center justify-between px-5 transition-all duration-300 ${
        isTimeTraveling
          ? "border-[#7b2ffb]/50 bg-[#1a0d2e]/90"
          : "border-[#3d2f6e]/30 bg-[#0e0d14]/80"
      } backdrop-blur-sm sticky top-0 z-30`}
    >
      {/* Left: Time Travel toggle (admin only) */}
      <div className="flex items-center gap-3">
        {user?.is_admin && (
          <>
            <button
              id="btn-time-travel-toggle"
              onClick={toggleTimeTravel}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium border transition-all duration-200 ${
                isTimeTraveling
                  ? "bg-[#7b2ffb]/20 border-[#7b2ffb]/60 text-[#a78bfa] hover:bg-[#7b2ffb]/30"
                  : "bg-transparent border-[#3d2f6e]/50 text-[#9b8ec4] hover:border-[#7b2ffb]/50 hover:text-[#a78bfa]"
              }`}
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              <FlaskConical size={13} />
              Time Travel
              {isTimeTraveling && (
                <span className="ml-1 h-1.5 w-1.5 bg-[#7b2ffb] rounded-full animate-pulse" />
              )}
            </button>

            {isTimeTraveling && (
              <div className="flex items-center gap-1.5">
                <Clock size={13} className="text-[#a78bfa] shrink-0" />
                <input
                  id="input-simulated-time"
                  type="datetime-local"
                  value={inputVal}
                  onChange={handleDateChange}
                  className="bg-[#1a0d2e] border border-[#7b2ffb]/40 rounded px-2 py-1 text-[11px] text-[#a78bfa] focus:outline-none focus:border-[#7b2ffb] w-44"
                />
              </div>
            )}
          </>
        )}

        {isTimeTraveling && (
          <span className="text-[11px] text-[#7b2ffb] font-medium px-2 py-0.5 border border-[#7b2ffb]/30 rounded bg-[#7b2ffb]/10">
            MODO SIMULADO
          </span>
        )}
      </div>

      {/* Right: user info */}
      <div className="flex items-center gap-2">
        <div className="text-right">
          <p
            className="text-xs font-medium text-white leading-none"
            style={{ fontFamily: "Space Grotesk, sans-serif" }}
          >
            {user?.username}
          </p>
          <p className="text-[10px] text-[#9b8ec4] leading-none mt-0.5">
            {user?.total_points ?? 0} pts
            {user?.rank != null && (
              <span className="ml-1 text-[#ff2d78]">#{user.rank}</span>
            )}
          </p>
        </div>
        <div className="h-7 w-7 rounded-full bg-gradient-to-br from-[#ff2d78] to-[#7b2ffb] flex items-center justify-center text-white text-[11px] font-bold shrink-0">
          {user?.username?.[0]?.toUpperCase() ?? "?"}
        </div>
      </div>
    </header>
  );
}
