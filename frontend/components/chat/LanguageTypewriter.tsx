"use client";

import { Typewriter } from "react-simple-typewriter";

const WORDS = [
  "Ask in any language",
  "Hindi में पूछें",
  "日本語で聞く",
  "中文提问",
  "اسأل بالعربية",
  "Posez une question",
  "Haga una pregunta",
  "Auf Deutsch fragen",
  "한국어로 물어보세요",
  "Tanya dalam Bahasa Melayu",
];

export function LanguageTypewriter() {
  return (
    <div className="flex items-center justify-center gap-1.5 text-[13px] text-missing-gray">
      <span className="inline-block w-1.5 h-1.5 rounded-full bg-brand-teal shrink-0" />
      <span>
        Supports multiple languages —{" "}
        <span className="text-brand-teal font-medium">
          <Typewriter
            words={WORDS}
            loop={0}
            cursor
            cursorStyle="|"
            typeSpeed={70}
            deleteSpeed={40}
            delaySpeed={1500}
          />
        </span>
      </span>
    </div>
  );
}
