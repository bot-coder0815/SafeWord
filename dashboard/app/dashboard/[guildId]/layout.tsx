"use client";

import { useParams } from "next/navigation";
import {
  LayoutDashboard,
  Filter,
  Settings,
  ArrowLeft,
  UserRound,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";
import { Sidebar, type SidebarItem } from "@/components/Sidebar";
import { useI18n } from "@/lib/i18n";

export default function GuildLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const { t } = useI18n();
  const guildId = (params?.guildId as string) ?? "";
  const base = `/dashboard/${guildId}`;

  const items: SidebarItem[] = [
    { href: base, label: t("nav.overview"), icon: LayoutDashboard },
    { href: `${base}/filters`, label: t("nav.filters"), icon: Filter },
    { href: `${base}/settings`, label: t("nav.settings"), icon: Settings },
    { href: `${base}/profile`, label: t("nav.profile"), icon: UserRound },
    { href: `${base}/security`, label: t("nav.security"), icon: ShieldAlert },
  ];

  return (
    <div className="flex min-h-screen">
      <Sidebar title={t("guild.sidebarTitle")} items={items} />
      <div className="flex-1 overflow-y-auto">
        <div className="border-b border-white/5 bg-discord px-6 py-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1 text-xs text-gray-400 hover:text-white"
          >
            <ArrowLeft className="h-3 w-3" /> {t("guild.allServers")}
          </Link>
        </div>
        <div className="p-6 lg:p-10">{children}</div>
      </div>
    </div>
  );
}
