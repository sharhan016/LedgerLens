import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { useRef } from "react";

import { LedgerLensMark } from "../components/LedgerLensMark";
import { useAuth } from "../hooks/useAuth";
import type { Role } from "../types/api";

gsap.registerPlugin(useGSAP);

const accounts: Array<{
  role: Role;
  initials: string;
  name: string;
  title: string;
  access: string;
}> = [
  {
    role: "analyst",
    initials: "AN",
    name: "Asha Rao",
    title: "Policy Analyst",
    access: "Standard policy library",
  },
  {
    role: "compliance",
    initials: "CO",
    name: "Mira Fernandes",
    title: "Compliance Officer",
    access: "Restricted policies and audit traces",
  },
  {
    role: "admin",
    initials: "KA",
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
        gsap.from(".brand-hero-copy > *", {
          opacity: 0,
          y: 22,
          duration: 0.75,
          stagger: 0.1,
          ease: "power3.out",
        });
        gsap.from(".brand-product-surface", {
          opacity: 0,
          x: 34,
          duration: 0.95,
          ease: "power3.out",
        });
        gsap.from(".brand-account", {
          opacity: 0,
          y: 18,
          duration: 0.55,
          stagger: 0.08,
          ease: "power2.out",
        });
      });
      return () => motion.revert();
    },
    { scope: page },
  );

  return (
    <main className="brand-login" ref={page}>
      <nav className="brand-nav" aria-label="LedgerLens introduction">
        <a className="brand-wordmark" href="#top" aria-label="LedgerLens home">
          <LedgerLensMark compact />
          <span>LedgerLens</span>
        </a>
        <span className="brand-promise">Evidence in context</span>
        <span className="brand-environment"><i aria-hidden="true" /> Demo environment</span>
      </nav>

      <section className="brand-hero" id="top">
        <div className="brand-hero-copy">
          <span className="brand-folio">Banking policy knowledge / 01</span>
          <h1>Every answer,<br /><em>accounted for.</em></h1>
          <p>
            Search your bank's policy library and inspect the exact passages behind every
            answer. Access stays aligned with your role.
          </p>
          <a className="brand-primary-action" href="#accounts">Choose an account</a>
        </div>

        <div className="brand-product-wrap">
          <div className="brand-construction-mark" aria-hidden="true">
            <LedgerLensMark />
            <i /><i /><i />
          </div>
          <article className="brand-product-surface" aria-label="LedgerLens product preview">
            <header>
              <div className="brand-wordmark small"><LedgerLensMark compact /><span>LedgerLens</span></div>
              <span>Policy search</span>
              <span className="brand-role-chip">CO</span>
            </header>
            <div className="brand-search-preview">
              <span>What are the customer due diligence requirements?</span>
              <strong aria-hidden="true">Search</strong>
            </div>
            <div className="brand-answer-preview">
              <span>Policy answer</span>
              <h2>Customer due diligence requirements</h2>
              <p>Customers must be identified and verified using reliable, independent source documents.</p>
              <footer>
                <span>3 sources</span>
                <span>BCBS KYC (2023)</span>
                <span>Section 3.1</span>
              </footer>
            </div>
          </article>
        </div>
      </section>

      <section className="brand-principles" aria-label="LedgerLens principles">
        <div><span>Policy</span><strong>Find the governing record.</strong></div>
        <div><span>Proof</span><strong>See the passage behind the answer.</strong></div>
        <div><span>Provenance</span><strong>Keep source and access context attached.</strong></div>
      </section>

      <section className="brand-access" id="accounts">
        <div className="brand-access-intro">
          <span className="brand-folio">Demo access / 02</span>
          <h2>Enter the policy workspace.</h2>
          <p>Choose a role to see how the same evidence changes across access boundaries.</p>
          <div className="brand-ledger-lines" aria-hidden="true"><i /><i /><i /><i /><i /></div>
        </div>

        <div className="brand-accounts" aria-label="Demo accounts">
          {accounts.map((account) => (
            <button
              className="brand-account"
              disabled={loading}
              key={account.role}
              onClick={() => void login(account.role)}
              type="button"
            >
              <span className={`brand-account-badge ${account.role}`}>{account.initials}</span>
              <span className="brand-account-copy">
                <small>{account.title}</small>
                <strong>{account.name}</strong>
                <span>{account.access}</span>
              </span>
              <span className="brand-account-action">Continue</span>
            </button>
          ))}
          {error && (
            <p className="brand-error" role="alert">
              <strong>Could not open the workspace.</strong>
              <span>{error}</span>
              <small>Confirm that the LedgerLens backend is running, then try again.</small>
            </p>
          )}
        </div>
      </section>

      <footer className="brand-footer">
        <div className="brand-wordmark"><LedgerLensMark compact /><span>LedgerLens</span></div>
        <p>Policy. Proof. Provenance.</p>
        <span>Northstar Union Bank is fictional. All data is synthetic.</span>
      </footer>
    </main>
  );
}
