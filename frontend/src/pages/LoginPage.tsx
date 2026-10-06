import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useRef, useState } from "react";

import { useAuth } from "../hooks/useAuth";
import type { Role } from "../types/api";

gsap.registerPlugin(ScrollTrigger, useGSAP);

const personas: Array<{
  role: Role;
  name: string;
  remit: string;
  code: string;
  access: string;
}> = [
  {
    role: "analyst",
    name: "Asha Rao",
    remit: "Policy research and customer guidance",
    code: "AN",
    access: "Standard policy corpus",
  },
  {
    role: "compliance",
    name: "Mira Fernandes",
    remit: "Restricted policy and audit review",
    code: "CO",
    access: "Controlled records and traces",
  },
  {
    role: "admin",
    name: "Dev Malhotra",
    remit: "Knowledge operations and ingestion",
    code: "AD",
    access: "Corpus and system operations",
  },
];

const reviews = [
  {
    quote: "A policy answer is only useful when the reviewer can inspect the exact passage behind it.",
    name: "Grounded review",
    detail: "Citation, source version, and retrieval scores stay attached.",
  },
  {
    quote: "The same question should reveal different evidence when the operator's authority changes.",
    name: "Role-aware retrieval",
    detail: "Tenant and role filters apply before any candidate is returned.",
  },
  {
    quote: "A production decision needs a trace, not a persuasive paragraph without provenance.",
    name: "Inspectable reasoning",
    detail: "Routing, grounding, and evaluation records remain visible.",
  },
];

const revealCopy = [
  "LedgerLens keeps retrieval visible from the first query to the final citation.",
  "Every source is filtered by tenant and role before ranking begins.",
  "Every answer carries enough evidence for a human reviewer to challenge it.",
];

export function LoginPage() {
  const { login, loading, error } = useAuth();
  const page = useRef<HTMLElement>(null);
  const [reviewIndex, setReviewIndex] = useState(0);

  useGSAP(
    () => {
      const motion = gsap.matchMedia();
      motion.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.from(".taste-hero-copy > *", {
          opacity: 0,
          y: 36,
          duration: 0.9,
          stagger: 0.12,
          ease: "power3.out",
        });
        gsap.from(".taste-hero-visual", {
          opacity: 0,
          scale: 0.86,
          duration: 1.2,
          ease: "power3.out",
        });
        gsap.fromTo(
          ".taste-story-image",
          { opacity: 0.35, scale: 0.82 },
          {
            opacity: 1,
            scale: 1,
            ease: "none",
            scrollTrigger: {
              trigger: ".taste-story",
              start: "top 80%",
              end: "bottom 35%",
              scrub: true,
            },
          },
        );
        gsap.to(".reveal-word", {
          opacity: 1,
          stagger: 0.08,
          ease: "none",
          scrollTrigger: {
            trigger: ".taste-story-copy",
            start: "top 72%",
            end: "bottom 42%",
            scrub: true,
          },
        });
        ScrollTrigger.create({
          trigger: ".taste-story",
          start: "top top",
          end: "bottom bottom",
          pin: ".taste-story-anchor",
          pinSpacing: false,
        });
      });
      return () => motion.revert();
    },
    { scope: page },
  );

  const activeReview = reviews[reviewIndex];
  const moveReview = (direction: number) => {
    setReviewIndex((current) => (current + direction + reviews.length) % reviews.length);
  };

  return (
    <main className="taste-login" ref={page}>
      <nav className="taste-nav" aria-label="LedgerLens introduction">
        <a className="taste-wordmark" href="#top" aria-label="LedgerLens home">
          <span className="taste-mark">LL</span>
          <span>LedgerLens</span>
        </a>
        <div className="taste-nav-links">
          <a href="#evidence">Evidence model</a>
          <a href="#personas">Enter workspace</a>
        </div>
        <span className="taste-environment">
          <i aria-hidden="true" /> Synthetic environment
        </span>
      </nav>

      <section className="taste-hero" id="top">
        <div className="taste-hero-copy">
          <p className="taste-kicker">Banking knowledge infrastructure</p>
          <h1>Banking knowledge, with its evidence intact.</h1>
          <p className="taste-hero-lede">
            A role-aware knowledge workspace where every answer remains connected to its
            source, score, route, and grounding record.
          </p>
          <div className="taste-actions">
            <a className="taste-button primary" href="#personas">Choose your access</a>
            <a className="taste-button secondary" href="#evidence">Inspect the model</a>
          </div>
        </div>
        <figure className="taste-hero-visual">
          <img
            alt="Architectural banking archive with ordered records"
            src="https://picsum.photos/seed/ledger-archive/1280/1500"
          />
          <figcaption>
            <span>Evidence surface</span>
            <strong>Sources remain visible</strong>
            <small>Northstar Union Bank, synthetic corpus</small>
          </figcaption>
        </figure>
      </section>

      <div className="taste-marquee" aria-label="LedgerLens capabilities">
        <div>
          <span>Role-aware retrieval</span><i />
          <span>Inspectable citations</span><i />
          <span>Hybrid search</span><i />
          <span>Grounded generation</span><i />
          <span>Audit-ready traces</span><i />
          <span aria-hidden="true">Role-aware retrieval</span><i aria-hidden="true" />
          <span aria-hidden="true">Inspectable citations</span><i aria-hidden="true" />
          <span aria-hidden="true">Hybrid search</span><i aria-hidden="true" />
        </div>
      </div>

      <section className="taste-interest" id="evidence">
        <header className="taste-section-heading">
          <p className="taste-kicker">Designed for scrutiny</p>
          <h2>The answer is only the beginning of the record.</h2>
        </header>
        <div className="taste-bento">
          <article className="taste-bento-main">
            <div>
              <span>Retrieval</span>
              <strong>Hybrid candidates, ranked with purpose.</strong>
            </div>
            <p>Semantic and lexical signals combine before a reranker orders the final evidence set.</p>
            <div className="taste-signal-lines" aria-hidden="true">
              <i /><i /><i /><i /><i /><i />
            </div>
          </article>
          <article className="taste-bento-image">
            <img alt="Ordered financial archive" src="https://picsum.photos/seed/evidence-vault/1200/900" />
            <div><span>Corpus boundary</span><strong>Tenant first</strong></div>
          </article>
          <article className="taste-bento-compact dark">
            <span>Authorization</span>
            <strong>Filtered before ranking</strong>
            <p>Role and tenant scope reduce the candidate pool before relevance scoring.</p>
          </article>
          <article className="taste-bento-compact coral">
            <span>Grounding</span>
            <strong>Citations stay attached</strong>
            <p>Passages, versions, and confidence signals travel with the answer.</p>
          </article>
          <article className="taste-bento-compact light">
            <span>Operations</span>
            <strong>Every route leaves a trace</strong>
            <p>Evaluation and audit views expose how the system reached its result.</p>
          </article>
        </div>
      </section>

      <section className="taste-story">
        <div className="taste-story-anchor">
          <p className="taste-kicker">A visible chain of custody</p>
          <h2>From source document to decision surface.</h2>
          <figure className="taste-story-image">
            <img alt="Rows of preserved institutional records" src="https://picsum.photos/seed/audit-ledger/1100/850" />
          </figure>
        </div>
        <div className="taste-story-copy">
          {revealCopy.map((sentence) => (
            <p key={sentence}>
              {sentence.split(" ").map((word, index) => (
                <span className="reveal-word" key={`${word}-${index}`}>{word} </span>
              ))}
            </p>
          ))}
        </div>
      </section>

      <section className="taste-review" aria-live="polite">
        <div className="taste-review-portrait" aria-hidden="true">
          <img alt="" src={`https://picsum.photos/seed/review-${reviewIndex + 1}/720/900`} />
          <span>{String(reviewIndex + 1).padStart(2, "0")}</span>
        </div>
        <div className="taste-review-copy">
          <blockquote>{activeReview.quote}</blockquote>
          <div>
            <span><strong>{activeReview.name}</strong><small>{activeReview.detail}</small></span>
            <span className="taste-review-controls">
              <button onClick={() => moveReview(-1)} type="button" aria-label="Previous review">Prev</button>
              <button onClick={() => moveReview(1)} type="button" aria-label="Next review">Next</button>
            </span>
          </div>
        </div>
      </section>

      <section className="taste-entry" id="personas">
        <header className="taste-section-heading inverted">
          <p className="taste-kicker">Enter with a defined role</p>
          <h2>Choose the evidence you are authorized to see.</h2>
        </header>
        <div className="taste-accordions" aria-label="Demo personas">
          {personas.map((persona, index) => (
            <button
              className="taste-persona"
              disabled={loading}
              key={persona.role}
              onClick={() => void login(persona.role)}
              type="button"
            >
              <span className="taste-persona-code">{persona.code}</span>
              <span className="taste-persona-index">0{index + 1}</span>
              <span className="taste-persona-copy">
                <small>{persona.role}</small>
                <strong>{persona.name}</strong>
                <em>{persona.remit}</em>
                <span>{persona.access}</span>
              </span>
              <span className="taste-persona-action">Enter workspace</span>
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
        <p>Inspectable retrieval. Cited generation. Evidence-led decisions.</p>
        <span>Northstar Union Bank is entirely fictional.</span>
      </footer>
    </main>
  );
}
