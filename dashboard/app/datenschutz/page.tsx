import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Datenschutz — SafeWord",
  description: "Datenschutzerklärung für SafeWord.",
};

export default function DatenschutzPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-blurple transition-colors hover:text-blurple/80">
        ← Zurück zur Startseite
      </Link>
      <h1 className="mt-6 text-3xl font-bold text-white">Datenschutzerklärung</h1>

      <section className="mt-8 space-y-8 text-sm leading-relaxed text-gray-300">
        <div className="card">
          <h2 className="text-lg font-semibold text-white">1. Verantwortlicher</h2>
          <p className="mt-3">
            Verantwortlich für die Datenverarbeitung im Sinne der DSGVO ist der Inhaber von
            SafeWord. Die Kontaktdaten finden sich im <Link href="/impressum" className="text-blurple transition-colors hover:text-blurple/80">Impressum</Link>.
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">2. Datenerfassung auf dieser Website</h2>
          <p className="mt-3">
            Diese Website wird über den Hosting-Anbieter Vercel Inc., 340 S Lemon Ave #4133,
            Walnut, CA 91789, USA, bereitgestellt. Beim Aufruf dieser Website erhebt der
            Hosting-Anbieter automatisch technische Daten (z.&nbsp;B. IP-Adresse, Uhrzeit des
            Zugriffs, Browser-Typ). Diese Daten sind technisch erforderlich, um die Website
            auszuliefern. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO.
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">3. Anmeldung über Discord (OAuth)</h2>
          <p className="mt-3">
            Zum Anmelden nutzt SafeWord den OAuth-Login von Discord. Hierbei werden von Discord die
            öffentliche Benutzerkennung (User-ID), dein Benutzername und dein Avatar übertragen.
            Diese Daten dienen ausschließlich der Authentifizierung und der Verwaltung deiner
            Server im Dashboard. Eine Speicherung der Discord-Daten erfolgt nur, soweit dies für
            die Funktion des Dashboards erforderlich ist.
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">4. Cookies</h2>
          <p className="mt-3">
            Diese Website verwendet ausschließlich technisch notwendige Cookies bzw. Session-Daten
            (Authentifizierungs-Session), die für das Einloggen in das Dashboard erforderlich sind.
            Tracking- oder Analyse-Cookies von Drittanbietern werden nicht eingesetzt.
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">5. Deine Rechte</h2>
          <p className="mt-3">
            Du hast das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung,
            Datenübertragbarkeit sowie das Recht, einer Verarbeitung zu widersprechen
            (Art. 15–21 DSGVO). Zudem hast du das Recht, dich bei einer Aufsichtsbehörde zu
            beschweren. Sende Anfragen bitte an die im Impressum genannten Kontaktdaten.
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">6. Server- und Messaging-Daten</h2>
          <p className="mt-3">
            SafeWord verarbeitet Nachrichteninhalte ausschließlich zur Ausführung der
            Moderation-Funktionen (z.&nbsp;B. automatische Wortfilterung) in den Discord-Servern,
            auf denen der Bot freigeschaltet ist. Die Daten verbleiben in der eigenen Datenbank
            des Serverbetreibers und werden nicht an Dritte weitergegeben.
          </p>
        </div>
      </section>
    </main>
  );
}
