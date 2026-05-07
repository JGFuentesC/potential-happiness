import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import { authApi } from "@/api/client";

type Mode = "login" | "register";

export default function Login() {
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pendingMsg, setPendingMsg] = useState(false);
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((s) => s.login);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === "register") {
        await authApi.register(username, password);
        setPendingMsg(true);
      } else {
        await login(username, password);
        navigate("/matches");
      }
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      if (msg === "Account not yet approved" || msg?.includes("approved")) {
        setPendingMsg(true);
      } else if (msg) {
        setError(msg);
      } else {
        setError("Error inesperado. Intente de nuevo.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (pendingMsg) {
    return (
      <div className="min-h-screen bg-[#0e0d14] bg-grid-pattern flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="border border-[#ff2d78]/30 bg-[#13111f]/80 backdrop-blur-sm rounded-lg p-10 text-center shadow-lg">
            <div className="text-5xl mb-4">⏳</div>
            <h2 className="text-xl font-semibold text-white mb-2" style={{ fontFamily: "Sora, sans-serif" }}>
              Cuenta pendiente de aprobación
            </h2>
            <p className="text-[#9b8ec4] text-sm leading-relaxed">
              Tu solicitud fue registrada. Un administrador revisará tu cuenta y la activará pronto.
            </p>
            <button
              onClick={() => { setPendingMsg(false); setMode("login"); setUsername(""); setPassword(""); }}
              className="mt-6 text-[#ff2d78] text-sm hover:underline"
            >
              Volver al login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0e0d14] bg-grid-pattern flex items-center justify-center px-4">
      {/* Ambient glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-[#ff2d78]/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#00f5c4]/8 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <span className="text-3xl">⚽</span>
            <span
              className="text-2xl font-bold text-white neon-glow-primary"
              style={{ fontFamily: "Sora, sans-serif", color: "#ff2d78" }}
            >
              Quiniela
            </span>
            <span className="text-2xl font-bold text-white" style={{ fontFamily: "Sora, sans-serif" }}>
              2026
            </span>
          </div>
          <p className="text-[#9b8ec4] text-sm">Mundial Norteamérica</p>
        </div>

        {/* Card */}
        <div className="border border-[#3d2f6e]/60 bg-[#13111f]/80 backdrop-blur-sm rounded-lg p-8 shadow-2xl">
          {/* Mode toggle */}
          <div className="flex mb-6 bg-[#0e0d14] rounded-md p-1 gap-1">
            {(["login", "register"] as Mode[]).map((m) => (
              <button
                key={m}
                id={`mode-${m}`}
                type="button"
                onClick={() => { setMode(m); setError(null); }}
                className={`flex-1 py-2 text-sm font-medium rounded transition-all duration-200 ${
                  mode === m
                    ? "bg-[#ff2d78] text-white shadow"
                    : "text-[#9b8ec4] hover:text-white"
                }`}
                style={{ fontFamily: "Space Grotesk, sans-serif" }}
              >
                {m === "login" ? "Iniciar Sesión" : "Registrarse"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#9b8ec4] mb-1.5 uppercase tracking-wide">
                Usuario
              </label>
              <input
                id="input-username"
                type="text"
                autoComplete="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full bg-[#0e0d14] border border-[#3d2f6e]/80 rounded px-3 py-2.5 text-white text-sm placeholder:text-[#4a3f6b] focus:outline-none focus:border-[#ff2d78] focus:ring-1 focus:ring-[#ff2d78]/40 transition"
                placeholder="tu_usuario"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-[#9b8ec4] mb-1.5 uppercase tracking-wide">
                Contraseña
              </label>
              <input
                id="input-password"
                type="password"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-[#0e0d14] border border-[#3d2f6e]/80 rounded px-3 py-2.5 text-white text-sm placeholder:text-[#4a3f6b] focus:outline-none focus:border-[#ff2d78] focus:ring-1 focus:ring-[#ff2d78]/40 transition"
                placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded px-3 py-2">
                {error}
              </div>
            )}

            <button
              id="btn-submit"
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-[#ff2d78] hover:bg-[#e0255e] disabled:opacity-50 text-white font-semibold rounded transition-all duration-200 neon-glow-btn text-sm"
              style={{ fontFamily: "Space Grotesk, sans-serif" }}
            >
              {loading
                ? "Procesando..."
                : mode === "login"
                ? "Entrar"
                : "Crear cuenta"}
            </button>
          </form>

          {mode === "register" && (
            <p className="mt-4 text-xs text-[#9b8ec4] text-center">
              Tu cuenta quedará pendiente hasta que un administrador la apruebe.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
