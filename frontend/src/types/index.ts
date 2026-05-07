// ── Match ─────────────────────────────────────────────────────────────────────

export type MatchStatus = "Open" | "Locked" | "Finished" | "Pending Teams";
export type MatchPhase = "Groups" | "R32" | "R16" | "QF" | "SF" | "ThirdPlace" | "Final";

export interface PredictionInMatch {
  home_score_guess: number;
  away_score_guess: number;
  points_earned: number | null;
}

export interface Match {
  id: number;
  home_team: string | null;
  away_team: string | null;
  home_team_code: string | null;
  away_team_code: string | null;
  home_team_placeholder: string | null;
  away_team_placeholder: string | null;
  start_time: string;
  phase: MatchPhase;
  group_name: string | null;
  matchday: number | null;
  venue: string | null;
  status: MatchStatus;
  home_score_final: number | null;
  away_score_final: number | null;
  my_prediction: PredictionInMatch | null;
}

export interface MatchCreate {
  home_team?: string;
  away_team?: string;
  home_team_code?: string;
  away_team_code?: string;
  home_team_placeholder?: string;
  away_team_placeholder?: string;
  start_time: string;
  phase: MatchPhase;
  group_name?: string;
  matchday?: number;
  venue?: string;
}

export interface MatchResult {
  home_score_final: number;
  away_score_final: number;
}

export interface ResultResponse {
  match_id: number;
  home_score_final: number;
  away_score_final: number;
  predictions_updated: number;
}

// ── User ──────────────────────────────────────────────────────────────────────

export type UserStatus = "Pending" | "Active" | "Rejected";

export interface User {
  id: number;
  username: string;
  is_admin: boolean;
  status: UserStatus;
  total_points: number;
  exact_scores: number;
  rank: number | null;
}

export interface RankingEntry {
  rank: number;
  user_id: number;
  username: string;
  total_points: number;
  exact_scores: number;
}

export interface AdminUser {
  id: number;
  username: string;
  status: UserStatus;
  total_points: number;
  exact_scores: number;
  created_at: string;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// ── Prediction ────────────────────────────────────────────────────────────────

export interface Prediction {
  id: number;
  match_id: number;
  home_score_guess: number;
  away_score_guess: number;
  points_earned: number | null;
  created_at: string;
  updated_at: string;
}

export interface FriendPrediction {
  username: string;
  home_score_guess: number;
  away_score_guess: number;
  points_earned: number | null;
}

// ── Bonus ─────────────────────────────────────────────────────────────────────

export type BonusQuestionType = "Champion" | "TopScorer";

export interface BonusQuestion {
  question_type: BonusQuestionType;
  question_text: string;
  points_reward: number;
  is_locked: boolean;
  my_prediction: string | null;
}

export interface BonusPrediction {
  question_type: BonusQuestionType;
  prediction_text: string;
  points_earned: number | null;
}
