// Which Indian script a value is written in, from its Unicode block. Used
// to label inputs ("As written (Bengali)") and to set the lang attribute,
// which screen readers and line breaking rely on.

const SCRIPTS = [
  { name: "Devanagari", lang: "hi", from: 0x0900, to: 0x097f },
  { name: "Bengali", lang: "bn", from: 0x0980, to: 0x09ff },
  { name: "Gurmukhi", lang: "pa", from: 0x0a00, to: 0x0a7f },
  { name: "Gujarati", lang: "gu", from: 0x0a80, to: 0x0aff },
  { name: "Odia", lang: "or", from: 0x0b00, to: 0x0b7f },
  { name: "Tamil", lang: "ta", from: 0x0b80, to: 0x0bff },
  { name: "Telugu", lang: "te", from: 0x0c00, to: 0x0c7f },
  { name: "Kannada", lang: "kn", from: 0x0c80, to: 0x0cff },
  { name: "Malayalam", lang: "ml", from: 0x0d00, to: 0x0d7f },
];

export function detectScript(text) {
  if (!text) return null;
  for (const char of text) {
    const code = char.codePointAt(0);
    const script = SCRIPTS.find((s) => code >= s.from && code <= s.to);
    if (script) return script;
  }
  return null;
}

/** The script most of these values are written in, or null. */
export function mainScript(values) {
  const counts = new Map();
  for (const value of values) {
    const script = detectScript(value);
    if (script) counts.set(script, (counts.get(script) ?? 0) + 1);
  }
  let best = null;
  for (const [script, count] of counts) {
    if (!best || count > counts.get(best)) best = script;
  }
  return best;
}

/** lang attribute for a value: its script's language, else English. */
export const langOf = (text) => detectScript(text)?.lang ?? "en";
