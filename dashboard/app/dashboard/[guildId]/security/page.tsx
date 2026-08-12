"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ShieldAlert, Power } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { Incident, ServerConfig } from "@/lib/types";
import { useI18n } from "@/lib/i18n";

export default function GuildSecurity() {
  const params = useParams();
  const guildId = (params?.guildId as string) ?? "";
  const { t, locale } = useI18n();
  const [config, setConfig] = useState<ServerConfig | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [toast, setToast] = useState<string | null>(null);

  const load = async () => {
    try {
      setConfig(await api<ServerConfig>(`/api/guilds/${guildId}`));
      setIncidents(await api<Incident[]>(`/api/guilds/${guildId}/incidents`));
    } catch (e) {
      setToast(e instanceof ApiError ? e.message : t("common.unknownError"));
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [guildId]);

  const reEnable = async () => {
    if (!window.confirm(t("security.reEnableConfirm"))) return;
    try {
      const res = await api<{ ok: boolean; status: string }>(
        `/api/guilds/${guildId}/enable`,
        { method: "POST" },
      );
      setToast(t("security.enabledToast"));
      await load();
    } catch (e) {
      setToast(e instanceof ApiError ? e.message : t("common.unknownError"));
    }
  };

  return (
    <div className="max-w-4xl space-y-8">
      <header>
        <h1 className="flex items-center gap-2 text-3xl font-bold text-white">
          <ShieldAlert className="h-7 w-7 text-wordlock-red" /> {t("security.title")}
        </h1>
        <p className="mt-1 text-sm text-gray-400">{t("security.subtitle")}</p>
      </header>

      {toast && (
        <div className="rounded-lg bg-blurple/10 px-4 py-3 text-sm text-blurple">{toast}</div>
      )}

      {config?.status === "disabled" && (
        <div className="rounded-xl border border-wordlock-red/40 bg-wordlock-red/10 p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="font-semibold text-wordlock-red">
                🛡️ {t("security.disabledBanner")}
              </div>
            </div>
            <button onClick={reEnable} className="btn-primary !bg-wordlock-green">
              <Power className="h-4 w-4" /> {t("security.reEnable")}
            </button>
          </div>
        </div>
      )}

      <div className="card space-y-4">
        <h2 className="text-lg font-semibold text-white">
          {t("security.title")} ({incidents.length})
        </h2>
        {incidents.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-500">{t("security.noIncidents")}</p>
        ) : (
          incidents.map((inc) => (
            <div key={inc.id} className="rounded-lg bg-white/5 p-4">
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`badge ${
                    inc.status === "open"
                      ? "bg-wordlock-red/15 text-wordlock-red"
                      : "bg-wordlock-green/15 text-wordlock-green"
                  }`}
                >
                  {inc.status === "open" ? t("security.open") : t("security.resolved")}
                </span>
                <span className="font-semibold text-white">
                  {t(`security.kind.${inc.kind}`) === `security.kind.${inc.kind}`
                    ? inc.kind
                    : t(`security.kind.${inc.kind}`)}
                </span>
                <span className="ml-auto text-xs text-gray-500">
                  {new Date(inc.created_at).toLocaleString(locale)}
                </span>
              </div>
              <div className="mt-2 grid gap-1 text-sm text-gray-300 sm:grid-cols-2">
                {inc.actor_id != null && (
                  <div>
                    {t("security.actor")}:{" "}
                    <span className="font-mono text-xs">{inc.actor_id}</span>
                  </div>
                )}
                {inc.detail && Object.keys(inc.detail).length > 0 && (
                  <div>
                    {t("security.detail")}:{" "}
                    <span className="text-gray-400">
                      {Object.entries(inc.detail)
                        .map(([k, v]) => `${k}: ${v}`)
                        .join(" · ")}
                    </span>
                  </div>
                )}
              </div>
              <div className="mt-2 text-xs text-gray-400">
                <span className="text-gray-500">{t("security.consequence")}:</span>{" "}
                {inc.consequence}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
