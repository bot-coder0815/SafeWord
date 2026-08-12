"use client";

import { useEffect, useState } from "react";
import { Plus, Save, Trash2, Users } from "lucide-react";
import { api } from "@/lib/api";
import type { TeamMember } from "@/lib/types";
import { useI18n } from "@/lib/i18n";

const EMPTY = { name: "", role: "", parent_id: null as number | null, sort_order: 0 };

export default function AdminTeam() {
  const { t } = useI18n();
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState<number | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  const reload = () => api<TeamMember[]>("/api/admin/team").then(setMembers);

  useEffect(() => {
    reload().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMsg(null);
    if (!form.name.trim()) return;
    await api(editing ? `/api/admin/team/${editing}` : "/api/admin/team", {
      method: editing ? "PATCH" : "POST",
      body: JSON.stringify(form),
    });
    setForm(EMPTY);
    setEditing(null);
    setMsg(t("adTeam.saved"));
    await reload();
  };

  const startEdit = (m: TeamMember) => {
    setEditing(m.id);
    setForm({ name: m.name, role: m.role, parent_id: m.parent_id, sort_order: m.sort_order });
  };

  const remove = async (m: TeamMember) => {
    if (!window.confirm(t("adTeam.deleteConfirm", { name: m.name }))) return;
    await api(`/api/admin/team/${m.id}`, { method: "DELETE" });
    await reload();
  };

  const cancel = () => {
    setEditing(null);
    setForm(EMPTY);
  };

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-white">{t("adTeam.title")}</h1>
        <p className="mt-1 text-sm text-gray-400">{t("adTeam.subtitle")}</p>
      </header>

      {msg && <div className="rounded-lg bg-safeword-green/10 px-4 py-3 text-sm text-safeword-green">{msg}</div>}

      <form onSubmit={submit} className="card space-y-4">
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="label">{t("adTeam.name")}</label>
            <input
              className="input w-56"
              value={form.name}
              placeholder={t("adTeam.namePlaceholder")}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t("adTeam.role")}</label>
            <input
              className="input w-64"
              value={form.role}
              placeholder={t("adTeam.rolePlaceholder")}
              onChange={(e) => setForm({ ...form, role: e.target.value })}
            />
          </div>
          <div>
            <label className="label">{t("adTeam.parent")}</label>
            <select
              className="input w-48"
              value={form.parent_id ?? ""}
              onChange={(e) =>
                setForm({ ...form, parent_id: e.target.value ? Number(e.target.value) : null })
              }
            >
              <option value="">{t("adTeam.noParent")}</option>
              {members
                .filter((m) => m.id !== editing)
                .map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
            </select>
          </div>
          <div>
            <label className="label">{t("adTeam.sortOrder")}</label>
            <input
              type="number"
              className="input w-24"
              value={form.sort_order}
              onChange={(e) => setForm({ ...form, sort_order: Number(e.target.value) })}
            />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">
              {editing ? <Save className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              {editing ? t("common.save") : t("common.add")}
            </button>
            {editing && (
              <button type="button" onClick={cancel} className="btn-secondary">
                {t("common.cancel")}
              </button>
            )}
          </div>
        </div>
      </form>

      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/5 text-left text-xs uppercase tracking-wider text-gray-400">
              <th className="pb-2">{t("adTeam.thName")}</th>
              <th className="pb-2">{t("adTeam.thRole")}</th>
              <th className="pb-2">{t("adTeam.thParent")}</th>
              <th className="pb-2">{t("adTeam.thOrder")}</th>
              <th className="pb-2 text-right">{t("adTeam.thActions")}</th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => (
              <tr key={m.id} className="border-b border-white/5 last:border-0">
                <td className="py-3">
                  <div className="flex items-center gap-2 font-medium text-white">
                    <Users className="h-4 w-4 text-blurple" /> {m.name}
                  </div>
                </td>
                <td className="py-3 text-gray-300">{m.role}</td>
                <td className="py-3 text-gray-400">
                  {members.find((p) => p.id === m.parent_id)?.name ?? "—"}
                </td>
                <td className="py-3 font-mono text-xs text-gray-400">{m.sort_order}</td>
                <td className="py-3">
                  <div className="flex justify-end gap-2">
                    <button onClick={() => startEdit(m)} className="btn-secondary px-2 py-1 text-xs">
                      {t("common.edit")}
                    </button>
                    <button onClick={() => remove(m)} className="btn-danger px-2 py-1 text-xs">
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {members.length === 0 && (
              <tr>
                <td colSpan={5} className="py-10 text-center text-gray-500">
                  {t("adTeam.empty")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
