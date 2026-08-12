"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

export type Lang = "de" | "en";

const de = {
  // common
  "common.logout": "Abmelden",
  "common.loading": "Lädt…",
  "common.error": "Unbekannter Fehler",
  "common.save": "Speichern",
  "common.saved": "Gespeichert ✓",
  "common.saving": "Speichern…",
  "common.add": "Hinzufügen",
  "common.delete": "Löschen",
  "common.refresh": "Aktualisieren",
  "common.enable": "Aktivieren",
  "common.disable": "Deaktivieren",
  "common.active": "aktiv",
  "common.off": "aus",
  "common.noData": "Noch keine Daten",
  "common.unknownError": "Unbekannter Fehler",
  "common.word": "Wort",
  "common.words": "Wörter",
  "common.category": "Kategorie",
  "common.severity": "Schweregrad",
  "common.action": "Aktion",
  "common.status": "Status",
  "common.language": "Sprache",
  "common.server": "Server",
  "common.members": "Mitglieder",
  "common.wordsCount": "{n} Wörter",

  // landing
  "landing.login": "Mit Discord anmelden",
  "landing.connecting": "Verbinde Backend…",
  "landing.hero1": "Dein Server.",
  "landing.hero2": "Deine Regeln.",
  "landing.tagline":
    "SafeWord filtert automatisch Schimpfwörter, Beleidigungen, Spam und toxische Begriffe — selbst wenn jemand versucht, den Filter zu umgehen. Professionelle Moderation für deine Community.",
  "landing.features": "Funktionen",
  "landing.securityNote": "OAuth2 • Keine Passwörter • Nur Server mit deinen Admin-Rechten",
  "landing.feature1.title": "Erweiterte Erkennung",
  "landing.feature1.text":
    "Umgehungen wie „id.iot“, „1di0t“ oder „i d i o t“ werden durch Textnormalisierung zuverlässig erkannt.",
  "landing.feature2.title": "Server eigene Filter",
  "landing.feature2.text": "Eigene Wörter, Kategorien und Aktionen pro Server — ganz ohne Code.",
  "landing.feature3.title": "Moderationslevel",
  "landing.feature3.text": "Fein abgestimmte Reaktionen: löschen, warnen, Timeout oder nur protokollieren.",
  "landing.feature4.title": "Blitzschnell",
  "landing.feature4.text": "Aho-Corasick-Matching normalisiert jede Nachricht in einem einzigen Durchlauf.",
  "landing.feature5.title": "Datenschutz",
  "landing.feature5.text": "Deine Daten bleiben in deiner eigenen Datenbank. Keine Weitergabe an Dritte.",
  "landing.feature6.title": "Professionelles Dashboard",
  "landing.feature6.text": "Verwalte alles über ein modernes Web-Dashboard — inklusive Statistiken und Sicherheitsvorfällen.",
  "landing.team": "Team",
  "landing.teamTitle": "Das Team hinter SafeWord",
  "landing.teamSubtitle": "Die Menschen, die SafeWord entwickeln und betreiben.",
  "landing.teamEmpty": "Noch keine Teammitglieder hinterlegt.",
  "landing.footer": "Offizieller Moderation-Bot",

  // dashboard home
  "dash.chooseServer": "Wähle einen Server",
  "dash.loggedInAs": "Angemeldet als {name} — du verwaltest diese Server.",
  "dash.adminPanel": "Admin Panel",
  "dash.adminDenied": "Zugriff verweigert — du bist kein Admin.",
  "dash.maintenance": "Wartungsmodus aktiv — einige Funktionen können vorübergehend eingeschränkt sein.",
  "dash.noServers": "Wir konnten keine Server finden, auf denen du Administrator bist.",
  "dash.connected": "Mit SafeWord verbunden ({count})",
  "dash.notInstalled": "Noch nicht installiert ({count})",
  "dash.openDashboard": "Dashboard öffnen →",
  "dash.inviteBot": "Bot einladen",

  // guild navigation
  "guild.sidebarTitle": "Server Dashboard",
  "guild.allServers": "Alle Server",
  "nav.overview": "Übersicht",
  "nav.filters": "Filter",
  "nav.settings": "Einstellungen",
  "nav.profile": "Bot Profil",
  "nav.security": "Sicherheit",

  // guild overview
  "overview.loading": "Lade Server-Daten…",
  "overview.serverIdLine": "Server-ID {id} • Status {status} • SafeWord v{version}",
  "overview.violationsToday": "Verstöße heute",
  "overview.warnings": "Verwarnungen",
  "overview.detectedWords": "Erkannte Begriffe",
  "overview.violations30": "Verstöße (30 Tage)",
  "overview.topWords": "Häufigste Filterbegriffe",
  "overview.actions": "Ausgeführte Aktionen",
  "overview.noActions": "Noch keine Aktionen",

  // filters
  "filters.title": "Filter",
  "filters.subtitle": "Eigene Wörter verwalten und Standardlisten aktivieren.",
  "filters.addWord": "Wort hinzufügen",
  "filters.wordPlaceholder": "z.B. spammer",
  "filters.severityHigh": "· hoch",
  "filters.yourWords": "Eigene Wörter ({count})",
  "filters.noWords": "Noch keine eigenen Wörter. Füge oben ein Wort hinzu.",
  "filters.added": "„{word}“ hinzugefügt.",
  "filters.th.statusActions": "Status / Aktionen",
  "filters.stdLists": "Standardlisten",
  "filters.stdListActive": "Aktiv",
  "filters.stdListInactive": "Inaktiv",
  "filters.stdListsNote": "Standardlisten werden vom SafeWord-Team gepflegt und automatisch aktualisiert.",
  "filters.stdWords": "Standardwörter ({count})",
  "filters.stdWordsSubtitle": "Einzelne Wörter aus den Standardlisten für diesen Server anpassen.",
  "filters.stdWordsReset": "Zurücksetzen",
  "filters.stdWordsResetAll": "Alle zurücksetzen",
  "filters.stdWordsActionNone": "Standard",
  "filters.stdWordsSaved": "Wort „{word}“ gespeichert.",
  "filters.stdWordsNote": "Anpassungen gelten nur für diesen Server und haben Vorrang vor den Standardlisten.",

  // settings
  "settings.title": "Einstellungen",
  "settings.subtitle": "Moderationsverhalten von SafeWord.",
  "settings.loading": "Lade Einstellungen…",
  "settings.general": "Allgemein",
  "settings.modLevel": "Moderationslevel (1–5)",
  "settings.levelOption": "Level {s} — {desc}",
  "settings.levelStrict": "sehr streng",
  "settings.levelBalanced": "ausgeglichen",
  "settings.levelHeavy": "nur schwerste",
  "settings.logChannelId": "Log / Ankündigungs-Kanal",
  "settings.logChannelPlaceholder": "z.B. 123456789012345678",
  "settings.logChannelAlt": "Ankündigungen und Logs werden hierhin gesendet.",
  "settings.logChannelNone": "Kein Kanal (automatisch)",
  "settings.timeout": "Timeout Dauer (Minuten)",
  "settings.actionDelete": "Nachricht löschen",
  "settings.actionDeleteDesc": "Entfernt die Nachricht vom Server.",
  "settings.actionWarn": "Benutzer warnen",
  "settings.actionWarnDesc": "Erteilt eine Verwarnung per DM und zählt sie.",
  "settings.actionTimeout": "Timeout",
  "settings.actionTimeoutDesc": "Schweigt den Benutzer für eine gewählte Dauer.",
  "settings.actionLog": "Nur loggen",
  "settings.actionLogDesc": "Protokolliert den Vorfall im Log Channel.",
  "settings.actions": "Aktionen",

  // bypass
  "settings.bypass": "Bypass",
  "settings.bypassDesc": "Rollen und Benutzer, die niemals gefiltert werden. Serverbesitzer und Administratoren sind immer ausgenommen.",
  "settings.bypassRoles": "Bypass-Rollen (IDs, kommasepariert)",
  "settings.bypassUsers": "Bypass-Benutzer (IDs, kommasepariert)",
  "settings.bypassPlaceholder": "z.B. 123456789012345678, 234567890123456789",
  "settings.bypassHint": "Du kannst die ID im Discord über „Server-Einstellungen → Rollen/Benutzer → Rechtsklick → ID kopieren“ erhalten. Alternativ `/filter bypass-add` im Discord.",

  // guild profile
  "profile.title": "Bot Profilbild",
  "profile.subtitle": "Das Profilbild des Bots für diesen Server anpassen.",
  "profile.info":
    "Discord erlaubt pro Bot nur ein globales Profilbild. Dein Upload überschreibt das aktuelle Bild für alle Server (der letzte Upload gewinnt). Bei anstößigen Bildern können die SafeWord-Admins es im Adminbereich ändern oder zurücksetzen. Die Activity bleibt immer „Made by DevCoder“.",
  "profile.header": "Profilbild",
  "profile.upload": "Profilbild hochladen",
  "profile.noImage": "Kein Bild",
  "profile.lastChanged": "Zuletzt geändert am {date}",
  "profile.readError": "Datei konnte nicht gelesen werden",
  "profile.pickError": "Bitte ein Bild wählen (PNG/JPG/GIF/WebP).",
  "profile.saved": "Profilbild gespeichert ✓",
  "profile.saveBtn": "Profilbild speichern",

  // charts
  "charts.violations": "Verstöße",
  "charts.servers": "Server",
  "charts.noData": "Noch keine Daten",

  // security / incidents (guild + admin)
  "security.disabledBanner":
    "SafeWord wurde für diesen Server deaktiviert (Selbstschutz). Ein Angriffs- oder Nuke-Versuch wurde erkannt und die Verarbeitung gestoppt. Ein Administrator kann den Bot hier wieder aktivieren.",
  "security.reEnable": "Bot wieder aktivieren",
  "security.reEnableConfirm": "SafeWord für diesen Server wirklich wieder aktivieren?",
  "security.title": "Sicherheit",
  "security.subtitle": "Angriffs- und Nuke-Versuche, bei denen sich der Bot selbst deaktiviert hat.",
  "security.noIncidents": "Keine Sicherheitsvorfälle.",
  "security.open": "Offen",
  "security.resolved": "Behoben",
  "security.attempted": "Was versucht wurde",
  "security.consequence": "Konsequenz",
  "security.actor": "User-ID",
  "security.guild": "Server",
  "security.date": "Zeitpunkt",
  "security.detail": "Details",
  "security.resolve": "Als behoben markieren",
  "security.resolveConfirm": "Diesen Vorfall als behoben markieren?",
  "security.enabledToast": "SafeWord wurde wieder aktiviert.",
  "security.kind.command_flood": "Befehlsspam (mögliche Manipulation)",
  "security.kind.mention_flood": "Erwähnungs-Flut gegen den Bot",
  "security.kind.channel_nuke": "Massenhafte Kanal-Erstellung/-Löschung (Nuke-Versuch)",
  "security.kind.bot_banned": "Bot wurde gebannt",
  "security.kind.bot_removed": "Bot wurde vom Server entfernt",

  // push notifications
  "push.enable": "Benachrichtigungen aktivieren",
  "push.disable": "Benachrichtigungen deaktivieren",
  "push.enabled": "Benachrichtigungen aktiv ✓",
  "push.denied": "Benachrichtigungen wurden im Browser blockiert.",
  "push.unsupported": "Dieser Browser unterstützt keine Push-Benachrichtigungen.",
  "push.error": "Push-Aktivierung fehlgeschlagen.",
  "push.unsubscribed": "Benachrichtigungen deaktiviert.",
  "push.test": "Test-Nachricht senden",
  "push.testSent": "Test-Nachricht gesendet ✓",
  "push.testError": "Test-Nachricht fehlgeschlagen. Ist die Benachrichtigung aktiv?",
  "push.testEmpty": "Keine Push-Abonnements gefunden. Aktivere zuerst Benachrichtigungen.",

  // admin navigation
  "admin.sidebarTitle": "Adminbereich",
  "admin.sidebarSubtitle": "Nur für SafeWord-Entwickler",
  "admin.headerLabel": "SafeWord Entwickler-Adminbereich",
  "admin.overview": "Übersicht",
  "admin.servers": "Server",
  "admin.stats": "Statistiken",
  "admin.profile": "Bot Profil",
  "admin.updates": "Updates",
  "admin.lists": "Wortlisten",
  "admin.team": "Team",
  "admin.logs": "Fehler & Logs",
  "admin.incidents": "Vorfälle",

  // admin overview
  "adminOv.loading": "Lade Übersicht…",
  "adminOv.title": "Übersicht",
  "adminOv.started": "SafeWord v{version} • Gestartet: {date}",
  "adminOv.bot": "Bot",
  "adminOv.api": "API",
  "adminOv.database": "Datenbank",
  "adminOv.maintenance": "Wartungsmodus ist aktiv.",
  "adminOv.servers": "Discord-Server",
  "adminOv.activeUsers": "Aktive Nutzer",
  "adminOv.violationsToday": "Verstöße heute",
  "adminOv.errors": "Fehler gesamt",
  "adminOv.lastUpdates": "Letzte Updates",
  "adminOv.noUpdates": "Noch keine Updates veröffentlicht.",
  "adminOv.metrics": "Metriken",
  "adminOv.totalServers": "Server gesamt",
  "adminOv.activeServers": "Aktive Server",
  "adminOv.totalViolations": "Verstöße gesamt",
  "adminOv.errorLogs": "Fehler in Logs",

  // admin servers
  "adServ.title": "Server Verwaltung",
  "adServ.subtitle": "{count} verbundene Discord-Server",
  "adServ.thServer": "Server",
  "adServ.thId": "ID",
  "adServ.thMembers": "Mitglieder",
  "adServ.thVersion": "Bot Version",
  "adServ.thStatus": "Status",
  "adServ.thActions": "Aktionen",
  "adServ.deactivate": "Deaktivieren",
  "adServ.activate": "Aktivieren",
  "adServ.maintenance": "Wartung",
  "adServ.kick": "Bot entfernen",
  "adServ.kickConfirm": "Bot wirklich von diesem Server entfernen?",
  "adServ.invite": "Einladen",
  "adServ.inviteNew": "Neu generieren",
  "adServ.thInvite": "Invite-Link",

  // admin team
  "adTeam.title": "Team",
  "adTeam.subtitle": "Verwalte das Team, das auf der Landing-Page angezeigt wird.",
  "adTeam.name": "Name",
  "adTeam.namePlaceholder": "z. B. Max Mustermann",
  "adTeam.role": "Rolle",
  "adTeam.rolePlaceholder": "z. B. Gründer",
  "adTeam.parent": "Übergeordnet",
  "adTeam.noParent": "Keine (oberste Ebene)",
  "adTeam.sortOrder": "Sortierung",
  "adTeam.thName": "Name",
  "adTeam.thRole": "Rolle",
  "adTeam.thParent": "Übergeordnet",
  "adTeam.thOrder": "Sortierung",
  "adTeam.thActions": "Aktionen",
  "adTeam.saved": "Team gespeichert.",
  "adTeam.deleteConfirm": "Mitglied \"{name}\" wirklich entfernen?",
  "adTeam.empty": "Noch keine Teammitglieder.",

  // admin stats
  "adStats.loading": "Lade Statistiken…",
  "adStats.title": "Statistiken",
  "adStats.subtitle": "Gesamtauswertung über alle Server.",
  "adStats.activeServers": "Aktive Server",
  "adStats.activeUsers": "Aktive Nutzer",
  "adStats.totalViolations": "Verstöße gesamt",
  "adStats.filterWords": "Filterbegriffe",
  "adStats.perDay": "Verstöße pro Tag",
  "adStats.growth": "Server-Wachstum",
  "adStats.topWords": "Häufigste Begriffe",
  "adStats.actions": "Aktionen",
  "adStats.topServers": "Top Server",

  // admin logs
  "adLogs.title": "Fehler & Logs",
  "adLogs.subtitle": "API-, Discord-, Datenbank-Fehler und Bot-Abstürze.",
  "adLogs.allLevels": "Alle Level",
  "adLogs.allTypes": "Alle Typen",
  "adLogs.none": "Keine Logs vorhanden.",

  // admin lists
  "adLists.title": "Wortlisten Verwaltung",
  "adLists.subtitle": "Globale Standardlisten bearbeiten — Änderungen verteilen sich an alle Server.",
  "adLists.saved": "Gespeichert: {count} Wörter (v{version})",
  "adLists.choose": "Wähle links eine Wortliste aus.",
  "adLists.newWord": "Neues Wort",
  "adLists.severity": "Severity {s}",

  // admin updates
  "adUpd.title": "Update-System",
  "adUpd.subtitle": "Neue Versionen ankündigen oder direkt veröffentlichen.",
  "adUpd.new": "Neues Update",
  "adUpd.version": "Version",
  "adUpd.titleLabel": "Titel",
  "adUpd.titlePlaceholder": "z.B. Improved Toxicity Detection",
  "adUpd.changelog": "Changelog",
  "adUpd.changelogPlaceholder": "- Neue Filter-Engine\n- Bessere Erkennung von Umgehungen\n- Neue deutsche Wortliste",
  "adUpd.maintenance": "Wartungsmodus aktivieren",
  "adUpd.announce": "Ankündigen",
  "adUpd.release": "Veröffentlichen & Verteilen",
  "adUpd.announced": "Angekündigt: {version}",
  "adUpd.released": "Veröffentlicht: {version} — Deploy: {deploy}",
  "adUpd.history": "Update-Verlauf",
  "adUpd.none": "Noch keine Updates.",
  "adUpd.maintenanceBadge": "Wartung",

  // admin profile
  "adProf.title": "Bot Profilbild (Admin)",
  "adProf.subtitle": "Moderieren & zurücksetzen, wenn Server-Admins unpassende Bilder hochladen.",
  "adProf.reset": "Auf Standard zurücksetzen",
  "adProf.resetConfirm": "Profilbild wirklich auf Standard (kein Bild) zurücksetzen?",
  "adProf.current": "Aktuelles Profilbild",
  "adProf.noImage": "Kein Bild",
  "adProf.replace": "Profilbild ersetzen",
  "adProf.apply": "Profilbild anwenden (Override)",
  "adProf.lastChangedBy": "Zuletzt geändert von {by} am {date}",
  "adProf.history": "Änderungsverlauf",
  "adProf.noChanges": "Noch keine Änderungen.",
  "adProf.by": "von",
  "adProf.server": "Server",
  "adProf.adminPanel": "Admin-Panel",
};

const en: Record<string, string> = {
  // common
  "common.logout": "Log out",
  "common.loading": "Loading…",
  "common.error": "Unknown error",
  "common.save": "Save",
  "common.saved": "Saved ✓",
  "common.saving": "Saving…",
  "common.add": "Add",
  "common.delete": "Delete",
  "common.refresh": "Refresh",
  "common.enable": "Enable",
  "common.disable": "Disable",
  "common.active": "active",
  "common.off": "off",
  "common.noData": "No data yet",
  "common.unknownError": "Unknown error",
  "common.word": "Word",
  "common.words": "words",
  "common.category": "Category",
  "common.severity": "Severity",
  "common.action": "Action",
  "common.status": "Status",
  "common.language": "Language",
  "common.server": "Server",
  "common.members": "Members",
  "common.wordsCount": "{n} words",

  // landing
  "landing.login": "Log in with Discord",
  "landing.connecting": "Connecting to backend…",
  "landing.hero1": "Your server.",
  "landing.hero2": "Your rules.",
  "landing.tagline":
    "SafeWord automatically filters profanity, insults, spam and toxic terms — even when someone tries to bypass the filter. Professional moderation for your community.",
  "landing.features": "Features",
  "landing.securityNote": "OAuth2 • No passwords • Only servers you can manage",
  "landing.feature1.title": "Advanced detection",
  "landing.feature1.text":
    "Bypasses like \"id.iot\", \"1di0t\" or \"i d i o t\" are reliably caught through text normalization.",
  "landing.feature2.title": "Per-server filters",
  "landing.feature2.text": "Custom words, categories and actions per server — no code required.",
  "landing.feature3.title": "Moderation level",
  "landing.feature3.text": "Fine-tuned reactions: delete, warn, timeout or log only.",
  "landing.feature4.title": "Blazing fast",
  "landing.feature4.text": "Aho-Corasick matching normalizes every message in a single pass.",
  "landing.feature5.title": "Privacy",
  "landing.feature5.text": "Your data stays in your own database. No third-party sharing.",
  "landing.feature6.title": "Professional dashboard",
  "landing.feature6.text": "Manage everything through a modern web dashboard — including statistics and security incidents.",
  "landing.team": "Team",
  "landing.teamTitle": "The team behind SafeWord",
  "landing.teamSubtitle": "The people who build and operate SafeWord.",
  "landing.teamEmpty": "No team members yet.",
  "landing.footer": "Official moderation bot",

  // dashboard home
  "dash.chooseServer": "Choose a server",
  "dash.loggedInAs": "Logged in as {name} — you manage these servers.",
  "dash.adminPanel": "Admin Panel",
  "dash.adminDenied": "Access denied — you are not an admin.",
  "dash.maintenance": "Maintenance mode is active — some features may be temporarily limited.",
  "dash.noServers": "We couldn't find any servers where you are an administrator.",
  "dash.connected": "Connected with SafeWord ({count})",
  "dash.notInstalled": "Not installed yet ({count})",
  "dash.openDashboard": "Open dashboard →",
  "dash.inviteBot": "Invite bot",

  // guild navigation
  "guild.sidebarTitle": "Server Dashboard",
  "guild.allServers": "All servers",
  "nav.overview": "Overview",
  "nav.filters": "Filters",
  "nav.settings": "Settings",
  "nav.profile": "Bot profile",
  "nav.security": "Security",

  // guild overview
  "overview.loading": "Loading server data…",
  "overview.serverIdLine": "Server ID {id} • Status {status} • SafeWord v{version}",
  "overview.violationsToday": "Violations today",
  "overview.warnings": "Warnings",
  "overview.detectedWords": "Detected words",
  "overview.violations30": "Violations (30 days)",
  "overview.topWords": "Top filter words",
  "overview.actions": "Executed actions",
  "overview.noActions": "No actions yet",

  // filters
  "filters.title": "Filters",
  "filters.subtitle": "Manage custom words and enable default lists.",
  "filters.addWord": "Add word",
  "filters.wordPlaceholder": "e.g. spammer",
  "filters.severityHigh": "· high",
  "filters.yourWords": "Custom words ({count})",
  "filters.noWords": "No custom words yet. Add one above.",
  "filters.added": "Added \"{word}\".",
  "filters.th.statusActions": "Status / Actions",
  "filters.stdLists": "Default lists",
  "filters.stdListActive": "Active",
  "filters.stdListInactive": "Inactive",
  "filters.stdListsNote": "Default lists are maintained by the SafeWord team and updated automatically.",
  "filters.stdWords": "Default words ({count})",
  "filters.stdWordsSubtitle": "Adjust individual words from the default lists for this server.",
  "filters.stdWordsReset": "Reset",
  "filters.stdWordsResetAll": "Reset all",
  "filters.stdWordsActionNone": "Default",
  "filters.stdWordsSaved": "Word \"{word}\" saved.",
  "filters.stdWordsNote": "Changes apply to this server only and take precedence over the default lists.",

  // settings
  "settings.title": "Settings",
  "settings.subtitle": "SafeWord moderation behavior.",
  "settings.loading": "Loading settings…",
  "settings.general": "General",
  "settings.modLevel": "Moderation level (1–5)",
  "settings.levelOption": "Level {s} — {desc}",
  "settings.levelStrict": "very strict",
  "settings.levelBalanced": "balanced",
  "settings.levelHeavy": "only the heaviest",
  "settings.logChannelId": "Log / Announcement channel",
  "settings.logChannelPlaceholder": "e.g. 123456789012345678",
  "settings.logChannelAlt": "Announcements and logs are sent here.",
  "settings.logChannelNone": "No channel (automatic)",
  "settings.timeout": "Timeout duration (minutes)",
  "settings.actionDelete": "Delete message",
  "settings.actionDeleteDesc": "Removes the message from the server.",
  "settings.actionWarn": "Warn user",
  "settings.actionWarnDesc": "Issues a warning via DM and counts it.",
  "settings.actionTimeout": "Timeout",
  "settings.actionTimeoutDesc": "Mutes the user for a chosen duration.",
  "settings.actionLog": "Log only",
  "settings.actionLogDesc": "Logs the incident in the log channel.",
  "settings.actions": "Actions",

  // bypass
  "settings.bypass": "Bypass",
  "settings.bypassDesc": "Roles and users that are never filtered. Server owners and administrators are always exempt.",
  "settings.bypassRoles": "Bypass roles (IDs, comma-separated)",
  "settings.bypassUsers": "Bypass users (IDs, comma-separated)",
  "settings.bypassPlaceholder": "e.g. 123456789012345678, 234567890123456789",
  "settings.bypassHint": "Get the ID in Discord via \"Server Settings → Roles/Users → Right-click → Copy ID\". Or use `/filter bypass-add` in Discord.",

  // guild profile
  "profile.title": "Bot profile picture",
  "profile.subtitle": "Customize the bot's profile picture for this server.",
  "profile.info":
    "Discord allows only one global profile picture per bot. Your upload overwrites the current image for all servers (last upload wins). For inappropriate images, SafeWord admins can change or reset it from the admin area. The activity always stays \"Made by DevCoder\".",
  "profile.header": "Profile picture",
  "profile.upload": "Upload profile picture",
  "profile.noImage": "No image",
  "profile.lastChanged": "Last changed on {date}",
  "profile.readError": "File could not be read",
  "profile.pickError": "Please choose an image (PNG/JPG/GIF/WebP).",
  "profile.saved": "Profile picture saved ✓",
  "profile.saveBtn": "Save profile picture",

  // charts
  "charts.violations": "Violations",
  "charts.servers": "Servers",
  "charts.noData": "No data yet",

  // security / incidents (guild + admin)
  "security.disabledBanner":
    "SafeWord was disabled for this server (self-protection). An attack or nuke attempt was detected and processing was stopped. An administrator can re-enable the bot here.",
  "security.reEnable": "Re-enable bot",
  "security.reEnableConfirm": "Really re-enable SafeWord for this server?",
  "security.title": "Security",
  "security.subtitle": "Attack and nuke attempts where the bot disabled itself.",
  "security.noIncidents": "No security incidents.",
  "security.open": "Open",
  "security.resolved": "Resolved",
  "security.attempted": "What was attempted",
  "security.consequence": "Consequence",
  "security.actor": "User ID",
  "security.guild": "Server",
  "security.date": "Time",
  "security.detail": "Details",
  "security.resolve": "Mark as resolved",
  "security.resolveConfirm": "Mark this incident as resolved?",
  "security.enabledToast": "SafeWord was re-enabled.",
  "security.kind.command_flood": "Command flood (possible manipulation)",
  "security.kind.mention_flood": "Mention flood against the bot",
  "security.kind.channel_nuke": "Mass channel creation/deletion (nuke attempt)",
  "security.kind.bot_banned": "Bot was banned",
  "security.kind.bot_removed": "Bot was removed from the server",

  // push notifications
  "push.enable": "Enable notifications",
  "push.disable": "Disable notifications",
  "push.enabled": "Notifications enabled ✓",
  "push.denied": "Notifications were blocked in the browser.",
  "push.unsupported": "This browser does not support push notifications.",
  "push.error": "Could not enable push notifications.",
  "push.unsubscribed": "Notifications disabled.",
  "push.test": "Send test notification",
  "push.testSent": "Test notification sent ✓",
  "push.testError": "Test notification failed. Are notifications enabled?",
  "push.testEmpty": "No push subscriptions found. Enable notifications first.",

  // admin navigation
  "admin.sidebarTitle": "Admin area",
  "admin.sidebarSubtitle": "SafeWord staff only",
  "admin.headerLabel": "SafeWord Developer Admin Area",
  "admin.overview": "Overview",
  "admin.servers": "Servers",
  "admin.stats": "Statistics",
  "admin.profile": "Bot profile",
  "admin.updates": "Updates",
  "admin.lists": "Word lists",
  "admin.team": "Team",
  "admin.logs": "Errors & Logs",
  "admin.incidents": "Incidents",

  // admin overview
  "adminOv.loading": "Loading overview…",
  "adminOv.title": "Overview",
  "adminOv.started": "SafeWord v{version} • Started: {date}",
  "adminOv.bot": "Bot",
  "adminOv.api": "API",
  "adminOv.database": "Database",
  "adminOv.maintenance": "Maintenance mode is active.",
  "adminOv.servers": "Discord servers",
  "adminOv.activeUsers": "Active users",
  "adminOv.violationsToday": "Violations today",
  "adminOv.errors": "Total errors",
  "adminOv.lastUpdates": "Latest updates",
  "adminOv.noUpdates": "No updates published yet.",
  "adminOv.metrics": "Metrics",
  "adminOv.totalServers": "Total servers",
  "adminOv.activeServers": "Active servers",
  "adminOv.totalViolations": "Total violations",
  "adminOv.errorLogs": "Errors in logs",

  // admin servers
  "adServ.title": "Server management",
  "adServ.subtitle": "{count} connected Discord servers",
  "adServ.thServer": "Server",
  "adServ.thId": "ID",
  "adServ.thMembers": "Members",
  "adServ.thVersion": "Bot version",
  "adServ.thStatus": "Status",
  "adServ.thActions": "Actions",
  "adServ.deactivate": "Deactivate",
  "adServ.activate": "Activate",
  "adServ.maintenance": "Maintenance",
  "adServ.kick": "Remove bot",
  "adServ.kickConfirm": "Really remove the bot from this server?",
  "adServ.invite": "Invite",
  "adServ.inviteNew": "Regenerate",
  "adServ.thInvite": "Invite link",

  // admin team
  "adTeam.title": "Team",
  "adTeam.subtitle": "Manage the team shown on the landing page.",
  "adTeam.name": "Name",
  "adTeam.namePlaceholder": "e.g. Jane Doe",
  "adTeam.role": "Role",
  "adTeam.rolePlaceholder": "e.g. Founder",
  "adTeam.parent": "Reports to",
  "adTeam.noParent": "None (top level)",
  "adTeam.sortOrder": "Sort order",
  "adTeam.thName": "Name",
  "adTeam.thRole": "Role",
  "adTeam.thParent": "Reports to",
  "adTeam.thOrder": "Sort order",
  "adTeam.thActions": "Actions",
  "adTeam.saved": "Team saved.",
  "adTeam.deleteConfirm": "Really remove member \"{name}\"?",
  "adTeam.empty": "No team members yet.",

  // admin stats
  "adStats.loading": "Loading statistics…",
  "adStats.title": "Statistics",
  "adStats.subtitle": "Overall statistics across all servers.",
  "adStats.activeServers": "Active servers",
  "adStats.activeUsers": "Active users",
  "adStats.totalViolations": "Total violations",
  "adStats.filterWords": "Filter words",
  "adStats.perDay": "Violations per day",
  "adStats.growth": "Server growth",
  "adStats.topWords": "Top words",
  "adStats.actions": "Actions",
  "adStats.topServers": "Top servers",

  // admin logs
  "adLogs.title": "Errors & Logs",
  "adLogs.subtitle": "API, Discord and database errors plus bot crashes.",
  "adLogs.allLevels": "All levels",
  "adLogs.allTypes": "All types",
  "adLogs.none": "No logs available.",

  // admin lists
  "adLists.title": "Word list management",
  "adLists.subtitle": "Edit global default lists — changes apply to all servers.",
  "adLists.saved": "Saved: {count} words (v{version})",
  "adLists.choose": "Choose a word list on the left.",
  "adLists.newWord": "New word",
  "adLists.severity": "Severity {s}",

  // admin updates
  "adUpd.title": "Update system",
  "adUpd.subtitle": "Announce or publish new versions.",
  "adUpd.new": "New update",
  "adUpd.version": "Version",
  "adUpd.titleLabel": "Title",
  "adUpd.titlePlaceholder": "e.g. Improved Toxicity Detection",
  "adUpd.changelog": "Changelog",
  "adUpd.changelogPlaceholder": "- New filter engine\n- Better bypass detection\n- New English word list",
  "adUpd.maintenance": "Enable maintenance mode",
  "adUpd.announce": "Announce",
  "adUpd.release": "Publish & distribute",
  "adUpd.announced": "Announced: {version}",
  "adUpd.released": "Published: {version} — Deploy: {deploy}",
  "adUpd.history": "Update history",
  "adUpd.none": "No updates yet.",
  "adUpd.maintenanceBadge": "Maintenance",

  // admin profile
  "adProf.title": "Bot profile picture (Admin)",
  "adProf.subtitle": "Moderate & reset when server admins upload inappropriate images.",
  "adProf.reset": "Reset to default",
  "adProf.resetConfirm": "Really reset the profile picture to default (no image)?",
  "adProf.current": "Current profile picture",
  "adProf.noImage": "No image",
  "adProf.replace": "Replace profile picture",
  "adProf.apply": "Apply profile picture (override)",
  "adProf.lastChangedBy": "Last changed by {by} on {date}",
  "adProf.history": "Change history",
  "adProf.noChanges": "No changes yet.",
  "adProf.by": "by",
  "adProf.server": "Server",
  "adProf.adminPanel": "Admin panel",
};

const translations: Record<Lang, Record<string, string>> = { de, en };

const STORAGE_KEY = "safeword_lang";

export function urlSafeBase64ToUint8Array(base64: string): Uint8Array<ArrayBuffer> {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const base64Url = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64Url);
  const bytes = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
  return bytes;
}

interface I18nContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
  locale: string;
}

const I18nContext = createContext<I18nContextValue>({
  lang: "en",
  setLang: () => undefined,
  t: (key) => key,
  locale: "en-US",
});

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (stored === "de" || stored === "en") setLangState(stored);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang === "de" ? "de" : "en";
  }, [lang]);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    try {
      window.localStorage.setItem(STORAGE_KEY, l);
    } catch {
      /* ignore */
    }
  }, []);

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      let str = translations[lang][key] ?? translations.de[key] ?? key;
      if (vars) {
        for (const [k, v] of Object.entries(vars)) {
          str = str.split(`{${k}}`).join(String(v));
        }
      }
      return str;
    },
    [lang],
  );

  const value = useMemo<I18nContextValue>(
    () => ({ lang, setLang, t, locale: lang === "de" ? "de-DE" : "en-US" }),
    [lang, setLang, t],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  return useContext(I18nContext);
}
