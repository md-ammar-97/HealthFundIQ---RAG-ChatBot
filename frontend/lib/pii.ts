// Client-side PII detection — mirrors server-side guardrails/classifier.py patterns
const PII_PATTERNS = [
  /\b[A-Z]{5}[0-9]{4}[A-Z]\b/i,        // PAN card (India)
  /\b[0-9]{12}\b/,                       // Aadhaar (12-digit)
  /\b[0-9]{10,11}\b/,                    // Phone number
  /[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/,  // Email
];

export function containsPII(query: string): boolean {
  return PII_PATTERNS.some((p) => p.test(query));
}
