import { Navigate, Outlet } from "react-router-dom";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import Sidebar from "@/components/layout/Sidebar";
import AppHeader from "@/components/layout/AppHeader";

export default function ProtectedLayout() {
  const user = useAuthStore((s) => s.user);
  const token = useAuthStore((s) => s.token);
  const [simulatedTime, setSimulatedTime] = useState<string | null>(null);

  if (!token || !user) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen overflow-hidden bg-[#0e0d14]">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <AppHeader
          simulatedTime={simulatedTime}
          onSimulatedTimeChange={setSimulatedTime}
        />
        <main className="flex-1 overflow-y-auto">
          {/* Pass simulatedTime down via context or outlet context */}
          <Outlet context={{ simulatedTime }} />
        </main>
      </div>
    </div>
  );
}
