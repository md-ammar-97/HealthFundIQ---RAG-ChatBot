"use client";

import { motion, AnimatePresence } from "motion/react";
import { useEffect, useState } from "react";

const STEPS = [
  "Classifying query…",
  "Retrieving relevant fund facts…",
  "Checking source evidence…",
  "Generating cited answer…",
];

// Realistic ECG QRS waveform path for the loading animation
const ECG_D =
  "M0,40 L40,40 L50,40 L55,20 L60,60 L65,10 L70,70 L75,40 L85,40 " +
  "L90,32 L95,48 L100,40 L140,40 " +
  "L150,40 L160,40 L165,20 L170,60 L175,10 L180,70 L185,40 L195,40 " +
  "L200,32 L205,48 L210,40 L250,40 " +
  "L260,40 L270,40 L275,20 L280,60 L285,10 L290,70 L295,40 L310,40";

export function LoadingState() {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setStep((s) => (s < STEPS.length - 1 ? s + 1 : s));
    }, 700);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="bg-surface border border-border rounded-card p-5 flex flex-col gap-4">
      {/* ECG animation */}
      <div className="w-full h-14 overflow-hidden">
        <svg viewBox="0 0 320 80" className="w-full h-full" preserveAspectRatio="none">
          <path
            d={ECG_D}
            fill="none"
            stroke="#2563EB"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="ecg-path"
            opacity="0.7"
          />
        </svg>
      </div>
      {/* Step text */}
      <AnimatePresence mode="wait">
        <motion.p
          key={step}
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.15 }}
          className="text-[13px] text-missing-gray"
        >
          {STEPS[step]}
        </motion.p>
      </AnimatePresence>
      {/* Step dots */}
      <div className="flex gap-1.5">
        {STEPS.map((_, i) => (
          <div
            key={i}
            className={`h-1 rounded-full transition-all duration-300 ${
              i <= step ? "bg-trust-blue w-6" : "bg-border w-1"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
