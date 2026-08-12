export interface Guild {
  id: string;
  name: string;
  icon: string | null;
  member_count: number;
  bot_in_server: boolean;
  bot_status: string;
}

export interface Me {
  id: string;
  username: string;
  avatar: string | null;
  role: string;
  admin_guilds: Guild[];
  maintenance: boolean;
}

export interface ServerConfig {
  guild_id: string;
  name: string;
  status: string;
  language: string;
  mod_level: number;
  log_channel_id: number | null;
  action_delete: boolean;
  action_warn: boolean;
  action_timeout: boolean;
  action_log: boolean;
  timeout_minutes: number;
  default_lists: Record<string, boolean>;
  bypass_roles: number[];
  bypass_users: number[];
  bot_version: string | null;
  member_count: number;
}

export interface Word {
  id: number;
  word: string;
  category: string;
  severity: number;
  action: string;
  enabled: boolean;
}

export interface SeriesPoint {
  day: string;
  value: number;
}

export interface WordCount {
  matched_word: string;
  count: number;
}

export interface ActionCount {
  action: string;
  count: number;
}

export interface GuildStats {
  guild_id: string;
  guild_name: string;
  member_count: number;
  status: string;
  violations_today: number;
  violations_series: SeriesPoint[];
  top_words: WordCount[];
  actions: ActionCount[];
  warning_count: number;
}

export interface Update {
  id: number;
  version: string;
  title: string;
  changelog: string | null;
  maintenance_mode: boolean;
  date: string;
}

export interface LogEntry {
  id: number;
  type: string;
  level: string;
  guild_id: number | null;
  message: string;
  stacktrace: string | null;
  created_at: string;
}

export interface AdminOverview {
  servers: number;
  active_servers: number;
  active_users: number;
  violations_today: number;
  violations_total: number;
  error_count: number;
  version: string;
  maintenance_mode: boolean;
  started_at: string | null;
  last_updates: Update[];
  status: { bot: string; api: string; database: string };
}

export interface AdminServer {
  guild_id: number;
  name: string;
  owner_id: number | null;
  status: string;
  bot_version: string | null;
  member_count: number;
  language: string;
  mod_level: number;
  created_at: string;
  updated_at: string;
}

export interface AdminStats {
  violations_series: SeriesPoint[];
  server_growth: SeriesPoint[];
  action_counts: ActionCount[];
  top_words: WordCount[];
  per_guild: { guild_id: number; count: number }[];
  servers: number;
  active_users: number;
  violations_total: number;
}

export interface WordListInfo {
  language: string;
  name: string;
  version: string;
  word_count: number;
}

export interface BotProfile {
  avatar: string | null;
  updated_by: number | null;
  updated_at: string | null;
}

export interface ProfileHistoryEntry {
  id: number;
  field: string;
  guild_id: number | null;
  updated_by: number | null;
  value: string | null;
  created_at: string;
}

export interface TeamMember {
  id: number;
  name: string;
  role: string;
  parent_id: number | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Incident {
  id: number;
  guild_id: number;
  kind: string;
  severity: string;
  actor_id: number | null;
  detail: Record<string, unknown> | null;
  consequence: string | null;
  status: string;
  pushed: boolean;
  created_at: string;
  resolved_at: string | null;
  guild_name?: string;
}
