import { useEffect, useState } from "react";
import { Globe, User, Lock, Save } from "lucide-react";
import { bonusApi } from "@/api/client";
import type { BonusQuestion } from "@/types";

export default function Bonus() {
  const [questions, setQuestions] = useState<BonusQuestion[]>([]);
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [saved, setSaved] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    bonusApi.questions()
      .then((r) => {
        setQuestions(r.data);
        const init: Record<string, string> = {};
        r.data.forEach((q) => { init[q.question_type] = q.my_prediction ?? ""; });
        setInputs(init);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (q: BonusQuestion) => {
    const val = inputs[q.question_type]?.trim();
    if (!val || q.is_locked) return;
    setSaving((s) => ({ ...s, [q.question_type]: true }));
    setErrors((e) => ({ ...e, [q.question_type]: "" }));
    try {
      await bonusApi.save(q.question_type, val);
      setSaved((s) => ({ ...s, [q.question_type]: true }));
      setTimeout(() => setSaved((s) => ({ ...s, [q.question_type]: false })), 2000);
      // Refresh to update is_locked
      bonusApi.questions().then((r) => setQuestions(r.data));
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setErrors((er) => ({ ...er, [q.question_type]: msg ?? "Error al guardar" }));
    } finally {
      setSaving((s) => ({ ...s, [q.question_type]: false }));
    }
  };

  const icons: Record<string, React.ReactNode> = {
    Champion: <Globe size={20} className="text-[#ff2d78]" style={{ filter: "drop-shadow(0 0 6px rgba(255,45,120,0.7))" }} />,
    TopScorer: <User size={20} className="text-[#00ffcc]" style={{ filter: "drop-shadow(0 0 6px rgba(0,255,204,0.7))" }} />,
  };

  const borderCls: Record<string, string> = {
    Champion: "border-[#ff2d78]/40 shadow-[inset_0_0_20px_rgba(255,45,120,0.05)]",
    TopScorer: "border-[#00ffcc]/30 shadow-[inset_0_0_20px_rgba(0,255,204,0.05)]",
  };

  const accentCls: Record<string, string> = {
    Champion: "border-[#ff2d78] focus:border-[#ff2d78] text-[#ff2d78] placeholder:text-[#5a3050]",
    TopScorer: "border-[#00ffcc] focus:border-[#00ffcc] text-[#00ffcc] placeholder:text-[#104040]",
  };

  const saveBtnCls: Record<string, string> = {
    Champion: "border-[#ff2d78]/50 text-[#ff2d78] hover:bg-[#ff2d78]/10 hover:shadow-[0_0_16px_rgba(255,45,120,0.3)]",
    TopScorer: "border-[#00ffcc]/50 text-[#00ffcc] hover:bg-[#00ffcc]/10 hover:shadow-[0_0_16px_rgba(0,255,204,0.3)]",
  };

  return (
    <div className="p-6 md:p-10 lg:p-16 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-4xl md:text-5xl font-bold text-white" style={{ fontFamily: "Sora, sans-serif" }}>
          Bonus{" "}
          <span className="text-[#ff2d78]" style={{ textShadow: "0 0 8px rgba(255,45,120,0.6)" }}>
            Predictions
          </span>
        </h1>

        {/* Lock notice */}
        <div className="mt-4 bg-[#1e1e30]/80 border-l-4 border-[#ffe04a] p-4 flex items-start gap-3 rounded-r-lg max-w-2xl">
          <Lock size={16} className="text-[#ffe04a] mt-0.5 shrink-0" />
          <div>
            <p className="text-[#ffe04a] text-xs font-bold uppercase tracking-wide mb-1" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
              Aviso de cierre
            </p>
            <p className="text-[#9b8ec4] text-sm">
              Las predicciones bonus se cierran automáticamente al inicio del primer partido del torneo.
              Una vez cerradas, no se pueden modificar.
            </p>
          </div>
        </div>
      </div>

      {/* Cards grid */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[0, 1].map((i) => (
            <div key={i} className="h-72 bg-[#141422] rounded-xl border border-[#302840] animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {questions.map((q) => (
              <section
                key={q.question_type}
                className={`relative bg-[#141422] rounded-xl border p-6 overflow-hidden flex flex-col h-80 ${borderCls[q.question_type] ?? "border-[#302840]"}`}
              >
                {/* Decorative icon bg */}
                <div className="absolute -right-8 -top-8 opacity-[0.06] pointer-events-none">
                  {q.question_type === "Champion"
                    ? <span className="text-[120px]">🏆</span>
                    : <span className="text-[120px]">👟</span>
                  }
                </div>

                {/* Title */}
                <div className="mb-6 z-10">
                  <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-1" style={{ fontFamily: "Sora, sans-serif" }}>
                    {icons[q.question_type]}
                    {q.question_type === "Champion" ? "Campeón del Mundo" : "Bota de Oro"}
                  </h2>
                  <p
                    className="text-[#9b8ec4] text-xs uppercase tracking-widest"
                    style={{ fontFamily: "Space Grotesk, sans-serif" }}
                  >
                    {q.question_type === "Champion" ? `+${q.points_reward} pts` : `+${q.points_reward} pts`}
                  </p>
                </div>

                {/* Input area */}
                <div className="flex-1 flex flex-col justify-center z-10">
                  {q.is_locked ? (
                    <div className="p-4 bg-[#1e1e30] rounded-lg border border-[#302840] flex items-center gap-3">
                      <Lock size={14} className="text-[#9b8ec4] shrink-0" />
                      <div>
                        <p className="text-white text-sm font-medium" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                          {inputs[q.question_type] || "No registrado"}
                        </p>
                        <p className="text-[#9b8ec4] text-xs mt-0.5">Predicción cerrada</p>
                      </div>
                    </div>
                  ) : (
                    <div className="relative">
                      <label className="block text-xs text-[#00ffcc] mb-2 uppercase tracking-wider pl-1" style={{ fontFamily: "Space Grotesk, sans-serif" }}>
                        {q.question_type === "Champion" ? "País" : "Jugador"}
                      </label>
                      <input
                        id={`bonus-input-${q.question_type}`}
                        type="text"
                        value={inputs[q.question_type] ?? ""}
                        onChange={(e) => setInputs((s) => ({ ...s, [q.question_type]: e.target.value }))}
                        placeholder={q.question_type === "Champion" ? "Ej: Argentina" : "Ej: Mbappé"}
                        className={`w-full bg-[#28283e] border-b-2 rounded-t-md px-4 py-3 text-sm focus:outline-none transition-colors ${accentCls[q.question_type] ?? ""}`}
                        style={{ fontFamily: "Inter, sans-serif" }}
                      />
                      {errors[q.question_type] && (
                        <p className="text-red-400 text-xs mt-1">{errors[q.question_type]}</p>
                      )}
                    </div>
                  )}
                </div>

                {/* Save footer */}
                {!q.is_locked && (
                  <div className="z-10 flex justify-end mt-4">
                    <button
                      id={`btn-save-bonus-${q.question_type}`}
                      onClick={() => handleSave(q)}
                      disabled={saving[q.question_type] || !inputs[q.question_type]?.trim()}
                      className={`flex items-center gap-2 px-5 py-2 border text-xs font-bold uppercase tracking-wider transition-all duration-200 rounded disabled:opacity-40 ${
                        saved[q.question_type]
                          ? "border-[#00ffcc]/50 text-[#00ffcc] bg-[#00ffcc]/10"
                          : saveBtnCls[q.question_type] ?? ""
                      }`}
                      style={{ fontFamily: "Space Grotesk, sans-serif" }}
                    >
                      <Save size={13} />
                      {saved[q.question_type] ? "Guardado" : "Guardar"}
                    </button>
                  </div>
                )}
              </section>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
