/**
 * Design Harness Validator
 * ========================
 * DESIGN.md의 스타일링 계약을 정적으로 강제한다.
 * fastapi의 `scripts/validate_harness.py`와 같은 역할을 프론트엔드에서 한다.
 *
 * 실행: pnpm design:check
 *
 * 검증 규칙:
 *   1. Tailwind 임의 색상 값 금지 — bg-[#111111] 같은 매직 넘버 대신 토큰을 쓴다.
 *   2. 전역 CSS는 app/globals.css 하나뿐 — 토큰 정의가 두 곳으로 갈라지지 않게 한다.
 *   3. Tailwind/shadcn 외 스타일링 라이브러리 금지 (styled-components, emotion, CSS Modules).
 *   4. JSX 인라인 style에 색상 리터럴 금지 — 동적 수치(transform 등)는 허용한다.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(fileURLToPath(import.meta.url), "..", "..");
const SKIP_DIRS = new Set(["node_modules", ".next", ".git", "public", "scripts"]);

/** 외부 브랜드 색은 globals.css의 토큰으로만 정의한다. 여기 값들이 유일한 예외 출처다. */
const BRAND_TOKENS = ["--brand-kakao", "--brand-kakao-foreground", "--brand-naver"];

const errors = [];

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP_DIRS.has(name)) continue;
    const full = join(dir, name);
    if (statSync(full).isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
}

const files = walk(ROOT);
const sourceFiles = files.filter((f) => /\.(tsx|ts)$/.test(f));
const cssFiles = files.filter((f) => f.endsWith(".css"));

// ── 규칙 1: 임의 색상 값 금지 ───────────────────────────────────────────────
const ARBITRARY_COLOR =
  /\[#[0-9a-fA-F]{3,8}\]|\[(?:rgb|rgba|hsl|hsla)\([^\]]*\)\]/g;

for (const file of sourceFiles) {
  const lines = readFileSync(file, "utf8").split("\n");
  lines.forEach((line, i) => {
    for (const hit of line.match(ARBITRARY_COLOR) ?? []) {
      errors.push(
        `[${relative(ROOT, file)}:${i + 1}] 임의 색상 값 '${hit}' — ` +
          `app/globals.css에 토큰을 정의하고 유틸리티(bg-surface 등)로 쓰세요.`,
      );
    }
  });
}

// ── 규칙 2: 전역 CSS는 하나 ────────────────────────────────────────────────
const expectedCss = join(ROOT, "app", "globals.css");
for (const file of cssFiles) {
  if (file !== expectedCss) {
    errors.push(
      `[${relative(ROOT, file)}] 전역 CSS가 둘 이상입니다. ` +
        `토큰 정의는 app/globals.css 한 곳에만 둡니다.`,
    );
  }
}
if (!cssFiles.includes(expectedCss)) {
  errors.push("app/globals.css가 없습니다. 디자인 토큰의 단일 출처입니다.");
}

// ── 규칙 3: 다른 스타일링 라이브러리 금지 ──────────────────────────────────
const BANNED_IMPORTS = ["styled-components", "@emotion/", ".module.css", ".module.scss"];
for (const file of sourceFiles) {
  const lines = readFileSync(file, "utf8").split("\n");
  lines.forEach((line, i) => {
    if (!/^\s*import\b/.test(line)) return;
    for (const banned of BANNED_IMPORTS) {
      if (line.includes(banned)) {
        errors.push(
          `[${relative(ROOT, file)}:${i + 1}] '${banned}' 사용 — ` +
            `스타일링은 Tailwind + shadcn/ui로 통일합니다.`,
        );
      }
    }
  });
}

// ── 규칙 4: 인라인 style의 색상 리터럴 금지 ────────────────────────────────
const INLINE_COLOR = /style=\{\{[^}]*(?:color|background|border|fill|stroke)[^}]*:[^}]*(?:#[0-9a-fA-F]{3,8}|rgb\(|hsl\()/;
for (const file of sourceFiles) {
  const lines = readFileSync(file, "utf8").split("\n");
  lines.forEach((line, i) => {
    if (INLINE_COLOR.test(line)) {
      errors.push(
        `[${relative(ROOT, file)}:${i + 1}] 인라인 style에 색상 리터럴 — ` +
          `색은 className과 토큰으로 표현합니다(동적 수치는 허용).`,
      );
    }
  });
}

// ── 브랜드 토큰 존재 확인 ──────────────────────────────────────────────────
const globals = cssFiles.includes(expectedCss) ? readFileSync(expectedCss, "utf8") : "";
for (const token of BRAND_TOKENS) {
  if (!globals.includes(token)) {
    errors.push(`app/globals.css에 브랜드 토큰 '${token}'이 없습니다.`);
  }
}

if (errors.length > 0) {
  console.error(`\n디자인 하네스 검증 실패 — ${errors.length}개 오류:\n`);
  for (const err of errors) console.error(`  ✗ ${err}`);
  console.error("\n규칙은 DESIGN.md를 참고하세요.\n");
  process.exit(1);
}

console.log(
  `디자인 하네스 검증 통과 — 소스 ${sourceFiles.length}개, CSS ${cssFiles.length}개 확인 완료.`,
);
