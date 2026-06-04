"use client";

import { motion } from "motion/react";

// Molecular nodes for the floating orb layer
const MOLECULAR_NODES = [
  { cx: "15%", cy: "25%", r: 5 },
  { cx: "25%", cy: "65%", r: 3.5 },
  { cx: "72%", cy: "20%", r: 4 },
  { cx: "80%", cy: "70%", r: 3 },
  { cx: "50%", cy: "45%", r: 6 },
  { cx: "60%", cy: "80%", r: 2.5 },
];

// Connections between molecular nodes
const CONNECTIONS = [
  [0, 4], [1, 4], [2, 4], [3, 5], [4, 5],
];

// Ticker funds list
const TICKER_CONTENT =
  "XLV · VHT · IXJ · IBB · FHLC · HDFC Pharma · Nippon India Pharma · Mirae Healthcare · SBI Healthcare · ICICI PHD · HHL.TO · XHC.TO · ZHU.TO · TDOC.TO · 2820.HK · 3174.HK · JP 1621 · JP 2639 · Wellington HC · Amova Asia HC · iShares Healthcare IE · Xtrackers MSCI HC · Lyxor Healthcare · ";
const TICKER_DOUBLED = TICKER_CONTENT.repeat(2);

export function HealthcareBackdrop() {
  return (
    <div
      className="backdrop-layer select-none"
      aria-hidden="true"
    >
      {/* Layer 1 — ECG/Heartbeat scroll (trust-blue) */}
      <div className="absolute inset-0 overflow-hidden">
        <svg
          className="absolute w-[200%] top-1/3"
          viewBox="0 0 896 80"
          preserveAspectRatio="none"
          style={{ opacity: 0.06 }}
        >
          <motion.path
            d={
              "M0,40 L30,40 L38,40 L42,18 L46,62 L50,6 L54,74 L58,40 L68,40 " +
              "L72,32 L76,48 L80,40 L112,40 " +
              "M112,40 L142,40 L150,40 L154,18 L158,62 L162,6 L166,74 L170,40 L180,40 " +
              "L184,32 L188,48 L192,40 L224,40 " +
              "M224,40 L254,40 L262,40 L266,18 L270,62 L274,6 L278,74 L282,40 L292,40 " +
              "L296,32 L300,48 L304,40 L336,40 " +
              "M336,40 L366,40 L374,40 L378,18 L382,62 L386,6 L390,74 L394,40 L404,40 " +
              "L408,32 L412,48 L416,40 L448,40 " +
              "M448,40 L478,40 L486,40 L490,18 L494,62 L498,6 L502,74 L506,40 L516,40 " +
              "L520,32 L524,48 L528,40 L560,40 " +
              "M560,40 L590,40 L598,40 L602,18 L606,62 L610,6 L614,74 L618,40 L628,40 " +
              "L632,32 L636,48 L640,40 L672,40 " +
              "M672,40 L702,40 L710,40 L714,18 L718,62 L722,6 L726,74 L730,40 L740,40 " +
              "L744,32 L748,48 L752,40 L784,40 " +
              "M784,40 L814,40 L822,40 L826,18 L830,62 L834,6 L838,74 L842,40 L852,40 " +
              "L856,32 L860,48 L864,40 L896,40"
            }
            stroke="#2563EB"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {/* Scrolling duplicate for seamless loop */}
          <motion.g
            animate={{ x: [0, -448] }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          >
            <path
              d={
                "M0,40 L30,40 L38,40 L42,18 L46,62 L50,6 L54,74 L58,40 L68,40 " +
                "L72,32 L76,48 L80,40 L112,40 " +
                "M112,40 L142,40 L150,40 L154,18 L158,62 L162,6 L166,74 L170,40 L180,40 " +
                "L184,32 L188,48 L192,40 L224,40 " +
                "M224,40 L254,40 L262,40 L266,18 L270,62 L274,6 L278,74 L282,40 L292,40 " +
                "L296,32 L300,48 L304,40 L336,40 " +
                "M336,40 L366,40 L374,40 L378,18 L382,62 L386,6 L390,74 L394,40 L404,40 " +
                "L408,32 L412,48 L416,40 L448,40"
              }
              stroke="#2563EB"
              strokeWidth="1.5"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </motion.g>
        </svg>
      </div>

      {/* Layer 2 — Molecular orbs (brand-teal) */}
      <div className="absolute inset-0">
        <svg className="w-full h-full" style={{ opacity: 0.05 }}>
          {/* Connection lines */}
          {CONNECTIONS.map(([a, b], i) => (
            <line
              key={i}
              x1={MOLECULAR_NODES[a].cx}
              y1={MOLECULAR_NODES[a].cy}
              x2={MOLECULAR_NODES[b].cx}
              y2={MOLECULAR_NODES[b].cy}
              stroke="#0D9488"
              strokeWidth="0.8"
              strokeDasharray="3 3"
            />
          ))}
          {/* Orbs */}
          {MOLECULAR_NODES.map((node, i) => (
            <motion.circle
              key={i}
              cx={node.cx}
              cy={node.cy}
              r={node.r}
              fill="#0D9488"
              animate={{ cy: [node.cy, `calc(${node.cy} - 10px)`, node.cy] }}
              transition={{
                duration: 3 + i * 0.3,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.4,
              }}
            />
          ))}
        </svg>
      </div>

      {/* Layer 3 — DNA Double Helix (primary-accent) */}
      <div className="absolute right-0 top-0 bottom-0 w-[18%]" style={{ opacity: 0.045 }}>
        <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Strand A */}
          <motion.path
            d={Array.from({ length: 20 }, (_, i) => {
              const y = (i / 19) * 100;
              const x = 50 + Math.sin((i / 19) * 4 * Math.PI) * 35;
              return `${i === 0 ? "M" : "L"}${x},${y}`;
            }).join(" ")}
            stroke="#1D4ED8"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
            animate={{ strokeDashoffset: [0, -40] }}
            style={{ strokeDasharray: "4 4" }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          />
          {/* Strand B */}
          <motion.path
            d={Array.from({ length: 20 }, (_, i) => {
              const y = (i / 19) * 100;
              const x = 50 - Math.sin((i / 19) * 4 * Math.PI) * 35;
              return `${i === 0 ? "M" : "L"}${x},${y}`;
            }).join(" ")}
            stroke="#1D4ED8"
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
            animate={{ strokeDashoffset: [0, -40] }}
            style={{ strokeDasharray: "4 4" }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear", delay: 0.5 }}
          />
          {/* Rungs connecting strands at crossing points */}
          {Array.from({ length: 8 }, (_, i) => {
            const t = (i + 0.5) / 8;
            const y = t * 100;
            const xA = 50 + Math.sin(t * 4 * Math.PI) * 35;
            const xB = 50 - Math.sin(t * 4 * Math.PI) * 35;
            return (
              <line
                key={i}
                x1={xA} y1={y} x2={xB} y2={y}
                stroke="#1D4ED8"
                strokeWidth="0.8"
                opacity="0.6"
              />
            );
          })}
        </svg>
      </div>

      {/* Layer 4 — Financial ticker strip (monospace) */}
      <div
        className="absolute bottom-0 left-0 right-0 h-8 overflow-hidden flex items-center"
        style={{ opacity: 0.06 }}
      >
        <motion.div
          className="whitespace-nowrap font-mono text-[11px] text-primary-accent"
          animate={{ x: ["0%", "-50%"] }}
          transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        >
          {TICKER_DOUBLED}
        </motion.div>
      </div>
    </div>
  );
}
