import { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { usersApi } from "@/api/client";
import { useAuthStore } from "@/store/authStore";
import type { RankingEntry } from "@/types";

export default function Leaderboard() {
  const currentUser = useAuthStore((s) => s.user);
  const [ranking, setRanking] = useState<RankingEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    usersApi.ranking()
      .then((r) => setRanking(r.data))
      .finally(() => setLoading(false));
  }, []);

  const medalColors: Record<number, string> = {
    1: "text-[#ffe04a]",
    2: "text-[#a8b2c0]",
    3: "text-[#cd7f32]",
  };

  return (
    <div className="p-6 md:p-8 max-w-5xl mx-auto">
      {/* Ambient */}
      <div className="pointer-events-none fixed top-0 right-0 w-[500px] h-[500px] bg-[#ff2d78]/4 rounded-full blur-[120px] -z-10" />

      {/* Header */}
      <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl md:text-5xl font-black text-white uppercase tracking-tight" style={{ fontFamily: "Sora, sans-serif" }}>
            Global{" "}
            <span className="text-[#ff2d78]" style={{ textShadow: "0 0 8px rgba(255,45,120,0.6)" }}>
              Rankings
            </span>
          </h1>
          <p className="text-[#00ffcc] text-sm mt-2 uppercase tracking-widest" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
            Clasificación en tiempo real
          </p>
        </div>
        <div className="text-right">
          <p className="text-[#9b8ec4] text-xs uppercase tracking-wide" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
            Tu posición
          </p>
          <p className="text-2xl font-bold text-[#ff2d78]" style={{ fontFamily: "Sora, sans-serif" }}>
            {currentUser?.rank != null ? `#${currentUser.rank}` : "—"}
          </p>
        </div>
      </div>

      {/* Table */}
      <div
        className="bg-[#141422]/80 rounded-xl overflow-hidden backdrop-blur-sm"
        style={{ border: "1px solid rgba(255, 45, 120, 0.3)", boxShadow: "inset 0 0 12px rgba(255, 45, 120, 0.05)" }}
      >
        <table className="w-full text-left border-collapse">
          <thead>
            <tr
              className="border-b text-[#9b8ec4] text-xs uppercase tracking-widest"
              style={{ borderColor: "#302840", background: "#1e1e30", fontFamily: "Space Grotesk, sans-serif" }}
            >
              <th className="p-4 w-16 text-center">Pos</th>
              <th className="p-4">Jugador</th>
              <th className="p-4 hidden md:table-cell text-center">Exactos</th>
              <th className="p-4 text-right">Puntos</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#302840]/30 text-sm">
            {loading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    <td colSpan={4} className="p-4">
                      <div className="h-10 bg-[#1e1e30] rounded animate-pulse" />
                    </td>
                  </tr>
                ))
              : ranking.map((entry) => {
                  const isMe = entry.user_id === currentUser?.id;
                  const isFirst = entry.rank === 1;
                  return (
                    <tr
                      key={entry.user_id}
                      className={`group transition-colors hover:bg-[#1e1e30] ${
                        isMe ? "bg-[#ff2d78]/8" : isFirst ? "bg-[#ffe04a]/5" : ""
                      }`}
                    >
                      {/* Rank */}
                      <td className="p-4 text-center relative">
                        {isFirst && (
                          <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#ffe04a]" />
                        )}
                        {isMe && !isFirst && (
                          <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#ff2d78]" />
                        )}
                        <span
                          className={`font-bold text-lg ${
                            medalColors[entry.rank] ?? "text-[#9b8ec4]"
                          } ${isFirst ? "text-2xl" : ""}`}
                          style={{ fontFamily: "Sora, sans-serif", textShadow: isFirst ? "0 0 8px currentColor" : undefined }}
                        >
                          {entry.rank}
                        </span>
                        {isFirst && (
                          <Star size={10} className="text-[#ffe04a] absolute top-2 right-2 hidden md:block fill-current" />
                        )}
                      </td>

                      {/* Player */}
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold shrink-0 ${
                              isFirst
                                ? "bg-gradient-to-br from-[#ffe04a] to-[#ff8800] border-2 border-[#ffe04a]"
                                : isMe
                                ? "bg-gradient-to-br from-[#ff2d78] to-[#7b2ffb]"
                                : "bg-[#28283e] border border-[#302840]"
                            }`}
                            style={{ boxShadow: isFirst ? "0 0 10px rgba(255,224,74,0.3)" : undefined }}
                          >
                            {entry.username[0].toUpperCase()}
                          </div>
                          <div>
                            <div
                              className={`font-bold transition-colors group-hover:text-[#ff2d78] ${
                                isFirst ? "text-[#ffe04a]" : isMe ? "text-[#ff2d78]" : "text-white"
                              }`}
                              style={{ fontFamily: "Sora, sans-serif" }}
                            >
                              {entry.username}
                              {isMe && <span className="ml-2 text-[10px] text-[#9b8ec4] font-normal">(tú)</span>}
                            </div>
                            {isFirst && (
                              <div
                                className="text-[10px] text-[#ffe04a] uppercase tracking-wider hidden md:block"
                                style={{ fontFamily: "Space Grotesk, sans-serif" }}
                              >
                                Grandmaster
                              </div>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Exact scores */}
                      <td className="p-4 hidden md:table-cell text-center text-[#9b8ec4]" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                        {entry.exact_scores}
                      </td>

                      {/* Points */}
                      <td className="p-4 text-right">
                        <span
                          className={`font-bold text-lg ${
                            isFirst
                              ? "text-[#00ffcc]"
                              : isMe
                              ? "text-[#ff2d78]"
                              : "text-white"
                          }`}
                          style={{
                            fontFamily: "Sora, sans-serif",
                            textShadow: isFirst ? "0 0 8px currentColor" : undefined,
                          }}
                        >
                          {entry.total_points.toLocaleString()}
                        </span>
                      </td>
                    </tr>
                  );
                })}

            {!loading && ranking.length === 0 && (
              <tr>
                <td colSpan={4} className="p-12 text-center text-[#9b8ec4]" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                  <p className="text-3xl mb-2">🏆</p>
                  <p className="text-xs uppercase tracking-widest">Aún no hay participantes activos.</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
