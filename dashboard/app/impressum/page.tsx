import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Impressum — SafeWord",
  description: "Impressum für SafeWord.",
};

export default function ImpressumPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-blurple transition-colors hover:text-blurple/80">
        ← Zurück zur Startseite
      </Link>
      <h1 className="mt-6 text-3xl font-bold text-white">Impressum</h1>

      <section className="mt-8 space-y-8 text-sm leading-relaxed text-gray-300">
        <div className="card">
          <h2 className="text-lg font-semibold text-white">Angaben gemäß § 5 DDG</h2>
          <p className="mt-3">
            SafeWord – Official moderation bot
            <br />
            Inhaber: <em>[Name Vorname Nachname]</em>
            <br />
            Adresse: <em>[Straße Hausnummer]</em>
            <br />
            PLZ Ort: <em>[PLZ Ort]</em>
            <br />
            Land: Deutschland
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">Kontakt</h2>
          <p className="mt-3">
            E-Mail: <em>[kontakt@example.de]</em>
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">Verantwortlich für den Inhalt</h2>
          <p className="mt-3">
            <em>[Name Vorname Nachname]</em>
            <br />
            <em>[Straße Hausnummer, PLZ Ort]</em>
          </p>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold text-white">Haftungsausschluss</h2>
          <p className="mt-3">
            Die Inhalte dieser Website wurden mit größter Sorgfalt erstellt. Für die Richtigkeit,
            Vollständigkeit und Aktualität der Inhalte kann jedoch keine Gewähr übernommen werden.
            Als Diensteanbieter sind wir für eigene Inhalte auf diesen Seiten nach den allgemeinen
            Gesetzen verantwortlich. Wir sind jedoch nicht verpflichtet, übermittelte oder
            gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf
            eine rechtswidrige Tätigkeit hinweisen.
          </p>
        </div>

        <p className="text-xs text-gray-500">
          Hinweis: Bitte ersetze die Platzhalter in eckigen Klammern durch deine echten Angaben.
        </p>
      </section>
    </main>
  );
}
