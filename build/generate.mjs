#!/usr/bin/env node
// Generates index.html and embed.html from ecosystem-registry.json.
// The registry is the single source of truth; the rendered HTML is a projection.
// Pure Node, no dependencies. Run: `node build/generate.mjs`
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(ROOT, "ecosystem-registry.json"), "utf8"));

const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const SECTIONS = [
  { id: "official", nav: "공식", title: "공식", titleEn: "Official", note: null },
  {
    id: "participation",
    nav: "참여",
    title: "참여",
    titleEn: "Participation",
    note: { ko: "Passport와 Agora에서도 직접 참여할 수 있습니다 (위 공식 섹션 참조).", en: "You can also take part through Passport and Agora — see Official above." },
  },
  {
    id: "intelligence",
    nav: "AI 분석",
    title: "AI 분석",
    titleEn: "Intelligence",
    note: { ko: "AI가 정리한 참고 정보입니다. 공식 입장이 아닙니다.", en: "AI-generated reference context. Not an official position." },
  },
  { id: "showcase", nav: "체험", title: "세계관 체험", titleEn: "Showcase", note: { ko: "Mossland 세계관을 둘러보고 체험하는 공간입니다.", en: "Explore and experience the Mossland world." } },
  {
    id: "labs",
    nav: "실험실",
    title: "실험실",
    titleEn: "Labs",
    note: { ko: "실험 단계입니다. 공식 제품이나 거버넌스가 아니며, 최종 결정과 실행은 사람과 MOC 홀더의 몫입니다.", en: "Experimental. Not official products or governance — humans and MOC holders decide." },
  },
  { id: "developers", nav: "개발자", title: "개발자", titleEn: "Developers", note: null },
  {
    id: "markets",
    nav: "시세·거래소",
    title: "시세·거래소",
    titleEn: "Markets / Third-party",
    note: { ko: "제3자 거래소·시세 링크는 참고용이며, 거래 권유가 아닙니다.", en: "Third-party market links are provided for reference only and are not trading recommendations." },
  },
];

// Nav: keep it lean (~6 anchors). Show the high-traffic sections.
const NAV_IDS = ["official", "participation", "intelligence", "showcase", "labs", "markets"];

// Chip = trust signal, data-driven (not id-string-driven). Color carries the
// meaning: green = verified Mossland (on- or off-domain), amber = Labs, grey =
// genuine third-party. Documented in the on-page legend.
function chipFor(s) {
  if (s.artifact) return { t: "자료", c: "chip muted" }; // dev data files
  if (s.tier === "labs") return { t: s.status === "offline" ? "연구" : "실험실", c: "chip lab" };
  if (s.owner === "third-party" || s.tier === "third_party") return { t: "제3자", c: "chip third" };
  if (s.tier === "official_beta") return { t: "베타", c: "chip accent" };
  if (s.status === "beta") return { t: "베타", c: "chip beta" };
  return { t: "공식", c: "chip" };
}

function domLine(s) {
  let d = esc(s.domain);
  if (s.ticker) d += ` · ${esc(s.ticker)}`;
  if (s.runtime) d += ` · 플레이 ${esc(s.runtime.domain)}`;
  return d;
}

function card(s) {
  const chip = chipFor(s);
  const role = esc(s.labelKo || s.label || ""); // KR-primary, single clean line
  const cls = "link" + (s.featured ? " featured" : "");
  return `              <a class="${cls}" href="${esc(s.url)}" target="_blank" rel="noreferrer noopener">
                <span class="link-copy">
                  <strong>${esc(s.name)}<span class="ext" aria-hidden="true">↗</span><span class="sr-only"> (새 창에서 열림 / opens in a new tab)</span></strong>
                  <span class="role">${role}</span>
                  <span class="dom">${domLine(s)}</span>
                </span>
                <span class="${chip.c}">${esc(chip.t)}</span>
              </a>`;
}

function renderSections() {
  const visible = reg.services.filter((s) => !s.hidden && s.section);
  const out = [];
  for (const meta of SECTIONS) {
    const items = visible.filter((s) => s.section === meta.id);
    if (!items.length) continue;
    const noteHtml = meta.note
      ? `\n              <p class="note"><span lang="ko">${esc(meta.note.ko)}</span><span lang="en">${esc(meta.note.en)}</span></p>`
      : "";
    out.push(`          <section class="section${meta.id === "labs" ? " labs" : ""}" id="${meta.id}" aria-labelledby="h-${meta.id}">
            <div class="section-head">
              <div>
                <h2 id="h-${meta.id}" lang="ko">${esc(meta.title)} <span class="en">${esc(meta.titleEn)}</span></h2>${noteHtml}
              </div>
            </div>
            <div class="list">
${items.map(card).join("\n")}
            </div>
          </section>`);
  }
  return out.join("\n\n");
}

function jsonLd() {
  const first = reg.services.filter(
    (s) => s.owner === "mossland" && !["third_party", "registry"].includes(s.tier) && !["registry-json", "llms-txt", "sitemap"].includes(s.id)
  );
  const sameAs = [...new Set(first.map((s) => s.url.replace(/\/$/, "")))];
  const org = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Mossland",
    url: "https://www.moss.land/",
    logo: "https://links.moss.land/apple-touch-icon.png",
    sameAs,
  };
  const listed = reg.services.filter((s) => !s.hidden && s.section);
  const itemList = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: "Mossland Verified Links",
    description: reg.description,
    itemListElement: listed.map((s, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: s.name,
      url: s.url,
      description: s.label || s.labelKo,
    })),
  };
  return (
    `    <script type="application/ld+json">\n${JSON.stringify(org, null, 2)}\n    </script>\n` +
    `    <script type="application/ld+json">\n${JSON.stringify(itemList, null, 2)}\n    </script>`
  );
}

const STYLE = readFileSync(join(ROOT, "build", "style.css"), "utf8");

const HEAD_META = `    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mossland 공식 링크 · Verified Links</title>
    <meta
      name="description"
      content="Mossland의 공식 도메인과 생태계 앱, 실험실, 거래소 링크를 한곳에 모은 공식 안내 페이지. 여기에 없는 주소는 공식이 아닙니다. Official Mossland domains, ecosystem apps, labs, and exchange links in one place."
    />
    <meta name="theme-color" content="#1f3b2b" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="canonical" href="https://links.moss.land/" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Mossland" />
    <meta property="og:locale" content="ko_KR" />
    <meta property="og:locale:alternate" content="en_US" />
    <meta property="og:title" content="Mossland 공식 링크 · Verified Links" />
    <meta
      property="og:description"
      content="진짜 Mossland 도메인만 모은 공식 링크 모음 — Passport, 공시, 생태계 앱, 거래소. The verified directory of real Mossland links."
    />
    <meta property="og:url" content="https://links.moss.land/" />
    <meta property="og:image" content="https://links.moss.land/og.png" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="Mossland 공식 링크 · Verified Links" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:site" content="@TheMossland" />
    <meta name="twitter:title" content="Mossland 공식 링크 · Verified Links" />
    <meta
      name="twitter:description"
      content="진짜 Mossland 도메인만 모은 공식 링크 모음. The verified directory of real Mossland links."
    />
    <meta name="twitter:image" content="https://links.moss.land/og.png" />
    <meta name="twitter:image:alt" content="Mossland 공식 링크 · Verified Links" />
    <link rel="alternate" type="application/json" href="/ecosystem-registry.json" title="Mossland Ecosystem Registry" />`;

const NAV = NAV_IDS.map((id) => {
  const m = SECTIONS.find((x) => x.id === id);
  return `            <a href="#${id}">${esc(m.title)}</a>`;
}).join("\n");

const VERIFY = `          <div class="verify">
            <strong lang="ko">이 페이지의 모든 링크는 Mossland가 직접 운영·검증한 공식 도메인입니다. 여기에 없는 주소는 공식이 아니니 주의하세요.</strong>
            <span lang="en">Every link here is an official Mossland domain we operate and verify. If an address isn't listed here, treat it as unofficial.</span>
          </div>`;

const LEGEND = `        <details class="legend">
          <summary>표시 안내 / What the chips mean</summary>
          <ul>
            <li><span class="chip">공식</span> Mossland 공식·검증 도메인과 채널 / Verified Mossland domains and channels</li>
            <li><span class="chip accent">베타</span> 운영 중인 공식 베타 / Official service in open beta</li>
            <li><span class="chip lab">실험실</span> 실험 단계 — 공식 제품·거버넌스 아님 / Experimental, not official</li>
            <li><span class="chip third">제3자</span> Mossland 미검증 외부 링크 / Third-party, not verified by Mossland</li>
          </ul>
        </details>`;

const indexHtml = `<!DOCTYPE html>
<!-- Generated from ecosystem-registry.json by build/generate.mjs — do not edit by hand. -->
<html lang="ko">
  <head>
${HEAD_META}
    <style>
${STYLE}
    </style>
${jsonLd()}
  </head>
  <body>
    <main class="page">
      <div class="shell">
        <header class="topbar">
          <div class="brand">
            <div class="brand-mark" aria-hidden="true">ML</div>
            <div class="brand-copy">
              <strong>Mossland</strong>
              <span>links.moss.land</span>
            </div>
          </div>
          <nav class="nav" aria-label="Sections">
${NAV}
          </nav>
        </header>

        <section class="hero" aria-labelledby="title">
          <h1 id="title"><span lang="ko">Mossland 공식 링크</span><span class="en" lang="en">Mossland Verified Links</span></h1>
          <p lang="ko">Mossland의 공식 도메인과 생태계 앱, 실험실, 거래소 링크를 한곳에 모았습니다.</p>
          <p class="hero-sub" lang="en">Official Mossland domains, ecosystem apps, labs, and exchange links — all in one place.</p>
${VERIFY}
          <div class="hero-actions">
            <a href="https://passport.moss.land/" target="_blank" rel="noreferrer noopener">
              Open Passport
              <span class="beta-badge">BETA</span>
            </a>
            <a href="https://www.moss.land/" target="_blank" rel="noreferrer noopener">
              Official Website
            </a>
          </div>
        </section>

        <div class="sections">
${renderSections()}
        </div>

${LEGEND}

        <footer class="footer">
          <span>links.moss.land · Mossland 공식 링크</span>
          <a href="https://github.com/MosslandOpenDevs/links" target="_blank" rel="noreferrer noopener">
            MosslandOpenDevs/links
          </a>
        </footer>
      </div>
    </main>
  </body>
</html>
`;

const embedHtml = `<!DOCTYPE html>
<!-- Generated from ecosystem-registry.json by build/generate.mjs — do not edit by hand. -->
<!-- Chrome-less kiosk view for embedding inside play.wa / Mossverse. -->
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Mossland Verified Links</title>
    <meta name="robots" content="noindex" />
    <meta name="theme-color" content="#1f3b2b" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <link rel="canonical" href="https://links.moss.land/" />
    <style>
${STYLE}
    </style>
  </head>
  <body class="embed">
    <main class="page">
      <div class="shell">
        <section class="hero" aria-labelledby="title">
          <h1 id="title" class="kiosk"><span lang="ko">Mossland 검증 링크</span></h1>
${VERIFY}
        </section>
        <div class="sections">
${renderSections()}
        </div>
      </div>
    </main>
  </body>
</html>
`;

function renderLlms() {
  const lines = [];
  lines.push("# Mossland Verified Links");
  lines.push("");
  lines.push(`> ${reg.description}`);
  lines.push("");
  lines.push(
    "Mossland is infrastructure for the AI civilization. This file lists the verified official domains so search engines and AI agents can resolve real Mossland services and avoid impersonators. The machine-readable source of truth is the JSON registry below."
  );
  lines.push("");
  for (const meta of SECTIONS) {
    const items = reg.services.filter((s) => !s.hidden && s.section === meta.id);
    if (!items.length) continue;
    lines.push(`## ${meta.titleEn}`);
    if (meta.note) lines.push(`> ${meta.note.en}`);
    for (const s of items) {
      lines.push(`- [${s.name}](${s.url}): ${s.label || s.labelKo}`);
    }
    lines.push("");
  }
  lines.push("## Source of truth");
  lines.push("- [Ecosystem Registry (JSON)](https://links.moss.land/ecosystem-registry.json): structured, machine-readable registry of every Mossland service with tier, status, and Passport eligibility.");
  lines.push("- [Registry JSON Schema](https://links.moss.land/ecosystem-registry.schema.json): the contract for the registry.");
  lines.push("");
  lines.push("## Notes");
  lines.push("- Agora is a Public Decision Workbench, not a DAO governance app.");
  lines.push("- MAIT is an AI Copilot; it assists understanding and never decides or votes for users.");
  lines.push("- Labs (AO, Algora, BRIDGE) are experimental; not official products or governance.");
  lines.push("- Markets / third-party links are reference only and are not trading recommendations.");
  lines.push("");
  return lines.join("\n");
}

writeFileSync(join(ROOT, "index.html"), indexHtml);
writeFileSync(join(ROOT, "embed.html"), embedHtml);
writeFileSync(join(ROOT, "llms.txt"), renderLlms());
const count = reg.services.filter((s) => !s.hidden && s.section).length;
console.log(`Generated index.html + embed.html + llms.txt — ${count} visible links across ${SECTIONS.length} sections.`);
