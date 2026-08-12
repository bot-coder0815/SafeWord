"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Save } from "lucide-react";
import { api } from "@/lib/api";
import type { ServerConfig } from "@/lib/types";
import { useI18n } from "@/lib/i18n";

interface ChannelOption {
  id: string;
  name: string;
  type: number;
}

export default function GuildSettings() {
  const params = useParams();
  const guildId = (params?.guildId as string) ?? "";
  const { t } = useI18n();
  const [cfg, setCfg] = useState<ServerConfig | null>(null);
  const [channels, setChannels] = useState<ChannelOption[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api<ServerConfig>(`/api/guilds/${guildId}`).then(setCfg);
    api<{ channels: ChannelOption[] }>(`/api/guilds/${guildId}/channels`)
      .then((r) => setChannels(r.channels ?? []))
      .catch(() => setChannels([]));
  }, [guildId]);

  const save = async () => {
    if (!cfg) return;
    setSaved(false);
    await api(`/api/guilds/${guildId}`, {
      method: "PUT",
      body: JSON.stringify({
        language: cfg.language,
        mod_level: cfg.mod_level,
        log_channel_id: cfg.log_channel_id,
        timeout_minutes: cfg.timeout_minutes,
        action_delete: cfg.action_delete,
        action_warn: cfg.action_warn,
        action_timeout: cfg.action_timeout,
        action_log: cfg.action_log,
        bypass_roles: cfg.bypass_roles ?? [],
        bypass_users: cfg.bypass_users ?? [],
      }),
    });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!cfg) return <p className="text-gray-400">{t("settings.loading")}</p>;

  const toggle = (key: keyof ServerConfig) =>
    setCfg({ ...cfg, [key]: !cfg[key] });

  const actions: { key: keyof ServerConfig; label: string; desc: string }[] = [
    { key: "action_delete", label: t("settings.actionDelete"), desc: t("settings.actionDeleteDesc") },
    { key: "action_warn", label: t("settings.actionWarn"), desc: t("settings.actionWarnDesc") },
    { key: "action_timeout", label: t("settings.actionTimeout"), desc: t("settings.actionTimeoutDesc") },
    { key: "action_log", label: t("settings.actionLog"), desc: t("settings.actionLogDesc") },
  ];

  return (
    <div className="max-w-3xl space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-white">{t("settings.title")}</h1>
        <p className="mt-1 text-sm text-gray-400">{t("settings.subtitle")}</p>
      </header>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-white">{t("settings.general")}</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="label">{t("common.language")}</label>
            <select
              className="input"
              value={cfg.language}
              onChange={(e) => setCfg({ ...cfg, language: e.target.value })}
            >
              <option value="en">English</option>
              <option value="de">Deutsch</option>
            </select>
          </div>
          <div>
            <label className="label">{t("settings.modLevel")}</label>
            <select
              className="input"
              value={cfg.mod_level}
              onChange={(e) => setCfg({ ...cfg, mod_level: Number(e.target.value) })}
            >
              {[1, 2, 3, 4, 5].map((s) => (
                <option key={s} value={s}>
                  {t("settings.levelOption", {
                    s: String(s),
                    desc:
                      s === 1
                        ? t("settings.levelStrict")
                        : s === 5
                          ? t("settings.levelHeavy")
                          : t("settings.levelBalanced"),
                  })}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">{t("settings.logChannelId")}</label>
            <select
              className="input"
              value={cfg.log_channel_id ?? ""}
              onChange={(e) =>
                setCfg({ ...cfg, log_channel_id: e.target.value ? Number(e.target.value) : null })
              }
            >
              <option value="">{t("settings.logChannelNone")}</option>
              {channels.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.type === 5 ? "📢 " : "# "}
                  {c.name}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">{t("settings.logChannelAlt")}</p>
          </div>
          <div>
            <label className="label">{t("settings.timeout")}</label>
            <input
              className="input"
              type="number"
              min={1}
              max={10080}
              value={cfg.timeout_minutes}
              onChange={(e) => setCfg({ ...cfg, timeout_minutes: Number(e.target.value) })}
            />
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-white">{t("settings.actions")}</h2>
        <div className="space-y-3">
          {actions.map((a) => (
            <div key={a.key} className="flex items-center justify-between rounded-lg bg-white/5 px-4 py-3">
              <div>
                <div className="font-medium text-white">{a.label}</div>
                <div className="text-xs text-gray-400">{a.desc}</div>
              </div>
              <button
                onClick={() => toggle(a.key)}
                className={`relative h-6 w-11 rounded-full transition ${
                  cfg[a.key] ? "bg-safeword-green" : "bg-white/10"
                }`}
                aria-label={a.label}
              >
                <span
                  className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-all ${
                    cfg[a.key] ? "left-[22px]" : "left-0.5"
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-white">{t("settings.bypass")}</h2>
        <p className="mb-4 text-sm text-gray-400">{t("settings.bypassDesc")}</p>
        <div className="space-y-4">
          <div>
            <label className="label">{t("settings.bypassRoles")}</label>
            <input
              className="input"
              placeholder={t("settings.bypassPlaceholder")}
              value={(cfg.bypass_roles ?? []).join(", ")}
              onChange={(e) =>
                setCfg({
                  ...cfg,
                  bypass_roles: e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean)
                    .map(Number),
                })
              }
            />
          </div>
          <div>
            <label className="label">{t("settings.bypassUsers")}</label>
            <input
              className="input"
              placeholder={t("settings.bypassPlaceholder")}
              value={(cfg.bypass_users ?? []).join(", ")}
              onChange={(e) =>
                setCfg({
                  ...cfg,
                  bypass_users: e.target.value
                    .split(",")
                    .map((s) => s.trim())
                    .filter(Boolean)
                    .map(Number),
                })
              }
            />
          </div>
          <p className="text-xs text-gray-500">{t("settings.bypassHint")}</p>
        </div>
      </div>

      <div className="flex justify-end">
        <button onClick={save} className="btn-primary">
          <Save className="h-4 w-4" />
          {saved ? t("common.saved") : t("common.save")}
        </button>
      </div>
    </div>
  );
}
