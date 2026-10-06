import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { useRef } from "react";

import { useAuth } from "../hooks/useAuth";
import type { Role } from "../types/api";

gsap.registerPlugin(useGSAP);

const personas: Array<{
  role: Role;
  name: string;
  title: string;
  access: string;
}> = [
  {
    role: "analyst",
    name: "Asha Rao",
    title: "Policy Analyst",
    access: "Standard policy library",
  },
  {
    role: "compliance",
    name: "Mira Fernandes",
    title: "Compliance Officer",
    access: "Restricted policies and audit traces",
  },
  {
    role: "admin",
    name: "Dev Malhotra",
    title: "Knowledge Admin",
    access: "Document ingestion and system settings",
  },
];

export function LoginPage() {
  const { login, loading, error } = useAuth();
  const page = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const motion = gsap.matchMedia();
      motion.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.from(".taste-hero-copy > *", {
          opacity: 0,
          y: 24,
          duration: 0.7,
          stagger: 0.1,
          ease: "power3.out",
        });
        gsap.from(".taste-hero-visual", {
          opacity: 0,
          duration: 1,
          ease: "power3.out",
        });
      });
      return () => motion.revert();
    },
    { scope: page },
  );

  return (
    <main className="taste-login" ref={page}>
      <nav className="taste-nav" aria-label="LedgerLens introduction">
        <a className="taste-wordmark" href="#top" aria-label="LedgerLens home">
          <span className="taste-mark">LL</span>
          <span>LedgerLens</span>
        </a>
        <span className="taste-environment">
          <i aria-hidden="true" /> Demo environment
        </span>
      </nav>

      <section className="taste-hero" id="top">
        <div className="taste-hero-copy">
          <h1>Policy answers with sources attached.</h1>
          <p className="taste-hero-lede">
            Search your bank's policy library and see the exact passages behind every answer.
            What you can see depends on your role.
          </p>
          <div className="taste-actions">
            <a className="taste-button primary" href="#signin">Sign in</a>
          </div>
        </div>
        <figure className="taste-hero-visual">
          <img
            alt="Rows of archived records"
            src="https://picsum.photos/seed/ledger-archive/1280/1500"
          />
        </figure>
      </section>

      {/* TODO: "How it works" toggle / architecture explainer goes here */}

      <section className="taste-entry" id="signin">
        <header className="taste-section-heading inverted">
          <span aria-hidden="true" />
          <div>
            <h2>Sign in as</h2>
            <p>Pick a demo account to explore the workspace.</p>
          </div>
        </header>
        <div className="taste-accordions" aria-label="Demo accounts">
          {personas.map((persona) => (
            <button
              className="taste-persona"
              disabled={loading}
              key={persona.role}
              onClick={() => void login(persona.role)}
              type="button"
            >
              <span className="taste-persona-copy">
                <small>{persona.title}</small>
                <strong>{persona.name}</strong>
                <span>{persona.access}</span>
              </span>
              <span className="taste-persona-action">Continue</span>
            </button>
          ))}
        </div>
        {error && <p className="taste-error" role="alert">{error}</p>}
      </section>

      <footer className="taste-footer">
        <div className="taste-wordmark">
          <span className="taste-mark">LL</span>
          <span>LedgerLens</span>
        </div>
        <span>Northstar Union Bank is a fictional company. All data is synthetic.</span>
      </footer>
    </main>
  );
}
