import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "@/pages/Login";
import Matches from "@/pages/Matches";
import Leaderboard from "@/pages/Leaderboard";
import Bonus from "@/pages/Bonus";
import Admin from "@/pages/Admin";
import ProtectedLayout from "@/components/layout/ProtectedLayout";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Protected — all authenticated routes share the sidebar/header layout */}
        <Route element={<ProtectedLayout />}>
          <Route path="/matches" element={<Matches />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/bonus" element={<Bonus />} />
          <Route path="/admin" element={<Admin />} />
        </Route>

        {/* Default redirect */}
        <Route path="*" element={<Navigate to="/matches" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
