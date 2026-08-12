"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Server,
  BarChart3,
  Rocket,
  FileText,
  ScrollText,
  ShieldCheck,
  ShieldAlert,
  UserCog,
  Users,
} from "lucide-react";
import { Sidebar, type SidebarItem } from "@/components/Sidebar";
import { api, ApiError } from "@/lib/api";
import type { Me } from "@/lib/types";
import { useI18n } from "@/lib/i18n";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { t } = useI18n();
  const [role, setRole] = useState<string | null>(null);

  const items: SidebarItem[] = [
    { href: "/admin", label: t("admin.overview"), icon: LayoutDashboard },
    { href: "/admin/servers", label: t("admin.servers"), icon: Server },
    { href: "/admin/stats", label: t("admin.stats"), icon: BarChart3 },
    { href: "/admin/incidents", label: t("admin.incidents"), icon: ShieldAlert },
    { href: "/admin/profile", label: t("admin.profile"), icon: UserCog },
    { href: "/admin/updates", label: t("admin.updates"), icon: Rocket },
    { href: "/admin/lists", label: t("admin.lists"), icon: FileText },
    { href: "/admin/team", label: t("admin.team"), icon: Users },
    { href: "/admin/logs", label: t("admin.logs"), icon: ScrollText },
  ];

  useEffect(() => {
    api<Me>("/api/auth/me")
      .then((me) => {
        setRole(me.role);
        if (!["owner", "developer", "moderator"].includes(me.role)) {
          router.replace("/dashboard");
        }
      })
      .catch((e: ApiError) => {
        if (e.status === 401) router.replace("/");
      });
  }, [router]);

  const roleBadge =
    role === "owner" ? (
      <span className="badge bg-safeword-red/15 text-safeword-red">
        <ShieldCheck className="h-3 w-3" /> Owner
      </span>
    ) : role === "developer" ? (
      <span className="badge bg-blurple/15 text-blurple">Developer</span>
    ) : (
      <span className="badge bg-safeword-green/15 text-safeword-green">Moderator</span>
    );

  return (
    <div className="flex min-h-screen">
      <Sidebar title={t("admin.sidebarTitle")} items={items} subtitle={t("admin.sidebarSubtitle")} />
      <div className="flex-1 overflow-y-auto">
        <div className="flex items-center justify-between border-b border-white/5 bg-discord px-6 py-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
            {t("admin.headerLabel")}
          </span>
          {roleBadge}
        </div>
        <div className="p-6 lg:p-10">{children}</div>
      </div>
    </div>
  );
}
