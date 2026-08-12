"use client";

import Link from "next/link";
import { Shield, MessageSquareWarning, Gauge, Users, Lock, Zap, GitBranch } from "lucide-react";
import { useEffect, useState } from "react";
import { api, loginUrl } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { LangSwitcher } from "@/components/LangSwitcher";
import type { TeamMember } from "@/lib/types";

function buildTree(members: TeamMember[]): Map<number | null, TeamMember[]> {
  const map = new Map<number | null, TeamMember[]>();
  for (const m of [...members].sort((a, b) => a.sort_order - b.sort_order)) {
    const key = m.parent_id ?? null;
    const list = map.get(key) ?? [];
    list.push(m);
    map.set(key, list);
  }
  return map;
}

function TeamNode({
  member,
  members,
  withStub = false,
}: {
  member: TeamMember;
  members: TeamMember[];
  withStub?: boolean;
}) {
  const tree = buildTree(members);
  const children = tree.get(member.id) ?? [];
  return (
    <li className="flex flex-col items-center">
      {withStub && <div className="h-6 w-px bg-blurple/40" />}
      <div className="rounded-xl border border-blurple/40 bg-discord px-5 py-3 text-center shadow-lg">
        <div className="text-sm font-semibold text-white">{member.name}</div>
        <div className="mt-0.5 text-xs text-blurple">{member.role}</div>
      </div>
      {children.length > 0 && (
        <>
          <div className="h-6 w-px bg-blurple/40" />
          <div className="relative w-full">
            <div className="absolute left-0 right-0 top-0 h-px bg-blurple/40" />
            <ul className="flex items-start justify-center gap-6 px-6">
              {children.map((c) => (
                <TeamNode key={c.id} member={c} members={members} withStub />
              ))}
            </ul>
          </div>
        </>
      )}
    </li>
  );
}

export default function LandingPage() {
  const [url, setUrl] = useState<string>("");
  const [team, setTeam] = useState<TeamMember[]>([]);
  const { t } = useI18n();

  const FEATURES = [
    {
      icon: MessageSquareWarning,
      title: t("landing.feature1.title"),
      text: t("landing.feature1.text"),
    },
    { icon: Users, title: t("landing.feature2.title"), text: t("landing.feature2.text") },
    { icon: Gauge, title: t("landing.feature3.title"), text: t("landing.feature3.text") },
    { icon: Zap, title: t("landing.feature4.title"), text: t("landing.feature4.text") },
    { icon: Lock, title: t("landing.feature5.title"), text: t("landing.feature5.text") },
    { icon: Shield, title: t("landing.feature6.title"), text: t("landing.feature6.text") },
  ];

  useEffect(() => {
    loginUrl().then(setUrl).catch(() => setUrl(""));
    api<TeamMember[]>("/api/team").then(setTeam).catch(() => {});
  }, []);

  const roots = buildTree(team).get(null) ?? [];

  return (
    <main className="min-h-screen bg-gradient-to-b from-discord-darker via-discord to-blurple/20">
      {/* Nav */}
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 text-xl font-bold text-white">
          <Shield className="h-7 w-7 text-blurple" />
          WordLock
        </div>
        <div className="flex items-center gap-3">
          <a href="#team" className="hidden text-sm font-medium text-gray-300 transition hover:text-white sm:block">
            {t("landing.team")}
          </a>
          <LangSwitcher />
          {url ? (
            <a href={url} className="btn-primary">
              {t("landing.login")}
            </a>
          ) : (
            <span className="btn-primary opacity-60">{t("landing.connecting")}</span>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-24 pt-16 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-6xl">
          {t("landing.hero1")}{" "}
          <span className="bg-gradient-to-r from-blurple to-wordlock-pink bg-clip-text text-transparent">
            {t("landing.hero2")}
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-300">{t("landing.tagline")}</p>
        <div className="mt-10 flex items-center justify-center gap-4">
          {url ? (
            <a href={url} className="btn-primary px-8 py-3 text-base">
              {t("landing.login")}
            </a>
          ) : (
            <span className="btn-primary px-8 py-3 text-base opacity-60">
              {t("landing.connecting")}
            </span>
          )}
          <a href="#features" className="btn-secondary px-8 py-3 text-base">
            {t("landing.features")}
          </a>
          <a href="#team" className="btn-secondary px-8 py-3 text-base">
            {t("landing.team")}
          </a>
        </div>
        <div className="mt-8 text-xs text-gray-500">{t("landing.securityNote")}</div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="card">
              <f.icon className="h-8 w-8 text-blurple" />
              <h3 className="mt-4 text-lg font-semibold text-white">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-400">{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section id="team" className="mx-auto max-w-6xl px-6 pb-24">
        <div className="mb-10 text-center">
          <GitBranch className="mx-auto h-8 w-8 text-blurple" />
          <h2 className="mt-4 text-3xl font-bold text-white">{t("landing.teamTitle")}</h2>
          <p className="mt-2 text-sm text-gray-400">{t("landing.teamSubtitle")}</p>
        </div>
        {team.length === 0 ? (
          <p className="py-12 text-center text-gray-500">{t("landing.teamEmpty")}</p>
        ) : (
          <ul className="flex flex-wrap justify-center gap-8">
            {roots.map((m) => (
              <TeamNode key={m.id} member={m} members={team} />
            ))}
          </ul>
        )}
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 text-center text-sm text-gray-500">
        <p>
          WordLock • {t("landing.footer")} • {t("landing.footerVersion")}
        </p>
        <p className="mt-2">{t("landing.copyright")}</p>
        <nav className="mt-4 flex justify-center gap-6">
          <Link href="/impressum" className="transition-colors hover:text-gray-300">
            {t("landing.impressum")}
          </Link>
          <Link href="/datenschutz" className="transition-colors hover:text-gray-300">
            {t("landing.datenschutz")}
          </Link>
        </nav>
      </footer>
    </main>
  );
}
