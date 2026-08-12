"use client";

import { useEffect, useState } from "react";
import { Server, Users, AlertTriangle, Bug, Activity, Clock, Rocket } from "lucide-react";
import { api } from "@/lib/api";
import type { AdminOverview } from "@/lib/types";
import { StatCard } from "@/components/StatCard";
import { useI18n } from "@/lib/i18n";

export default function AdminOverview() {
  const { t, locale } = useI18n();
  const [data, setData] = useState<AdminOverview | null>(null);

  useEffect(() => {
    api<AdminOverview>("/api/admin/overview").then(setData);
  }, []);

  if (!data) return <p className="text-gray-400">{t("adminOv.loading")}</p>;

  const statusDot = (s: string) => (
    <span className={`inline-block h-2.5 w-2.5 rounded-full ${s === "online" || s === "connected" ? "bg-wordlock-green" : "bg-wordlock-red"}`} />
  );

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">{t("adminOv.title")}</h1>
          <p className="mt-1 text-sm text-gray-400">
            {t("adminOv.started", {
              version: data.version,
              date: data.started_at ? new Date(data.started_at).toLocaleString(locale) : "—",
            })}
          </p>
        </div>
        <div className="card flex items-center gap-3">
          <Activity className="h-5 w-5 text-blurple" />
          <div className="text-xs">
            <div className="flex items-center gap-1.5">
              {statusDot(data.status.bot)} {t("adminOv.bot")}: {data.status.bot}
            </div>
            <div className="flex items-center gap-1.5">
              {statusDot(data.status.api)} {t("adminOv.api")}: {data.status.api}
            </div>
            <div className="flex items-center gap-1.5">
              {statusDot(data.status.database)} {t("adminOv.database")}: {data.status.database}
            </div>
          </div>
        </div>
      </header>

      {data.maintenance_mode && (
        <div className="rounded-xl border border-wordlock-yellow/40 bg-wordlock-yellow/10 p-4 text-sm text-wordlock-yellow">
          {t("adminOv.maintenance")}
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label={t("adminOv.servers")} value={data.servers} icon={Server} />
        <StatCard label={t("adminOv.activeUsers")} value={data.active_users} icon={Users} tone="green" />
        <StatCard label={t("adminOv.violationsToday")} value={data.violations_today} icon={AlertTriangle} tone="yellow" />
        <StatCard label={t("adminOv.errors")} value={data.error_count} icon={Bug} tone="red" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-white">
            <Rocket className="h-5 w-5 text-blurple" /> {t("adminOv.lastUpdates")}
          </h2>
          {data.last_updates.length ? (
            <ul className="space-y-3">
              {data.last_updates.map((u) => (
                <li key={u.id} className="rounded-lg bg-white/5 px-4 py-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white">{u.version}</span>
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                      <Clock className="h-3 w-3" />
                      {new Date(u.date).toLocaleDateString(locale)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-300">{u.title}</div>
                  {u.changelog && (
                    <p className="mt-1 whitespace-pre-line text-xs text-gray-500">{u.changelog}</p>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="py-6 text-center text-sm text-gray-500">{t("adminOv.noUpdates")}</p>
          )}
        </div>

        <div className="card">
          <h2 className="mb-4 text-lg font-semibold text-white">{t("adminOv.metrics")}</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg bg-white/5 p-4">
              <div className="text-2xl font-bold text-white">{data.servers}</div>
              <div className="text-xs text-gray-400">{t("adminOv.totalServers")}</div>
            </div>
            <div className="rounded-lg bg-white/5 p-4">
              <div className="text-2xl font-bold text-white">{data.active_servers}</div>
              <div className="text-xs text-gray-400">{t("adminOv.activeServers")}</div>
            </div>
            <div className="rounded-lg bg-white/5 p-4">
              <div className="text-2xl font-bold text-white">{data.violations_total}</div>
              <div className="text-xs text-gray-400">{t("adminOv.totalViolations")}</div>
            </div>
            <div className="rounded-lg bg-white/5 p-4">
              <div className="text-2xl font-bold text-white">{data.error_count}</div>
              <div className="text-xs text-gray-400">{t("adminOv.errorLogs")}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
