import axios from "axios";
import type {
  Match, Prediction, FriendPrediction, User, RankingEntry,
  BonusQuestion, BonusPrediction, TokenResponse, ResultResponse,
  AdminUser, MatchCreate, MatchResult,
} from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// On 401, clear session and redirect to login
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (username: string, password: string) =>
    api.post<{ id: number; username: string }>("/auth/register", { username, password }),

  login: (username: string, password: string) =>
    api.post<TokenResponse>("/auth/login", { username, password }),
};

// ── Users ─────────────────────────────────────────────────────────────────────

export const usersApi = {
  me: () => api.get<User>("/users/me"),
  ranking: () => api.get<RankingEntry[]>("/users/ranking"),
};

// ── Matches ───────────────────────────────────────────────────────────────────

export const matchesApi = {
  list: (params?: { phase?: string; group_name?: string; simulated_time?: string }) =>
    api.get<Match[]>("/matches", { params }),

  get: (id: number, params?: { simulated_time?: string }) =>
    api.get<Match>(`/matches/${id}`, { params }),
};

// ── Predictions ───────────────────────────────────────────────────────────────

export const predictionsApi = {
  upsert: (payload: {
    match_id: number;
    home_score_guess: number;
    away_score_guess: number;
    simulated_time?: string;
  }) => api.post<Prediction>("/predictions", payload),

  forMatch: (matchId: number, params?: { simulated_time?: string }) =>
    api.get<FriendPrediction[]>(`/predictions/match/${matchId}`, { params }),
};

// ── Bonus ─────────────────────────────────────────────────────────────────────

export const bonusApi = {
  questions: () => api.get<BonusQuestion[]>("/bonus-questions"),

  save: (question_type: string, prediction_text: string) =>
    api.post<BonusPrediction>("/bonus-predictions", { question_type, prediction_text }),
};

// ── Admin ─────────────────────────────────────────────────────────────────────

export const adminApi = {
  // Users
  listUsers: (status?: string) =>
    api.get<AdminUser[]>("/admin/users", { params: status ? { status } : undefined }),
  approveUser: (id: number) => api.post<AdminUser>(`/admin/users/${id}/approve`),
  rejectUser: (id: number) => api.post<AdminUser>(`/admin/users/${id}/reject`),

  // Matches
  createMatch: (data: MatchCreate) => api.post<Match>("/admin/matches", data),
  updateMatch: (id: number, data: Partial<MatchCreate>) =>
    api.put<Match>(`/admin/matches/${id}`, data),
  setResult: (id: number, result: MatchResult) =>
    api.post<ResultResponse>(`/admin/matches/${id}/result`, result),
  correctResult: (id: number, result: MatchResult) =>
    api.put<ResultResponse>(`/admin/matches/${id}/result`, result),

  // Bonus
  validateBonus: (userId: number, questionType: string, points: number) =>
    api.post<BonusPrediction>(`/admin/bonus-predictions/${userId}/${questionType}/validate`, {
      points_earned: points,
    }),
};
