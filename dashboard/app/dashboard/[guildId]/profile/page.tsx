"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ImagePlus, Save, Info } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { BotProfile } from "@/lib/types";
import { useI18n } from "@/lib/i18n";

function fileToDataUri(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error("File read error"));
    reader.readAsDataURL(file);
  });
}

export default function GuildProfile() {
  const params = useParams();
  const guildId = (params?.guildId as string) ?? "";
  const { t } = useI18n();

  const [profile, setProfile] = useState<BotProfile | null>(null);
  const [avatar, setAvatar] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api<BotProfile>("/api/profile").then((p) => {
      setProfile(p);
      setAvatar(p.avatar);
    });
  }, []);

  const pick = async (file?: File) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError(t("profile.pickError"));
      return;
    }
    const dataUri = await fileToDataUri(file);
    setAvatar(dataUri);
    setError(null);
  };

  const save = async () => {
    if (!avatar) return;
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const res = await api<{ avatar: string }>("/api/profile/apply", {
        method: "POST",
        body: JSON.stringify({ guild_id: guildId, avatar }),
      });
      setAvatar(res.avatar);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : t("common.error"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-white">{t("profile.title")}</h1>
        <p className="mt-1 text-sm text-gray-400">{t("profile.subtitle")}</p>
      </header>

      <div className="card flex items-start gap-2 !bg-blurple/10 !border-blurple/30">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-blurple" />
        <p className="text-sm text-gray-300">{t("profile.info")}</p>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold text-white">{t("profile.header")}</h2>
        <div className="flex items-center gap-5">
          {avatar ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatar}
              alt=""
              className="h-24 w-24 rounded-full border-4 border-white/10 object-cover"
            />
          ) : (
            <div className="flex h-24 w-24 items-center justify-center rounded-full border-4 border-white/10 bg-white/5 text-xs text-gray-500">
              {t("profile.noImage")}
            </div>
          )}
          <label className="cursor-pointer rounded-lg bg-white/10 px-3 py-2 text-sm font-medium text-white hover:bg-white/20">
            <ImagePlus className="mr-1 inline h-4 w-4" />
            {t("profile.upload")}
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => pick(e.target.files?.[0])}
            />
          </label>
        </div>
        {profile?.updated_by && (
          <p className="mt-3 text-xs text-gray-500">
            {t("profile.lastChanged", {
              date: profile.updated_at ? new Date(profile.updated_at).toLocaleString() : "–",
            })}
          </p>
        )}
      </div>

      <div className="flex items-center justify-end gap-3">
        {error && <p className="text-sm text-red-400">{error}</p>}
        {saved && <p className="text-sm text-safeword-green">{t("profile.saved")}</p>}
        <button onClick={save} disabled={saving || !avatar} className="btn-primary">
          <Save className="h-4 w-4" />
          {saving ? t("common.loading") : t("profile.saveBtn")}
        </button>
      </div>
    </div>
  );
}
