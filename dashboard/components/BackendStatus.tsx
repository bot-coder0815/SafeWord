"use client";

import { useEffect, useState } from "react";
import { Loader2, WifiOff } from "lucide-react";
import { useI18n } from "@/lib/i18n";

const POLL_MS = 15000;

export function BackendStatus() {
  const { t } = useI18n();
  const [unreachable, setUnreachable] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      try {
        const res = await fetch("/api/health", { cache: "no-store" });
        if (!cancelled) setUnreachable(!res.ok);
      } catch {
        if (!cancelled) setUnreachable(true);
      }
    };

    check();
    const id = setInterval(check, POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (!unreachable) return null;

  return (
    <div className="flex items-start gap-3 rounded-xl border border-wordlock-yellow/40 bg-wordlock-yellow/10 p-4 text-sm text-wordlock-yellow">
      <WifiOff className="mt-0.5 h-5 w-5 shrink-0" />
      <div>
        <div className="font-semibold">{t("backend.unreachable")}</div>
        <div className="mt-0.5 flex items-center gap-1.5 text-xs text-wordlock-yellow/80">
          <Loader2 className="h-3 w-3 animate-spin" />
          {t("backend.restarting")}
        </div>
      </div>
    </div>
  );
}
