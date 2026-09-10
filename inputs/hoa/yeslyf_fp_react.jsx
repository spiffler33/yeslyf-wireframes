import { useState } from "react";
import { LayoutDashboard, Umbrella, Shield, ArrowRightLeft, CreditCard, Receipt, CalendarHeart, ListChecks } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  LabelList,
} from "recharts";

/* ============================================================
   YESLYF — Financial Planning
   Overview tab, v1.
   The yellow-highlighted phrases in the hero come from the three
   psychometric intake answers below. Swap these values with the
   user's real responses and the narrative re-renders.
   ============================================================ */

const PSYCHOMETRICS = {
  stage: {
    question: "Where are you in your financial journey?",
    answer: "established, but wondering if you're on track",
  },
  feeling: {
    question: "How does money make you feel, day to day?",
    answer: "anxious — you worry about it more than you'd like",
  },
  aspiration: {
    question: "Five years from now, what do you want money to give you?",
    answer: "financial independence — options, not obligations",
  },
};

/* ---------- design tokens ---------- */
/* Brand palette — light mode
   Yellow = Possibility  #ffda00
   Deep Slate = Clarity  #2a2e38
   Soft Neutral = Context #fffff3
   Tertiary: olive #ac9440, sky #85b3e3, orchid #cd80d5, ocean #2a6dad */
const T = {
  pageBg: "#ffffff",
  ink: "#2a2e38",
  panelBg: "#fffff3",
  panelEdge: "#ffda00",
  highlight: "#ffda00",
  highlightTint: "#fdf3c0",
  label: "#ac9440",
  softNeutral: "#fffff3",
  slateDim: "#b7bcc6",
  slateMute: "#6b7280",
  rule: "#e5e7ea",
  ocean: "#2a6dad",
  sans: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, 'Helvetica Neue', Arial, sans-serif",
};

const Highlight = ({ children }) => (
  <span
    style={{
      background: T.highlightTint,
      color: T.ink,
      padding: "1px 5px",
      borderRadius: 3,
      boxShadow: `inset 0 -2px 0 ${T.highlight}`,
      boxDecorationBreak: "clone",
      WebkitBoxDecorationBreak: "clone",
    }}
  >
    {children}
  </span>
);

/* ---------- brand ---------- */
const BRAND_YELLOW = "#ffda00";

function YeslyfLogo({ size = 30 }) {
  return (
    <div
      style={{
        fontFamily:
          "'Snaga Uni Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, 'Helvetica Neue', Arial, sans-serif",
        fontWeight: 600,
        fontSize: size,
        lineHeight: 1,
        letterSpacing: "0.02em",
        color: T.ink,
        textTransform: "lowercase",
      }}
    >
      yeslyf
    </div>
  );
}

/* ---------- hero panel (the image) ---------- */
function PlanNarrative({ p }) {
  return (
    <section
      style={{
        background: T.panelBg,
        border: `1px solid ${T.rule}`,
        borderLeft: `4px solid ${T.panelEdge}`,
        borderRadius: 8,
        padding: "36px 40px 32px",
      }}
    >
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 12,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.ink,
          marginBottom: 22,
        }}
      >
        Your plan — built on what you told us
      </div>

      <p
        style={{
          fontFamily: T.sans,
          fontSize: 19,
          fontWeight: 400,
          lineHeight: 1.8,
          color: T.ink,
          margin: 0,
        }}
      >
        You told us you're <Highlight>{p.stage.answer}</Highlight>. That you're
        feeling <Highlight>{p.feeling.answer}</Highlight>. And that what you
        want — five years from now — is{" "}
        <Highlight>{p.aspiration.answer}</Highlight>.
      </p>

      <p
        style={{
          fontFamily: T.sans,
          fontSize: 15,
          color: T.slateMute,
          marginTop: 26,
          marginBottom: 0,
        }}
      >
        This plan is built on that. Your numbers. Your timeline. Your
        aspiration.
      </p>
    </section>
  );
}

/* ---------- financial snapshot ---------- */
/* Wire these to the user's real numbers. Amounts are in INR.
   monthlySurplus is derived (takeHome - fixedCommitments) unless overridden. */
const SNAPSHOT = {
  monthlyTakeHome: 250000,
  fixedCommitments: 145000,
  totalAssets: 12000000,
  totalLiabilities: 3800000,
  lifeCover: 10000000,
};

function formatINR(n) {
  if (n >= 10000000) {
    const v = n / 10000000;
    return `\u20B9${v % 1 === 0 ? v : v.toFixed(1)} Cr`;
  }
  if (n >= 100000) {
    const v = n / 100000;
    return `\u20B9${v % 1 === 0 ? v : v.toFixed(1)} L`;
  }
  return `\u20B9${n.toLocaleString("en-IN")}`;
}

function FinancialSnapshot({ data }) {
  const surplus = data.monthlyTakeHome - data.fixedCommitments;
  const commitPct = Math.round(
    (data.fixedCommitments / data.monthlyTakeHome) * 100
  );
  const netWorth = data.totalAssets - data.totalLiabilities;

  const cards = [
    {
      label: "Monthly take-home",
      value: formatINR(data.monthlyTakeHome),
      note: "What lands in your account",
      accent: "#93c5fd",
      bg: "#f9fcff",
    },
    {
      label: "Fixed commitments",
      value: formatINR(data.fixedCommitments),
      note: `${commitPct}% of your income`,
      accent: "#fecdd3",
      bg: "#fffcfd",
    },
    {
      label: "Monthly surplus",
      value: formatINR(surplus),
      note: "Left over each month",
      accent: "#86efac",
      bg: "#f9fdfa",
    },
    {
      label: "What you own",
      value: formatINR(data.totalAssets),
      note: "Total assets",
      accent: "#86efac",
      bg: "#f9fdfa",
    },
    {
      label: "What you owe",
      value: formatINR(data.totalLiabilities),
      note: "Total liabilities",
      accent: "#fecdd3",
      bg: "#fffcfd",
    },
    {
      label: "Life cover",
      value: formatINR(data.lifeCover),
      note: "Current protection",
      accent: "#5eead4",
      bg: "#f9fdfd",
    },
  ];

  return (
    <section style={{ marginTop: 44 }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 8,
          marginBottom: 20,
        }}
      >
        <div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              color: T.label,
              marginBottom: 6,
            }}
          >
            Financial snapshot
          </div>
          <p
            style={{
              fontFamily: T.sans,
              fontSize: 15,
              color: T.slateMute,
              margin: 0,
              maxWidth: 560,
            }}
          >
            Where you stand today, in six numbers.
          </p>
        </div>
        <div
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            color: T.ink,
          }}
        >
          Net worth&nbsp;
          <strong style={{ fontSize: 17 }}>{formatINR(netWorth)}</strong>
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        {cards.map((c) => (
          <div
            key={c.label}
            style={{
              background: c.bg || T.softNeutral,
              border: `1px solid ${T.rule}`,
              borderLeft: c.accent
                ? `4px solid ${c.accent}`
                : `1px solid ${T.rule}`,
              borderRadius: 8,
              padding: "18px 20px 16px",
            }}
          >
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                color: T.label,
                marginBottom: 10,
              }}
            >
              {c.label}
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 26,
                fontWeight: 600,
                lineHeight: 1,
                letterSpacing: "-0.01em",
                color: T.ink,
                marginBottom: 8,
              }}
            >
              {c.value}
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 13,
                color: T.slateMute,
              }}
            >
              {c.note}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}



/* ---------- what success looks like ---------- */
/* Top 3 goals from the user's intake. futureValue = inflation-adjusted
   cost in the target year. status: "funded" | "partial" | "unfunded".
   RETIREMENT projects the corpus on the user's current investing pattern. */
const GOALS = [
  {
    name: "Aryan's higher education",
    year: 2035,
    todayCost: 4000000,
    futureValue: 8000000,
    status: "unfunded",
  },
  {
    name: "Priya's higher education",
    year: 2039,
    todayCost: 4000000,
    futureValue: 10900000,
    status: "unfunded",
  },
  {
    name: "Family home upgrade",
    year: 2032,
    todayCost: 6000000,
    futureValue: 8500000,
    status: "partial",
    fundedPct: 40,
  },
];

const RETIREMENT = {
  age: 60,
  year: 2046,
  monthlyInvesting: 45000,
  surplusInvestedPct: 43,
  projectedCorpus: 16700000,
};

const GOAL_STATUS = {
  funded: { edge: "#86efac", badgeColor: "#2f7d4f", label: "Funded" },
  partial: { edge: "#e0b04b", badgeColor: "#a67b1d", label: "Partially funded" },
  unfunded: { edge: "#fecdd3", badgeColor: "#b2434f", label: "Not funded" },
};

function SuccessOutlook({ goals, retirement }) {
  return (
    <section style={{ marginTop: 44 }}>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        What this plan builds toward
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 18px",
          paddingBottom: 12,
          borderBottom: "2px solid #2f7d4f",
        }}
      >
        What Success Looks Like
      </h2>

      {/* aspiration banner */}
      <div
        style={{
          background: "#edf4ef",
          borderLeft: "4px solid #2f7d4f",
          borderRadius: "0 8px 8px 0",
          padding: "18px 22px",
          marginBottom: 20,
        }}
      >
        <div
          style={{
            fontFamily: T.sans,
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: "#2f7d4f",
            marginBottom: 8,
          }}
        >
          Your aspiration — in numbers
        </div>
        <div
          style={{
            fontFamily: T.sans,
            fontSize: 16,
            color: T.ink,
          }}
        >
          You want <strong>{PSYCHOMETRICS.aspiration.answer}</strong>.
        </div>
      </div>
      <p
        style={{
          fontFamily: T.sans,
          fontSize: 14,
          fontStyle: "italic",
          color: T.slateMute,
          margin: "0 0 20px",
          maxWidth: 620,
        }}
      >
        Your top {goals.length} goals, what each will cost in its target year,
        and where the funding stands today.
      </p>

      {/* goal cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        {goals.map((g) => {
          const st = GOAL_STATUS[g.status] || GOAL_STATUS.unfunded;
          return (
            <div
              key={g.name}
              style={{
                background: "#ffffff",
                border: `1px solid ${T.rule}`,
                borderTop: `4px solid ${st.edge}`,
                borderRadius: 8,
                padding: "16px 18px",
              }}
            >
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 12,
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  color: T.slateMute,
                  marginBottom: 6,
                }}
              >
                {g.year}
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 15,
                  fontWeight: 600,
                  color: T.ink,
                  marginBottom: 10,
                }}
              >
                {g.name}
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 22,
                  fontWeight: 600,
                  letterSpacing: "-0.01em",
                  color: T.ink,
                }}
              >
                {formatINR(g.futureValue)}
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 12,
                  color: T.slateMute,
                  marginTop: 2,
                  marginBottom: 10,
                }}
              >
                Cost in {g.year} ({formatINR(g.todayCost)} today)
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 9.5,
                  fontWeight: 600,
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  color: st.badgeColor,
                }}
              >
                {st.label}
                {g.status === "partial" && g.fundedPct
                  ? ` \u00B7 ${g.fundedPct}%`
                  : ""}
              </div>
            </div>
          );
        })}
      </div>

      {/* retirement corpus on current path */}
      <div
        style={{
          marginTop: 16,
          background: T.softNeutral,
          border: `1px solid ${T.rule}`,
          borderRadius: 8,
          padding: "18px 20px",
          display: "flex",
          flexWrap: "wrap",
          alignItems: "baseline",
          justifyContent: "space-between",
          gap: 12,
        }}
      >
        <div style={{ minWidth: 240 }}>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: T.label,
              marginBottom: 6,
            }}
          >
            Retirement corpus on your current path
          </div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 13,
              color: T.slateMute,
            }}
          >
            Investing {formatINR(retirement.monthlyInvesting)}/month —{" "}
            {retirement.surplusInvestedPct}% of your monthly surplus.
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 26,
              fontWeight: 600,
              letterSpacing: "-0.01em",
              color: T.ink,
            }}
          >
            {formatINR(retirement.projectedCorpus)}
          </div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 12,
              color: T.slateMute,
            }}
          >
            at age {retirement.age} ({retirement.year})
          </div>
        </div>
      </div>
    </section>
  );
}

/* ---------- key concerns ---------- */
/* Concern logic will come from the psychometric-based rules engine.
   severity: "high" (red) | "mid" (yellow) | "low" (white) */
const CONCERNS = [
  {
    severity: "high",
    title: "Term cover gap",
    detail:
      "Current \u20B975L leaves family \u20B913L after loan settlement. Need \u20B92 Cr.",
  },
  {
    severity: "high",
    title: "No emergency fund",
    detail:
      "\u20B92.8L in savings has no designation. One event away from disruption.",
  },
  {
    severity: "mid",
    title: "Retirement on current path",
    detail: "Corpus of \u20B91.67 Cr at 60. Money runs out at age 69.",
  },
  {
    severity: "mid",
    title: "Education goals unfunded",
    detail: "Aryan and Priya have no dedicated investments yet.",
  },
];

const SEVERITY_STYLES = {
  high: {
    edge: "#cf5b6b",
    bg: "#fdf3f4",
    badgeColor: "#b2434f",
    badgeLabel: "Address this first",
  },
  mid: {
    edge: "#e0b04b",
    bg: "#fdf9ee",
    badgeColor: "#a67b1d",
    badgeLabel: "Needs attention",
  },
  low: {
    edge: "#d7dadf",
    bg: "#ffffff",
    badgeColor: "#6b7280",
    badgeLabel: "Keep an eye on",
  },
};

function KeyConcerns({ concerns }) {
  return (
    <section style={{ marginTop: 44 }}>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        What needs attention
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #b2434f",
        }}
      >
        Key Concerns
      </h2>
      <p
        style={{
          fontFamily: T.sans,
          fontSize: 14,
          fontStyle: "italic",
          color: T.slateMute,
          margin: "0 0 20px",
          maxWidth: 620,
        }}
      >
        {concerns.length} things in your picture that need to be addressed —
        in this order. Each section of the plan covers one of these in full.
      </p>

      <div style={{ display: "grid", gap: 12 }}>
        {concerns.map((c) => {
          const st = SEVERITY_STYLES[c.severity] || SEVERITY_STYLES.low;
          return (
            <div
              key={c.title}
              style={{
                background: st.bg,
                border: `1px solid ${T.rule}`,
                borderLeft: `4px solid ${st.edge}`,
                borderRadius: 8,
                padding: "14px 18px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: 10,
                  flexWrap: "wrap",
                  marginBottom: 4,
                }}
              >
                <span
                  style={{
                    fontFamily: T.sans,
                    fontSize: 15,
                    fontWeight: 600,
                    color: T.ink,
                  }}
                >
                  {c.title}
                </span>
                <span
                  style={{
                    fontFamily: T.sans,
                    fontSize: 9.5,
                    fontWeight: 600,
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                    color: st.badgeColor,
                  }}
                >
                  {st.badgeLabel}
                </span>
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 13.5,
                  color: T.slateMute,
                }}
              >
                {c.detail}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}


/* ---------- plan sections ---------- */
/* Section 1 of 7 — Emergency Fund. Narrative comes from the plan engine. */
const EMERGENCY_FUND = {
  sectionNo: 1,
  sectionTotal: 7,
  track: "Foundation",
  title: "Emergency Fund",
  narrative:
    "You have \u20B92.8 lakhs in a savings account with no designation. It is not an emergency fund \u2014 it is money that will get spent. Move it today, top it up for 4 months, and it is done. Then redirect the full surplus to your goals.",
  monthlyExpenses: 145000,
  targetMonths: 6,
  availableFD: 300000,
  availableDebtFund: 250000,
  monthlyContribution: 80000, // into liquid fund, after EPF & existing SIPs
  actions: [
    {
      title: "Move \u20B92.8L savings \u2192 liquid mutual fund today",
      note: "Same-day redemption. ~7% return vs ~3.5% savings account. Label: Emergency Fund.",
    },
    {
      title: "Top up \u20B945,000/month for 4 months",
      note: "Full surplus here first. Month 4: balance \u20B94.68L. Stop. Redirect all to goals from month 5.",
    },
  ],
};

function EmergencyFund({ data }) {
  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Section {data.sectionNo} of {data.sectionTotal} · {data.track}
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #c87e45",
        }}
      >
        {data.title}
      </h2>

      {/* narrative callout */}
      <div
        style={{
          background: T.panelBg,
          border: `1px solid ${T.rule}`,
          borderLeft: `4px solid ${T.panelEdge}`,
          borderRadius: 8,
          padding: "20px 24px",
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            fontStyle: "italic",
            lineHeight: 1.75,
            color: T.ink,
            margin: 0,
          }}
        >
          {data.narrative}
        </p>
      </div>

      <EmergencyFundLedger data={data} />
      <Actionables items={data.actions} />
    </section>
  );
}

function Actionables({ items, startFrom = 1 }) {
  return (
    <div style={{ marginTop: 28 }}>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 12,
        }}
      >
        Actionables
      </div>
      <div style={{ display: "grid", gap: 12 }}>
        {items.map((a, i) => (
          <div
            key={a.title}
            style={{
              background: "#fdf9ee",
              border: `1px solid ${T.rule}`,
              borderRadius: 8,
              padding: "14px 18px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 10,
                marginBottom: 4,
              }}
            >
              <span
                style={{
                  fontFamily: T.sans,
                  fontSize: 13,
                  fontWeight: 600,
                  color: T.label,
                }}
              >
                {startFrom + i}.
              </span>
              <span
                style={{
                  fontFamily: T.sans,
                  fontSize: 15,
                  fontWeight: 600,
                  color: T.ink,
                }}
              >
                {a.title}
              </span>
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 13,
                color: T.slateMute,
                paddingLeft: 24,
              }}
            >
              {a.note}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EmergencyFundLedger({ data }) {
  const target = data.monthlyExpenses * data.targetMonths;
  const available = data.availableFD + data.availableDebtFund;
  const gap = Math.max(target - available, 0);
  const monthsToFill =
    gap === 0 ? 0 : Math.ceil(gap / data.monthlyContribution);

  const rows = [
    {
      label: "Monthly expenses",
      note: "What your household runs on",
      value: formatINR(data.monthlyExpenses),
    },
    {
      label: `Target \u2014 liquid fund kitty`,
      note: `${data.targetMonths} months of expenses`,
      value: formatINR(target),
    },
    {
      label: "Available funds",
      note: `FD ${formatINR(data.availableFD)} + debt fund ${formatINR(
        data.availableDebtFund
      )}`,
      value: formatINR(available),
    },
    {
      label: "Monthly move to liquid fund",
      note: "From savings, after EPF and existing commitments",
      value: `${formatINR(data.monthlyContribution)}/mo`,
    },
  ];

  return (
    <div style={{ marginTop: 28 }}>
      <div style={{ borderTop: `1px solid ${T.rule}` }}>
        {rows.map((r) => (
          <div
            key={r.label}
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              gap: 16,
              padding: "16px 4px",
              borderBottom: `1px solid ${T.rule}`,
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 14,
                  fontWeight: 600,
                  color: T.ink,
                }}
              >
                {r.label}
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 12.5,
                  color: T.slateMute,
                  marginTop: 2,
                }}
              >
                {r.note}
              </div>
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 18,
                fontWeight: 600,
                letterSpacing: "-0.01em",
                color: T.ink,
                whiteSpace: "nowrap",
              }}
            >
              {r.value}
            </div>
          </div>
        ))}
      </div>

      {/* outcome row */}
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          gap: 16,
          padding: "16px 4px",
        }}
      >
        <div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 14,
              fontWeight: 600,
              color: "#2f7d4f",
            }}
          >
            Liquid bucket fully funded
          </div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 12.5,
              color: T.slateMute,
              marginTop: 2,
            }}
          >
            Gap of {formatINR(gap)} at {formatINR(data.monthlyContribution)}
            /month
          </div>
        </div>
        <div
          style={{
            fontFamily: T.sans,
            fontSize: 18,
            fontWeight: 600,
            color: "#2f7d4f",
            whiteSpace: "nowrap",
          }}
        >
          {monthsToFill === 0 ? "Already there" : `in ${monthsToFill} months`}
        </div>
      </div>
    </div>
  );
}


/* ---------- section 2: life insurance ---------- */
/* LIFE INSURANCE LOGIC (captured for the plan engine):
   Additional life insurance requirement =
       (+) Total liabilities (home loan + all other debt)
       (+) Present value of future family expenses
       (-) Assets (EXCLUDING the primary/self-occupied property)
       (-) Current life insurance cover (term + ULIP + endowment)
   A positive result is the additional pure term cover to buy.
   Health insurance is covered separately in the next section. */
const LIFE_INSURANCE = {
  sectionNo: 2,
  sectionTotal: 7,
  track: "Protection",
  title: "Life Insurance",
  narrative:
    "Your term cover is \u20B975 lakhs. Your home loan is \u20B962 lakhs. After the loan is settled, your family has \u20B913 lakhs to live on. That is not protection \u2014 that is the appearance of it. And your health cover disappears the day you change jobs.",
  liabilities: 6200000,
  pvFutureExpenses: 27000000,
  coverTerm: 7500000,
  coverULIP: 1000000,
  coverEndowment: 1500000,
  assetsExclPrimaryHome: 3000000,
  /* POLICY REVIEW RULES (captured for the plan engine):
     - ULIP: if it has completed the 5-year lock-in, it can be redeemed.
     - Endowment: if it has NOT yet completed half of its policy term,
       surrender it. Invest the surrender value plus all future premiums
       at better-yielding returns, and replace the lost sum assured with
       additional pure term cover. */
  actions: [
    {
      title: "Buy \u20B92 Cr additional pure term cover",
      note: "Closes the life insurance gap computed above. Pure term plan, cover until your income-earning years end.",
    },
    {
      title: "Redeem the policy that has completed 5 years",
      note: "Redirect the proceeds and future premiums into better-yielding investments.",
    },
  ],
};

function LifeInsurance({ data }) {
  const currentCover = data.coverTerm + data.coverULIP + data.coverEndowment;
  const requirement =
    data.liabilities +
    data.pvFutureExpenses -
    data.assetsExclPrimaryHome -
    currentCover;

  const rows = [
    {
      sign: "+",
      label: "Liabilities",
      note: "Home loan and all other outstanding debt",
      value: formatINR(data.liabilities),
    },
    {
      sign: "+",
      label: "Future family expenses",
      note: "Present value of what your family will need",
      value: formatINR(data.pvFutureExpenses),
    },
    {
      sign: "\u2212",
      label: "Current insurance cover",
      note: `Term ${formatINR(data.coverTerm)} + ULIP ${formatINR(
        data.coverULIP
      )} + endowment ${formatINR(data.coverEndowment)}`,
      value: formatINR(currentCover),
    },
    {
      sign: "\u2212",
      label: "Assets you own",
      note: "Excluding your primary home",
      value: formatINR(data.assetsExclPrimaryHome),
    },
  ];

  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Section {data.sectionNo} of {data.sectionTotal} · {data.track}
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #b2434f",
        }}
      >
        {data.title}
      </h2>

      {/* narrative callout */}
      <div
        style={{
          background: T.panelBg,
          border: `1px solid ${T.rule}`,
          borderLeft: `4px solid ${T.panelEdge}`,
          borderRadius: 8,
          padding: "20px 24px",
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            fontStyle: "italic",
            lineHeight: 1.75,
            color: T.ink,
            margin: 0,
          }}
        >
          {data.narrative}
        </p>
      </div>

      {/* requirement ledger */}
      <div style={{ marginTop: 28 }}>
        <div style={{ borderTop: `1px solid ${T.rule}` }}>
          {rows.map((r) => (
            <div
              key={r.label}
              style={{
                display: "flex",
                alignItems: "baseline",
                justifyContent: "space-between",
                gap: 16,
                padding: "16px 4px",
                borderBottom: `1px solid ${T.rule}`,
              }}
            >
              <div style={{ display: "flex", gap: 12 }}>
                <span
                  style={{
                    fontFamily: T.sans,
                    fontSize: 15,
                    fontWeight: 600,
                    color: r.sign === "+" ? "#2f7d4f" : "#b2434f",
                    width: 14,
                  }}
                >
                  {r.sign}
                </span>
                <div>
                  <div
                    style={{
                      fontFamily: T.sans,
                      fontSize: 14,
                      fontWeight: 600,
                      color: T.ink,
                    }}
                  >
                    {r.label}
                  </div>
                  <div
                    style={{
                      fontFamily: T.sans,
                      fontSize: 12.5,
                      color: T.slateMute,
                      marginTop: 2,
                    }}
                  >
                    {r.note}
                  </div>
                </div>
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 18,
                  fontWeight: 600,
                  letterSpacing: "-0.01em",
                  color: T.ink,
                  whiteSpace: "nowrap",
                }}
              >
                {r.value}
              </div>
            </div>
          ))}
        </div>

        {/* result row */}
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 16,
            padding: "16px 4px",
          }}
        >
          <div style={{ paddingLeft: 26 }}>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 14,
                fontWeight: 600,
                color: "#b2434f",
              }}
            >
              Additional life insurance requirement
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 12.5,
                color: T.slateMute,
                marginTop: 2,
              }}
            >
              Liabilities + future expenses − assets − current
              cover
            </div>
          </div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 20,
              fontWeight: 600,
              color: "#b2434f",
              whiteSpace: "nowrap",
            }}
          >
            {formatINR(Math.max(requirement, 0))}
          </div>
        </div>
      </div>

      <Actionables items={data.actions} startFrom={3} />
    </section>
  );
}


/* ---------- section 3: health insurance ---------- */
/* HEALTH INSURANCE LOGIC (captured for the plan engine):
   Trigger: user's ONLY health cover is employer-provided.
   -> Employer cover is not sufficient: it lapses the day the user
      leaves the company, leaving the user AND family uninsured.
   Recommendation (independent of employer cover):
   - If monthly income < \u20B92L: basic family floater of \u20B915L
     (plus \u20B950L top-up).
   - If monthly income > \u20B92L: basic family floater of \u20B925L. */
const HEALTH_INSURANCE = {
  sectionNo: 3,
  sectionTotal: 7,
  track: "Protection",
  title: "Health Insurance",
  employerCoverOnly: true,
  monthlyIncome: 250000, // keep in sync with SNAPSHOT.monthlyTakeHome
  incomeThreshold: 200000,
  actions: [
    {
      title: "Buy a \u20B925L family floater health policy",
      note: "In your own name, independent of your employer \u2014 it stays with you across jobs.",
    },
  ],
};

function HealthInsurance({ data }) {
  const highIncome = data.monthlyIncome >= data.incomeThreshold;
  const rec = highIncome
    ? { base: 2500000, topUp: null }
    : { base: 1500000, topUp: 5000000 };

  return (
    <section style={{ marginTop: 52 }}>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #b2434f",
        }}
      >
        {data.title}
      </h2>

      {/* narrative callout */}
      {data.employerCoverOnly && (
        <div
          style={{
            background: T.panelBg,
            border: `1px solid ${T.rule}`,
            borderLeft: `4px solid ${T.panelEdge}`,
            borderRadius: 8,
            padding: "20px 24px",
          }}
        >
          <p
            style={{
              fontFamily: T.sans,
              fontSize: 15,
              fontStyle: "italic",
              lineHeight: 1.75,
              color: T.ink,
              margin: 0,
            }}
          >
            Your only health cover today comes from your employer. It is not
            yours — the day you leave the company, you and your family
            are without health insurance. Cover that depends on your job is
            not cover you can count on.
          </p>
        </div>
      )}

      {/* recommendation rows */}
      <div style={{ marginTop: 28 }}>
        <div style={{ borderTop: `1px solid ${T.rule}` }}>
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              gap: 16,
              padding: "16px 4px",
              borderBottom: `1px solid ${T.rule}`,
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 14,
                  fontWeight: 600,
                  color: T.ink,
                }}
              >
                Basic family floater
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 12.5,
                  color: T.slateMute,
                  marginTop: 2,
                }}
              >
                Independent cover for the whole family, in your name
              </div>
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 18,
                fontWeight: 600,
                letterSpacing: "-0.01em",
                color: T.ink,
                whiteSpace: "nowrap",
              }}
            >
              {formatINR(rec.base)}
            </div>
          </div>

          {rec.topUp && (
            <div
              style={{
                display: "flex",
                alignItems: "baseline",
                justifyContent: "space-between",
                gap: 16,
                padding: "16px 4px",
                borderBottom: `1px solid ${T.rule}`,
              }}
            >
              <div>
                <div
                  style={{
                    fontFamily: T.sans,
                    fontSize: 14,
                    fontWeight: 600,
                    color: T.ink,
                  }}
                >
                  Top-up cover
                </div>
                <div
                  style={{
                    fontFamily: T.sans,
                    fontSize: 12.5,
                    color: T.slateMute,
                    marginTop: 2,
                  }}
                >
                  Kicks in above the base floater, at a fraction of the cost
                </div>
              </div>
              <div
                style={{
                  fontFamily: T.sans,
                  fontSize: 18,
                  fontWeight: 600,
                  letterSpacing: "-0.01em",
                  color: T.ink,
                  whiteSpace: "nowrap",
                }}
              >
                {formatINR(rec.topUp)}
              </div>
            </div>
          )}
        </div>
      </div>

      <Actionables items={data.actions} startFrom={5} />
    </section>
  );
}


/* ---------- section 3: cashflow ---------- */
/* CASHFLOW LOGIC (captured for the plan engine):
   surplus = monthly income - monthly expenses.
   - If surplus > 0: show the surplus narrative (amount/month after
     fixed costs, and how the plan phases direct it).
   - If surplus < 0 (income < expenses): the user is running a DEFICIT
     budget -> show the remark: "You are running a deficit budget -
     either your income or your expenses need a re-look." */
const CASH_FLOW = {
  sectionNo: 3,
  sectionTotal: 7,
  track: "Cashflow",
  title: "Cashflow",
  monthlyIncome: 250000,
  monthlyExpenses: 150800,
  surplusNarrativeTail:
    "Phase 1 directs all of it to the emergency fund for 4 months. From month 5, every rupee is directed intentionally \u2014 before a single rupee is spent.",
  /* projection inputs */
  currentAge: 41,
  retirementAge: 60,
  horizonAge: 100,
  inflationRate: 0.06,
  lifeEvents: [
    { age: 47, amount: 2500000, label: "Home upgrade" },
    { age: 50, amount: 8000000, label: "Aryan's education" },
    { age: 54, amount: 10900000, label: "Priya's education" },
    { age: 65, amount: 1200000, label: "Health event" },
    { age: 70, amount: 1800000, label: "Health event" },
  ],
  /* SIP LOGIC (captured for the plan engine):
     Once the emergency bucket is filled (month 4 in this case), from
     month 5 onwards start an SIP of the balance surplus =
     monthly surplus - investments already committed (EPF, running SIPs). */
  actions: [
    {
      title: "From month 5, start an SIP of \u20B954,200/month",
      note: "The emergency bucket is filled by month 4. This is the balance of your surplus after the investments you are already committed to.",
    },
  ],
};

function CashFlow({ data }) {
  const surplus = data.monthlyIncome - data.monthlyExpenses;
  const isDeficit = surplus < 0;

  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Section {data.sectionNo} of {data.sectionTotal} · {data.track}
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: `2px solid ${T.ocean}`,
        }}
      >
        {data.title}
      </h2>

      {/* narrative callout */}
      <div
        style={{
          background: T.panelBg,
          border: `1px solid ${T.rule}`,
          borderLeft: `4px solid ${T.panelEdge}`,
          borderRadius: 8,
          padding: "20px 24px",
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            fontStyle: "italic",
            lineHeight: 1.75,
            color: T.ink,
            margin: 0,
          }}
        >
          {isDeficit
            ? `You are spending ${formatINR(
                Math.abs(surplus)
              )}/month more than you earn. You are running a deficit budget \u2014 either your income or your expenses need a re-look.`
            : `Your surplus is ${formatINR(
                surplus
              )}/month after fixed costs. ${data.surplusNarrativeTail}`}
        </p>
      </div>

      <CashflowProjection data={data} />
      <Actionables items={data.actions} startFrom={6} />

      {/* closing principle */}
      <div
        style={{
          marginTop: 20,
          background: T.panelBg,
          border: `1px solid ${T.rule}`,
          borderLeft: `4px solid ${T.panelEdge}`,
          borderRadius: 8,
          padding: "16px 20px",
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            fontStyle: "italic",
            fontWeight: 500,
            color: T.ink,
            margin: 0,
          }}
        >
          Invest first. Spend what remains. Set once — automatic forever.
        </p>
      </div>
    </section>
  );
}


/* Cashflow projection chart: blue = active income (stops at retirement),
   rose = regular expenses (never stop), yellow = life events stacked on
   expenses. Colors match the Overview snapshot cards. */
function CashflowProjection({ data }) {
  const [withInflation, setWithInflation] = useState(true);
  const [viewUntil, setViewUntil] = useState(75);

  const annualIncome = data.monthlyIncome * 12;
  const annualExpenses = data.monthlyExpenses * 12;

  const series = [];
  for (let age = data.currentAge; age <= viewUntil; age++) {
    const yearsOut = age - data.currentAge;
    const infl = withInflation
      ? Math.pow(1 + data.inflationRate, yearsOut)
      : 1;
    const event = data.lifeEvents.find((e) => e.age === age);
    series.push({
      age,
      income: age < data.retirementAge ? annualIncome : 0,
      expenses: Math.round(annualExpenses * infl),
      lifeEvent: event ? event.amount : 0,
      eventLabel: event ? event.label : null,
    });
  }

  const legend = [
    { color: "#6d9dc5", text: "Active income — stops at retirement" },
    { color: "#cd8162", text: "Regular expenses — never stop" },
    { color: "#c9a227", text: "Life events — stacked on expenses" },
  ];

  return (
    <div style={{ marginTop: 36 }}>
      {/* header row */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
          marginBottom: 16,
        }}
      >
        <div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              color: T.label,
              marginBottom: 4,
            }}
          >
            Cashflow projection
          </div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 13.5,
              fontStyle: "italic",
              color: T.slateMute,
            }}
          >
            The opportunity window — income exceeds expenses today. Not
            forever.
          </div>
        </div>
        <button
          onClick={() => setWithInflation(!withInflation)}
          style={{
            fontFamily: T.sans,
            fontSize: 10.5,
            fontWeight: 600,
            letterSpacing: "0.1em",
            textTransform: "uppercase",
            color: T.label,
            background: "transparent",
            border: `1px solid ${T.label}`,
            borderRadius: 4,
            padding: "7px 12px",
            cursor: "pointer",
          }}
        >
          {withInflation ? "With inflation" : "Without inflation"}
        </button>
      </div>

      {/* chart */}
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <BarChart data={series} barGap={1} barCategoryGap="20%">
            <XAxis
              dataKey="age"
              tick={{ fontFamily: "sans-serif", fontSize: 11, fill: "#6b7280" }}
              tickLine={false}
              axisLine={{ stroke: "#e5e7ea" }}
              interval={4}
            />
            <YAxis
              tickFormatter={(v) => formatINR(v)}
              tick={{ fontFamily: "sans-serif", fontSize: 11, fill: "#6b7280" }}
              tickLine={false}
              axisLine={false}
              width={54}
            />
            <Tooltip
              formatter={(value, name) => {
                const labels = {
                  income: "Active income",
                  expenses: "Regular expenses",
                  lifeEvent: "Life event",
                };
                return [formatINR(value), labels[name] || name];
              }}
              labelFormatter={(age) => `Age ${age}`}
              contentStyle={{
                fontFamily: "sans-serif",
                fontSize: 12,
                border: `1px solid ${T.rule}`,
                borderRadius: 6,
              }}
            />
            <ReferenceLine
              x={data.retirementAge}
              stroke="#b8863f"
              strokeDasharray="4 4"
              label={{
                value: "retirement",
                position: "insideTopRight",
                fontFamily: "sans-serif",
                fontSize: 10,
                fill: "#b8863f",
              }}
            />
            <Bar dataKey="income" fill="#6d9dc5" />
            <Bar dataKey="expenses" stackId="out" fill="#cd8162" />
            <Bar dataKey="lifeEvent" stackId="out" fill="#c9a227" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* horizon slider */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
          marginTop: 10,
          padding: "0 4px",
        }}
      >
        <span
          style={{
            fontFamily: T.sans,
            fontSize: 12,
            color: T.slateMute,
            whiteSpace: "nowrap",
          }}
        >
          View until age
        </span>
        <style>{`
          .yl-slider {
            -webkit-appearance: none;
            appearance: none;
            flex: 1;
            height: 3px;
            border-radius: 2px;
            background: ${T.rule};
            outline: none;
            cursor: pointer;
          }
          .yl-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: ${T.ink};
            border: none;
          }
          .yl-slider::-moz-range-thumb {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: ${T.ink};
            border: none;
          }
          .yl-slider::-moz-range-track {
            height: 3px;
            border-radius: 2px;
            background: ${T.rule};
          }
        `}</style>
        <input
          type="range"
          className="yl-slider"
          min={data.retirementAge}
          max={data.horizonAge}
          value={viewUntil}
          onChange={(e) => setViewUntil(Number(e.target.value))}
        />
        <span
          style={{
            fontFamily: T.sans,
            fontSize: 13,
            fontWeight: 600,
            color: T.ink,
            width: 30,
            textAlign: "right",
          }}
        >
          {viewUntil}
        </span>
      </div>

      {/* legend */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px 24px",
          marginTop: 14,
        }}
      >
        {legend.map((l) => (
          <div
            key={l.text}
            style={{ display: "flex", alignItems: "center", gap: 8 }}
          >
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: 3,
                background: l.color,
                display: "inline-block",
              }}
            />
            <span
              style={{
                fontFamily: T.sans,
                fontSize: 12.5,
                color: T.slateMute,
              }}
            >
              {l.text}
            </span>
          </div>
        ))}
      </div>

      {/* takeaway callout */}
      <div
        style={{
          marginTop: 20,
          background: "#f2f6fa",
          borderLeft: `4px solid ${T.ocean}`,
          borderRadius: "0 8px 8px 0",
          padding: "16px 20px",
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 14,
            fontStyle: "italic",
            lineHeight: 1.7,
            color: T.ink,
            margin: 0,
          }}
        >
          The gap between the income and expense bars during your earning
          years is the most valuable thing in your financial life right now.
          It won't always be there. This plan directs every rupee of it
          intentionally.
        </p>
      </div>
    </div>
  );
}


/* ---------- section 4: debt & liabilities ---------- */
/* DEBT LOGIC (captured for the plan engine):
   For EACH loan:
   1. EMI burden = monthly EMI / monthly take-home.
      Healthy ceiling = 30% (all EMIs combined). Above 30% -> concern.
   2. Effective borrowing rate:
      - taxDeductible loans (home loan u/s 24(b)): rate x (1 - tax bracket)
      - non-deductible loans (car, personal): rate as-is.
   3. Verdict: compare effective borrowing rate vs investment return
      assumption:
      - borrowing rate <  investment rate -> DO NOT PREPAY.
      - borrowing rate >= investment rate -> TRY REPAYING IT EARLY. */
const DEBT = {
  sectionNo: 4,
  sectionTotal: 7,
  track: "Debt",
  monthlyTakeHome: 250000, // keep in sync with SNAPSHOT.monthlyTakeHome
  taxBracketPct: 30,
  equityReturnPct: 11,
  emiCeilingPct: 30,
  loans: [
    {
      title: "Home Loan",
      outstanding: 6200000,
      monthlyEMI: 58800,
      ratePct: 8.5,
      rateTag: "floating",
      taxDeductible: true,
      narrative: true,
    },
    {
      title: "Car Loan",
      outstanding: 650000,
      monthlyEMI: 14500,
      ratePct: 11.5,
      rateTag: "fixed",
      taxDeductible: false,
      narrative: false,
    },
  ],
};

function formatINRFull(n) {
  return `\u20B9${n.toLocaleString("en-IN")}`;
}

function LoanBlock({ loan, ctx, first }) {
  const emiPct = Math.round((loan.monthlyEMI / ctx.monthlyTakeHome) * 100);
  const withinCeiling = emiPct <= ctx.emiCeilingPct;
  const effectiveRate = loan.taxDeductible
    ? loan.ratePct * (1 - ctx.taxBracketPct / 100)
    : loan.ratePct;
  const effectiveRounded = Math.round(effectiveRate * 10) / 10;
  const doNotPrepay = effectiveRate < ctx.equityReturnPct;

  const rows = [
    {
      label: `${loan.title} outstanding`,
      value: formatINRFull(loan.outstanding),
      tag: "approx.",
    },
    {
      label: "Monthly EMI",
      value: formatINRFull(loan.monthlyEMI),
      tag: "approx.",
    },
    {
      label: "EMI as % of take-home",
      value: `~${emiPct}%`,
      tag: withinCeiling
        ? `within ${ctx.emiCeilingPct}% ceiling`
        : `above ${ctx.emiCeilingPct}% ceiling`,
    },
    {
      label: `${loan.title} rate`,
      value: `${loan.ratePct}% p.a.`,
      tag: loan.rateTag,
    },
    {
      label: "Investment return assumption",
      value: `${ctx.equityReturnPct}% p.a.`,
      tag: "opportunity cost",
    },
  ];

  return (
    <div style={{ marginTop: first ? 0 : 44 }}>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: `2px solid ${T.ocean}`,
        }}
      >
        {loan.title}
      </h2>

      {loan.narrative && (
        <div
          style={{
            background: T.panelBg,
            border: `1px solid ${T.rule}`,
            borderLeft: `4px solid ${T.panelEdge}`,
            borderRadius: 8,
            padding: "20px 24px",
            marginBottom: 28,
          }}
        >
          <p
            style={{
              fontFamily: T.sans,
              fontSize: 15,
              fontStyle: "italic",
              lineHeight: 1.75,
              color: T.ink,
              margin: 0,
            }}
          >
            Your home loan EMI is {emiPct}% of take-home —{" "}
            {withinCeiling ? "within" : "above"} the healthy ceiling. At your
            effective post-tax loan rate of {effectiveRounded}%,{" "}
            {doNotPrepay
              ? `prepayment is a poor trade against the ${ctx.equityReturnPct}% return on the same money.`
              : `prepayment beats the ${ctx.equityReturnPct}% return \u2014 pay it down.`}
          </p>
        </div>
      )}

      <div style={{ borderTop: `1px solid ${T.rule}` }}>
        {rows.map((r) => (
          <div
            key={r.label}
            style={{
              display: "flex",
              alignItems: "baseline",
              justifyContent: "space-between",
              gap: 16,
              padding: "15px 4px",
              borderBottom: `1px solid ${T.rule}`,
            }}
          >
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 14,
                fontWeight: 500,
                color: T.ink,
              }}
            >
              {r.label}
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 12,
                whiteSpace: "nowrap",
              }}
            >
              <span
                style={{
                  fontFamily: T.sans,
                  fontSize: 15,
                  fontWeight: 600,
                  color: T.ink,
                }}
              >
                {r.value}
              </span>
              <span
                style={{
                  fontFamily: T.sans,
                  fontSize: 12,
                  fontStyle: "italic",
                  color: T.slateMute,
                }}
              >
                {r.tag}
              </span>
            </div>
          </div>
        ))}

        {/* verdict row */}
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 16,
            padding: "15px 4px",
            borderBottom: `1px solid ${T.rule}`,
            background: "#fdf9ee",
          }}
        >
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 14,
              fontWeight: 500,
              color: T.ink,
              paddingLeft: 4,
            }}
          >
            Verdict
          </div>
          <div style={{ textAlign: "right", paddingRight: 4 }}>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 15,
                fontWeight: 600,
                color: T.ocean,
              }}
            >
              {doNotPrepay ? "Do not prepay" : "Try repaying it early"}
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 12,
                fontStyle: "italic",
                color: T.slateMute,
                marginTop: 2,
              }}
            >
              {doNotPrepay
                ? "You are borrowing at a lower rate than your investments earn — let the money grow instead"
                : "You are borrowing at a higher rate than your investments earn — clearing it early saves more"}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DebtSection({ data }) {
  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Section {data.sectionNo} of {data.sectionTotal} · {data.track}
      </div>
      {data.loans.map((loan, i) => (
        <LoanBlock key={loan.title} loan={loan} ctx={data} first={i === 0} />
      ))}
    </section>
  );
}


/* ---------- section 5: tax ---------- */
/* TAX LOGIC FY 2025-26 (captured for the plan engine; mirrors the
   reference calculator workbook):
   INCOME = salary/bonus/business + other income + debt-MF gains
            (all taxed at slab rate). LTCG equity taxed at 12.5%
            above Rs 1.25L exemption; STCG equity at 20% flat.
   OLD REGIME:
   - Exemptions: standard deduction 50,000 + HRA u/s 10(13A)
     (HRA exemption = min of: HRA received; 50% metro / 40% non-metro
     of Basic+DA; rent paid - 10% of Basic+DA).
   - Deductions (each capped): 80C 1,50,000; 80CCD-1B NPS 50,000;
     80D self 25,000 (50,000 if 60+); 80D parents 25,000 (50,000 if
     60+); 80E education-loan interest (no limit); 80TTA 10,000;
     Sec 24(b) home-loan interest 2,00,000.
   - Slabs: 0-2.5L nil; 2.5-5L 5%; 5-10L 20%; >10L 30%.
   - Rebate 87A: slab tax = 0 if taxable income <= 5,00,000.
   NEW REGIME:
   - Standard deduction 75,000. No other deductions.
   - Slabs: 0-4L nil; 4-8L 5%; 8-12L 10%; 12-16L 15%; 16-20L 20%;
     20-24L 25%; >24L 30%.
   - Rebate 87A: slab tax = 0 if taxable income <= 12,00,000.
   BOTH: surcharge 10% (>50L), 15% (>1Cr), 25% (>2Cr), 37% (>5Cr,
   old regime only; new regime caps at 25%); Health & Edu cess 4%.
   VERDICT: recommend the regime with the LOWER total liability.
   Note: basic comparison only, not an actual tax computation. */

const OLD_SLABS = [
  { upto: 250000, rate: 0 },
  { upto: 500000, rate: 0.05 },
  { upto: 1000000, rate: 0.2 },
  { upto: Infinity, rate: 0.3 },
];
const NEW_SLABS = [
  { upto: 400000, rate: 0 },
  { upto: 800000, rate: 0.05 },
  { upto: 1200000, rate: 0.1 },
  { upto: 1600000, rate: 0.15 },
  { upto: 2000000, rate: 0.2 },
  { upto: 2400000, rate: 0.25 },
  { upto: Infinity, rate: 0.3 },
];

function slabTax(income, slabs) {
  let tax = 0;
  let prev = 0;
  for (const s of slabs) {
    if (income > prev) {
      tax += (Math.min(income, s.upto) - prev) * s.rate;
      prev = s.upto;
    } else break;
  }
  return tax;
}

function surchargeRate(taxable, isOld) {
  if (taxable > 50000000) return isOld ? 0.37 : 0.25;
  if (taxable > 20000000) return 0.25;
  if (taxable > 10000000) return 0.15;
  if (taxable > 5000000) return 0.1;
  return 0;
}

function hraExemption(inp) {
  if (inp.hraRentPaid <= 0) return 0;
  const rule1 = inp.hraReceived;
  const rule2 = inp.hraBasicDA * (inp.hraMetro ? 0.5 : 0.4);
  const rule3 = inp.hraRentPaid - 0.1 * inp.hraBasicDA;
  return Math.max(Math.min(rule1, rule2, rule3), 0);
}

function computeRegimes(inp) {
  const slabIncome = inp.salary + inp.otherIncome + inp.debtMFGains;
  const ltcgTax = Math.max(inp.ltcgEquity - 125000, 0) * 0.125;
  const stcgTax = inp.stcgEquity * 0.2;

  // OLD
  const deductions =
    Math.min(inp.ded80C, 150000) +
    Math.min(inp.dedNPS, 50000) +
    Math.min(inp.ded80DSelf, 25000) +
    Math.min(inp.ded80DParents, 50000) +
    Math.min(inp.homeLoanInterest, 200000) +
    hraExemption(inp);
  const oldTaxable = Math.max(slabIncome - 50000 - deductions, 0);
  let oldSlab = oldTaxable <= 500000 ? 0 : slabTax(oldTaxable, OLD_SLABS);
  let oldTax = oldSlab + ltcgTax + stcgTax;
  oldTax += oldTax * surchargeRate(oldTaxable, true);
  oldTax *= 1.04;

  // NEW
  const newTaxable = Math.max(slabIncome - 75000, 0);
  let newSlab = newTaxable <= 1200000 ? 0 : slabTax(newTaxable, NEW_SLABS);
  let newTax = newSlab + ltcgTax + stcgTax;
  newTax += newTax * surchargeRate(newTaxable, false);
  newTax *= 1.04;

  return {
    oldTaxable,
    newTaxable,
    oldTax: Math.round(oldTax),
    newTax: Math.round(newTax),
  };
}

const TAX_DEFAULTS = {
  salary: 3000000,
  otherIncome: 0,
  debtMFGains: 0,
  ltcgEquity: 0,
  stcgEquity: 0,
  hraMetro: true,
  hraBasicDA: 0,
  hraReceived: 0,
  hraRentPaid: 0,
  ded80C: 150000,
  dedNPS: 50000,
  ded80DSelf: 25000,
  ded80DParents: 0,
  homeLoanInterest: 200000,
};

function TaxInputRow({ label, note, value, onChange }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 16,
        padding: "12px 4px",
        borderBottom: `1px solid ${T.rule}`,
      }}
    >
      <div>
        <div
          style={{
            fontFamily: T.sans,
            fontSize: 14,
            fontWeight: 500,
            color: T.ink,
          }}
        >
          {label}
        </div>
        {note && (
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 12,
              color: T.slateMute,
              marginTop: 2,
            }}
          >
            {note}
          </div>
        )}
      </div>
      <input
        type="number"
        value={value}
        min={0}
        onChange={(e) => onChange(Math.max(Number(e.target.value) || 0, 0))}
        style={{
          fontFamily: T.sans,
          fontSize: 14,
          fontWeight: 600,
          color: T.ink,
          textAlign: "right",
          width: 140,
          padding: "8px 10px",
          background: "#f6f7f8",
          border: `1px solid ${T.rule}`,
          borderRadius: 6,
          outline: "none",
        }}
      />
    </div>
  );
}

function TaxSection() {
  const [inp, setInp] = useState(TAX_DEFAULTS);
  const set = (key) => (v) => setInp((s) => ({ ...s, [key]: v }));
  const r = computeRegimes(inp);
  const newWins = r.newTax <= r.oldTax;
  const savings = Math.abs(r.oldTax - r.newTax);

  const groupLabel = (text) => (
    <div
      style={{
        fontFamily: T.sans,
        fontSize: 11,
        fontWeight: 600,
        letterSpacing: "0.14em",
        textTransform: "uppercase",
        color: T.label,
        margin: "28px 0 4px",
      }}
    >
      {text}
    </div>
  );

  const regimeCard = (name, tax, taxable, winner) => (
    <div
      style={{
        flex: 1,
        minWidth: 220,
        background: winner ? "#f2f8f4" : "#ffffff",
        border: `1px solid ${winner ? "#86efac" : T.rule}`,
        borderTop: `4px solid ${winner ? "#2f7d4f" : T.rule}`,
        borderRadius: 8,
        padding: "18px 20px",
      }}
    >
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          color: winner ? "#2f7d4f" : T.slateMute,
          marginBottom: 8,
        }}
      >
        {name}
      </div>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 26,
          fontWeight: 600,
          letterSpacing: "-0.01em",
          color: T.ink,
        }}
      >
        {formatINRFull(tax)}
      </div>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 12,
          color: T.slateMute,
          marginTop: 4,
        }}
      >
        on taxable income of {formatINR(taxable)}
      </div>
    </div>
  );

  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Section 5 of 7 · Tax
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #b8863f",
        }}
      >
        Tax — Old vs New Regime
      </h2>

      {/* narrative / verdict callout */}
      <div
        style={{
          background: T.panelBg,
          border: `1px solid ${T.rule}`,
          borderLeft: `4px solid ${T.panelEdge}`,
          borderRadius: 8,
          padding: "20px 24px",
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            fontStyle: "italic",
            lineHeight: 1.75,
            color: T.ink,
            margin: 0,
          }}
        >
          On your numbers, the{" "}
          <strong>{newWins ? "New" : "Old"} Tax Regime</strong> works out
          better — it saves you {formatINRFull(savings)} a year over the{" "}
          {newWins ? "Old" : "New"} Regime. Adjust the figures below and the
          comparison updates live.
        </p>
      </div>

      {/* inputs */}
      {groupLabel("Your income (annual)")}
      <div style={{ borderTop: `1px solid ${T.rule}` }}>
        <TaxInputRow
          label="Salary, bonus & business income"
          value={inp.salary}
          onChange={set("salary")}
        />
        <TaxInputRow
          label="Other income"
          note="Rental, interest and other sources"
          value={inp.otherIncome}
          onChange={set("otherIncome")}
        />
        <TaxInputRow
          label="Debt mutual fund gains"
          note="Taxed at your slab rate"
          value={inp.debtMFGains}
          onChange={set("debtMFGains")}
        />
        <TaxInputRow
          label="LTCG on equities"
          note="12.5% above the 1.25L exemption"
          value={inp.ltcgEquity}
          onChange={set("ltcgEquity")}
        />
        <TaxInputRow
          label="STCG on equities"
          note="Taxed at 20%"
          value={inp.stcgEquity}
          onChange={set("stcgEquity")}
        />
      </div>

      {groupLabel("Deductions you claim (old regime only)")}
      <div style={{ borderTop: `1px solid ${T.rule}` }}>
        <TaxInputRow
          label="Section 80C"
          note="PF, PPF, ELSS, insurance, home-loan principal (cap 1,50,000)"
          value={inp.ded80C}
          onChange={set("ded80C")}
        />
        <TaxInputRow
          label="NPS — 80CCD(1B)"
          note="Cap 50,000"
          value={inp.dedNPS}
          onChange={set("dedNPS")}
        />
        <TaxInputRow
          label="Health insurance — 80D (self & family)"
          note="Cap 25,000 (50,000 if 60+)"
          value={inp.ded80DSelf}
          onChange={set("ded80DSelf")}
        />
        <TaxInputRow
          label="Health insurance — 80D (parents)"
          note="Cap 25,000 (50,000 if 60+)"
          value={inp.ded80DParents}
          onChange={set("ded80DParents")}
        />
        <TaxInputRow
          label="Home loan interest — Sec 24(b)"
          note="Cap 2,00,000"
          value={inp.homeLoanInterest}
          onChange={set("homeLoanInterest")}
        />
      </div>

      {groupLabel("HRA exemption (only if you live on rent)")}
      <div style={{ borderTop: `1px solid ${T.rule}` }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
            padding: "12px 4px",
            borderBottom: `1px solid ${T.rule}`,
          }}
        >
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 14,
              fontWeight: 500,
              color: T.ink,
            }}
          >
            City you live in
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {[
              { v: true, label: "Metro" },
              { v: false, label: "Non-metro" },
            ].map((o) => (
              <button
                key={o.label}
                onClick={() => setInp((st) => ({ ...st, hraMetro: o.v }))}
                style={{
                  fontFamily: T.sans,
                  fontSize: 12,
                  fontWeight: 600,
                  padding: "7px 14px",
                  borderRadius: 6,
                  cursor: "pointer",
                  border: `1px solid ${
                    inp.hraMetro === o.v ? T.ink : T.rule
                  }`,
                  background: inp.hraMetro === o.v ? T.ink : "#ffffff",
                  color: inp.hraMetro === o.v ? "#ffffff" : T.slateMute,
                }}
              >
                {o.label}
              </button>
            ))}
          </div>
        </div>
        <TaxInputRow
          label="Basic salary + DA (annual)"
          value={inp.hraBasicDA}
          onChange={set("hraBasicDA")}
        />
        <TaxInputRow
          label="HRA received (annual)"
          note="The HRA component in your salary"
          value={inp.hraReceived}
          onChange={set("hraReceived")}
        />
        <TaxInputRow
          label="Rent paid (annual)"
          note="Leave 0 if you don't pay rent"
          value={inp.hraRentPaid}
          onChange={set("hraRentPaid")}
        />
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 16,
            padding: "14px 4px",
          }}
        >
          <div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 14,
                fontWeight: 600,
                color: "#2f7d4f",
              }}
            >
              Your HRA exemption
            </div>
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 12,
                color: T.slateMute,
                marginTop: 2,
              }}
            >
              Least of: HRA received; {inp.hraMetro ? "50%" : "40%"} of Basic
              + DA; rent paid minus 10% of Basic + DA
            </div>
          </div>
          <div
            style={{
              fontFamily: T.sans,
              fontSize: 18,
              fontWeight: 600,
              color: "#2f7d4f",
              whiteSpace: "nowrap",
            }}
          >
            {formatINRFull(Math.round(hraExemption(inp)))}
          </div>
        </div>
      </div>

      {/* comparison */}
      {groupLabel("The comparison")}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          marginTop: 8,
        }}
      >
        {regimeCard("Old Regime", r.oldTax, r.oldTaxable, !newWins)}
        {regimeCard("New Regime", r.newTax, r.newTaxable, newWins)}
      </div>

      {/* disclaimer */}
      <p
        style={{
          fontFamily: T.sans,
          fontSize: 11.5,
          color: T.slateMute,
          marginTop: 16,
        }}
      >
        A basic comparison for choosing between regimes — not your
        actual tax liability. Please confirm with your tax advisor.
      </p>
    </section>
  );
}


/* ---------- section 6: key life events ---------- */
/* KEY LIFE EVENTS CHART (for the plan engine):
   - One stacked bar per calendar year; each stack segment is a life
     event category (education / home / vehicle / wedding / health).
   - X-axis shows family ages for that year (user + children) plus the
     calendar year.
   - An icon for each event floats above the bar; two events in the
     same year -> two icons stacked. */
const KLE = {
  sectionNo: 6,
  sectionTotal: 7,
  track: "Key Life Events",
  title: "Key Life Events",
  startYear: 2026,
  endYear: 2056,
  family: [
    { name: "You", ageInStartYear: 41 },
    { name: "Aryan", ageInStartYear: 12 },
    { name: "Priya", ageInStartYear: 8 },
  ],
  /* liquid assets available in the event year, from the NWGC
     (net-worth growth calculator), under each scenario */
  baseAnnualExpenses: 1809600, // current annual expenses
  expenseInflation: 0.06,
  events: [
    { year: 2032, category: "home", label: "Home upgrade", amount: 8500000, icon: "\uD83C\uDFE0", asIsLiquid: 6200000, recLiquid: 17000000 },
    { year: 2035, category: "education", label: "Aryan's education", amount: 8000000, icon: "\uD83C\uDF93", asIsLiquid: 7800000, recLiquid: 22000000 },
    { year: 2035, category: "vehicle", label: "Car upgrade", amount: 1200000, icon: "\uD83D\uDE97", asIsLiquid: 7800000, recLiquid: 22000000 },
    { year: 2039, category: "education", label: "Priya's education", amount: 10900000, icon: "\uD83C\uDF93", asIsLiquid: 9200000, recLiquid: 31000000 },
    { year: 2045, category: "wedding", label: "Aryan's wedding", amount: 4000000, icon: "\uD83D\uDC8D", asIsLiquid: 11000000, recLiquid: 42000000 },
    { year: 2048, category: "wedding", label: "Priya's wedding", amount: 4500000, icon: "\uD83D\uDC8D", asIsLiquid: 9500000, recLiquid: 51000000 },
    { year: 2050, category: "health", label: "Health corpus", amount: 1200000, icon: "\uD83C\uDFE5", asIsLiquid: 6000000, recLiquid: 56000000 },
  ],
  /* RETIREMENT — a MANDATORY life event. Not plotted on the events
     chart; always shown in the comparison below. NWGC supplies, per
     scenario: liquid assets at retirement age, and the age until
     which the money lasts (corpus drawn down against inflating
     expenses at post-retirement returns). Expenses at retirement =
     baseAnnualExpenses x (1+inflation)^(retYear - startYear).
     Healthy if money lasts at least to life expectancy. */
  retirement: {
    age: 60,
    year: 2046,
    lifeExpectancy: 85,
    asIs: { liquidAtRet: 16700000, lastsTillAge: 69 },
    rec: { liquidAtRet: 65000000, lastsTillAge: 92 },
  },
};

/* LIFE-EVENT FUNDING COMPARISON LOGIC (captured for the plan engine):
   Linked to the NWGC (net-worth growth calculator). For EACH life
   event, under TWO scenarios:
     Scenario A "As-Is"        = user's current saving/investing path.
     Scenario B "Recommended"  = path after the plan's recommended changes.
   For each scenario, the NWGC supplies the liquid assets available in
   the event year. Then:
     eventMet     = liquidAvailable >= event future cost.
     bufferCovered = (liquidAvailable - event cost) >=
                     3 x that year's annual expenses, where that year's
                     annual expenses = baseAnnualExpenses x
                     (1 + inflation)^(eventYear - startYear).
   Both checks shown side by side so the user sees what the
   recommendations change. */

const KLE_CATEGORIES = [
  { key: "education", color: "#7fb3d5", label: "Education" },
  { key: "home", color: "#f1948a", label: "Home" },
  { key: "vehicle", color: "#f7dc6f", label: "Vehicle" },
  { key: "wedding", color: "#c39bd3", label: "Wedding" },
  { key: "health", color: "#7dcea0", label: "Health" },
];

function KleAxisTick({ x, y, payload, data }) {
  const d = data.find((r) => r.year === payload.value);
  if (!d) return null;
  const show = payload.value % 2 === 0;
  if (!show) return null;
  const lines = [...d.ages, String(d.year)];
  return (
    <g>
      {lines.map((t, i) => (
        <text
          key={i}
          x={x}
          y={y + 12 + i * 13}
          textAnchor="middle"
          style={{
            fontFamily: "sans-serif",
            fontSize: 10,
            fill: i === lines.length - 1 ? "#2a2e38" : "#9aa0ab",
            fontWeight: i === lines.length - 1 ? 600 : 400,
          }}
        >
          {t}
        </text>
      ))}
    </g>
  );
}

function KleIconLabel(props) {
  const { x, y, width, index, data } = props;
  const icons = data[index] ? data[index].icons : [];
  if (!icons || icons.length === 0) return null;
  return (
    <g>
      {icons.map((ic, i) => (
        <text
          key={i}
          x={x + width / 2}
          y={y - 8 - i * 18}
          textAnchor="middle"
          style={{ fontSize: 14 }}
        >
          {ic}
        </text>
      ))}
    </g>
  );
}

function KeyLifeEvents({ data }) {
  const series = [];
  for (let year = data.startYear; year <= data.endYear; year++) {
    const row = {
      year,
      ages: data.family.map(
        (f) => f.ageInStartYear + (year - data.startYear)
      ),
      icons: [],
    };
    KLE_CATEGORIES.forEach((c) => (row[c.key] = 0));
    data.events
      .filter((e) => e.year === year)
      .forEach((e) => {
        row[e.category] += e.amount / 100000; // in lakhs
        row.icons.push(e.icon);
      });
    series.push(row);
  }

  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Section {data.sectionNo} of {data.sectionTotal} · {data.track}
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #b8863f",
        }}
      >
        {data.title}
      </h2>

      <div
        style={{
          fontFamily: T.sans,
          fontSize: 12,
          color: T.slateMute,
          marginBottom: 8,
        }}
      >
        In lakhs
      </div>

      <div style={{ width: "100%", height: 340, position: "relative" }}>
        {/* whose age is each axis row */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 278,
            width: 52,
            textAlign: "right",
            pointerEvents: "none",
          }}
        >
          {[...data.family.map((f) => f.name), "Year"].map((n, i) => (
            <div
              key={n}
              style={{
                fontFamily: T.sans,
                fontSize: 9.5,
                fontWeight: i === data.family.length ? 600 : 500,
                color: i === data.family.length ? T.ink : "#9aa0ab",
                lineHeight: "13px",
                textTransform: "uppercase",
                letterSpacing: "0.04em",
              }}
            >
              {n}
            </div>
          ))}
        </div>
        <ResponsiveContainer>
          <BarChart data={series} margin={{ top: 40, right: 8, left: 24 }}>
            <XAxis
              dataKey="year"
              interval={0}
              height={70}
              tickLine={false}
              axisLine={{ stroke: "#e5e7ea" }}
              tick={<KleAxisTick data={series} />}
            />
            <YAxis
              tick={{ fontFamily: "sans-serif", fontSize: 11, fill: "#6b7280" }}
              tickLine={false}
              axisLine={false}
              width={36}
            />
            <Tooltip
              formatter={(value, name) => {
                const cat = KLE_CATEGORIES.find((c) => c.key === name);
                return [
                  formatINR(Math.round(value * 100000)),
                  cat ? cat.label : name,
                ];
              }}
              labelFormatter={(year) => {
                const row = series.find((r) => r.year === year);
                const evts = data.events
                  .filter((e) => e.year === year)
                  .map((e) => e.label)
                  .join(" + ");
                return evts ? `${year} \u2014 ${evts}` : `${year}`;
              }}
              contentStyle={{
                fontFamily: "sans-serif",
                fontSize: 12,
                border: `1px solid ${T.rule}`,
                borderRadius: 6,
              }}
            />
            {KLE_CATEGORIES.map((c, i) => (
              <Bar key={c.key} dataKey={c.key} stackId="kle" fill={c.color}>
                {i === KLE_CATEGORIES.length - 1 && (
                  <LabelList content={<KleIconLabel data={series} />} />
                )}
              </Bar>
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* legend */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "10px 24px",
          marginTop: 10,
        }}
      >
        {KLE_CATEGORIES.map((c) => (
          <div
            key={c.key}
            style={{ display: "flex", alignItems: "center", gap: 8 }}
          >
            <span
              style={{
                width: 12,
                height: 12,
                borderRadius: 3,
                background: c.color,
                display: "inline-block",
              }}
            />
            <span
              style={{
                fontFamily: T.sans,
                fontSize: 12.5,
                color: T.slateMute,
              }}
            >
              {c.label}
            </span>
          </div>
        ))}
      </div>

      <LifeEventComparisons data={data} />
    </section>
  );
}

function ScenarioPanel({ title, liquid, cost, threeYrNeed, recommended }) {
  const met = liquid >= cost;
  const buffer = liquid - cost >= threeYrNeed;
  const badge = (ok, yes, no) => (
    <span
      style={{
        fontFamily: T.sans,
        fontSize: 10,
        fontWeight: 600,
        letterSpacing: "0.06em",
        textTransform: "uppercase",
        color: ok ? "#2f7d4f" : "#b2434f",
        background: ok ? "#eaf5ee" : "#fdf1f2",
        padding: "3px 8px",
        borderRadius: 4,
        whiteSpace: "nowrap",
      }}
    >
      {ok ? yes : no}
    </span>
  );
  return (
    <div
      style={{
        flex: 1,
        minWidth: 230,
        background: recommended ? "#f7fbf8" : "#fbfbfb",
        border: `1px solid ${recommended ? "#cfe8d8" : T.rule}`,
        borderRadius: 8,
        padding: "14px 16px",
      }}
    >
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 10.5,
          fontWeight: 600,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: recommended ? "#2f7d4f" : T.slateMute,
          marginBottom: 10,
        }}
      >
        {title}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
          marginBottom: 8,
        }}
      >
        <span
          style={{ fontFamily: T.sans, fontSize: 12.5, color: T.slateMute }}
        >
          Event funded
        </span>
        {badge(met, "Met", "Not met")}
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
          marginBottom: 8,
        }}
      >
        <span
          style={{ fontFamily: T.sans, fontSize: 12.5, color: T.slateMute }}
        >
          Liquid assets that year
        </span>
        <span
          style={{
            fontFamily: T.sans,
            fontSize: 13.5,
            fontWeight: 600,
            color: T.ink,
            whiteSpace: "nowrap",
          }}
        >
          {formatINR(liquid)}
        </span>
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
        }}
      >
        <span
          style={{ fontFamily: T.sans, fontSize: 12.5, color: T.slateMute }}
        >
          Next 3 yrs of expenses
        </span>
        {badge(buffer, "Covered", "Not covered")}
      </div>
    </div>
  );
}

function RetirementScenarioPanel({ title, liquid, expensesAtRet, lastsTill, lifeExpectancy, recommended }) {
  const ok = lastsTill >= lifeExpectancy;
  return (
    <div
      style={{
        flex: 1,
        minWidth: 230,
        background: recommended ? "#f7fbf8" : "#fbfbfb",
        border: `1px solid ${recommended ? "#cfe8d8" : T.rule}`,
        borderRadius: 8,
        padding: "14px 16px",
      }}
    >
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 10.5,
          fontWeight: 600,
          letterSpacing: "0.1em",
          textTransform: "uppercase",
          color: recommended ? "#2f7d4f" : T.slateMute,
          marginBottom: 10,
        }}
      >
        {title}
      </div>
      {[
        ["Liquid assets at retirement", formatINR(liquid)],
        ["Expenses at retirement", `${formatINR(expensesAtRet)}/yr`],
      ].map(([k, v]) => (
        <div
          key={k}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 10,
            marginBottom: 8,
          }}
        >
          <span
            style={{ fontFamily: T.sans, fontSize: 12.5, color: T.slateMute }}
          >
            {k}
          </span>
          <span
            style={{
              fontFamily: T.sans,
              fontSize: 13.5,
              fontWeight: 600,
              color: T.ink,
              whiteSpace: "nowrap",
            }}
          >
            {v}
          </span>
        </div>
      ))}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 10,
        }}
      >
        <span
          style={{ fontFamily: T.sans, fontSize: 12.5, color: T.slateMute }}
        >
          Money lasts till
        </span>
        <span
          style={{
            fontFamily: T.sans,
            fontSize: 10,
            fontWeight: 600,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            color: ok ? "#2f7d4f" : "#b2434f",
            background: ok ? "#eaf5ee" : "#fdf1f2",
            padding: "3px 8px",
            borderRadius: 4,
            whiteSpace: "nowrap",
          }}
        >
          Age {lastsTill}
        </span>
      </div>
    </div>
  );
}

function LifeEventComparisons({ data }) {
  return (
    <div style={{ marginTop: 40 }}>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Will each event be met?
      </div>
      <p
        style={{
          fontFamily: T.sans,
          fontSize: 14,
          fontStyle: "italic",
          color: T.slateMute,
          margin: "0 0 20px",
          maxWidth: 640,
        }}
      >
        For every event: the liquid assets available in that year, whether
        they fund the event, and whether they still cover the next 3 years of
        expenses — on your current path vs with our recommendations.
      </p>

      <div style={{ display: "grid", gap: 20 }}>
        {data.events.map((e) => {
          const yearsOut = e.year - data.startYear;
          const threeYrNeed =
            data.baseAnnualExpenses *
            Math.pow(1 + data.expenseInflation, yearsOut) *
            3;
          return (
            <div
              key={`${e.year}-${e.label}`}
              style={{
                border: `1px solid ${T.rule}`,
                borderRadius: 8,
                padding: "16px 18px",
                background: "#ffffff",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: 8,
                  marginBottom: 14,
                }}
              >
                <div
                  style={{
                    fontFamily: T.sans,
                    fontSize: 15,
                    fontWeight: 600,
                    color: T.ink,
                  }}
                >
                  {e.icon} {e.label}{" "}
                  <span
                    style={{
                      fontWeight: 500,
                      color: T.slateMute,
                      fontSize: 13,
                    }}
                  >
                    · {e.year}
                  </span>
                </div>
                <div
                  style={{
                    fontFamily: T.sans,
                    fontSize: 13,
                    color: T.slateMute,
                  }}
                >
                  Costs {formatINR(e.amount)} in {e.year}
                </div>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                <ScenarioPanel
                  title="As-is — current path"
                  liquid={e.asIsLiquid}
                  cost={e.amount}
                  threeYrNeed={threeYrNeed}
                  recommended={false}
                />
                <ScenarioPanel
                  title="With recommendations"
                  liquid={e.recLiquid}
                  cost={e.amount}
                  threeYrNeed={threeYrNeed}
                  recommended={true}
                />
              </div>
            </div>
          );
        })}

        {/* retirement — mandatory event */}
        {(() => {
          const r = data.retirement;
          const expensesAtRet = Math.round(
            data.baseAnnualExpenses *
              Math.pow(1 + data.expenseInflation, r.year - data.startYear)
          );
          return (
            <div
              style={{
                border: "1px solid #e6d9b8",
                borderLeft: "4px solid #b8863f",
                borderRadius: 8,
                padding: "16px 18px",
                background: "#fffdf5",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: 8,
                  marginBottom: 14,
                }}
              >
                <div
                  style={{
                    fontFamily: T.sans,
                    fontSize: 15,
                    fontWeight: 600,
                    color: T.ink,
                  }}
                >
                  {"\uD83C\uDFD6\uFE0F"} Retirement{" "}
                  <span
                    style={{
                      fontWeight: 500,
                      color: T.slateMute,
                      fontSize: 13,
                    }}
                  >
                    · age {r.age}, {r.year}
                  </span>
                </div>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                <RetirementScenarioPanel
                  title="As-is — current path"
                  liquid={r.asIs.liquidAtRet}
                  expensesAtRet={expensesAtRet}
                  lastsTill={r.asIs.lastsTillAge}
                  lifeExpectancy={r.lifeExpectancy}
                  recommended={false}
                />
                <RetirementScenarioPanel
                  title="With recommendations"
                  liquid={r.rec.liquidAtRet}
                  expensesAtRet={expensesAtRet}
                  lastsTill={r.rec.lastsTillAge}
                  lifeExpectancy={r.lifeExpectancy}
                  recommended={true}
                />
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}


/* ---------- section 7: summary ---------- */
/* ACTION SUMMARY: consolidates every actionable from all tabs, in
   plan order, with continuous numbering and the tab each came from. */
function SummarySection() {
  const groups = [
    { source: "Emergency Fund", items: EMERGENCY_FUND.actions },
    { source: "Life Insurance", items: LIFE_INSURANCE.actions },
    { source: "Health Insurance", items: HEALTH_INSURANCE.actions },
    { source: "Cash Flow", items: CASH_FLOW.actions },
  ];
  let n = 0;

  return (
    <section>
      <div
        style={{
          fontFamily: T.sans,
          fontSize: 11,
          fontWeight: 600,
          letterSpacing: "0.14em",
          textTransform: "uppercase",
          color: T.label,
          marginBottom: 6,
        }}
      >
        Everything in one place
      </div>
      <h2
        style={{
          fontFamily: T.sans,
          fontSize: 24,
          fontWeight: 600,
          color: T.ink,
          margin: "0 0 14px",
          paddingBottom: 12,
          borderBottom: "2px solid #b8863f",
        }}
      >
        Action Summary
      </h2>

      {/* narrative callout */}
      <div
        style={{
          background: T.panelBg,
          border: `1px solid ${T.rule}`,
          borderLeft: `4px solid ${T.panelEdge}`,
          borderRadius: 8,
          padding: "20px 24px",
          marginBottom: 28,
        }}
      >
        <p
          style={{
            fontFamily: T.sans,
            fontSize: 15,
            fontStyle: "italic",
            lineHeight: 1.75,
            color: T.ink,
            margin: 0,
          }}
        >
          This is everything your plan asks you to do. Nothing requires a
          promotion, a windfall, or a change in lifestyle. It requires
          direction — and you now have it.
        </p>
      </div>

      {/* consolidated actions */}
      <div style={{ display: "grid", gap: 12 }}>
        {groups.map((g) =>
          g.items.map((a) => {
            n += 1;
            return (
              <div
                key={a.title}
                style={{
                  background: "#fdf9ee",
                  border: `1px solid ${T.rule}`,
                  borderRadius: 8,
                  padding: "14px 18px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "baseline",
                    justifyContent: "space-between",
                    gap: 10,
                    flexWrap: "wrap",
                    marginBottom: 4,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "baseline",
                      gap: 10,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: T.sans,
                        fontSize: 13,
                        fontWeight: 600,
                        color: T.label,
                      }}
                    >
                      {n}.
                    </span>
                    <span
                      style={{
                        fontFamily: T.sans,
                        fontSize: 15,
                        fontWeight: 600,
                        color: T.ink,
                      }}
                    >
                      {a.title}
                    </span>
                  </div>
                  <span
                    style={{
                      fontFamily: T.sans,
                      fontSize: 10.5,
                      fontWeight: 600,
                      letterSpacing: "0.08em",
                      textTransform: "uppercase",
                      color: T.slateMute,
                    }}
                  >
                    {g.source}
                  </span>
                </div>
                <div
                  style={{
                    fontFamily: T.sans,
                    fontSize: 13,
                    color: T.slateMute,
                    paddingLeft: 24,
                  }}
                >
                  {a.note}
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

/* ---------- tab shell ---------- */
const TABS = [
  { name: "Overview", Icon: LayoutDashboard },
  { name: "Emergency Fund", Icon: Umbrella },
  { name: "Protection", Icon: Shield },
  { name: "Cash Flow", Icon: ArrowRightLeft },
  { name: "Debt", Icon: CreditCard },
  { name: "Tax", Icon: Receipt },
  { name: "Key Life Events", Icon: CalendarHeart },
  { name: "Summary", Icon: ListChecks },
];

export default function YeslyfPlan() {
  const [tab, setTab] = useState("Overview");
  const p = PSYCHOMETRICS;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: T.pageBg,
        color: T.ink,
        padding: "0 0 80px",
      }}
    >
      {/* masthead — brand bar */}
      <div style={{ height: 4, background: BRAND_YELLOW }} />
      <header
        style={{
          background: T.pageBg,
          borderBottom: `1px solid ${T.rule}`,
        }}
      >
        <div
          style={{
            maxWidth: 860,
            margin: "0 auto",
            padding: "18px 24px",
            display: "flex",
            alignItems: "center",
          }}
        >
          <YeslyfLogo size={28} />
        </div>
      </header>

      {/* tabs */}
      <nav
        style={{
          maxWidth: 860,
          margin: "28px auto 0",
          padding: "0 24px",
          display: "flex",
          gap: 4,
          borderBottom: `1px solid ${T.rule}`,
        }}
      >
        {TABS.map(({ name, Icon }) => {
          const active = name === tab;
          return (
            <button
              key={name}
              onClick={() => setTab(name)}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 7,
                fontFamily: T.sans,
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                padding: "10px 16px 12px",
                background: "transparent",
                border: "none",
                cursor: "pointer",
                color: active ? T.ink : "#9aa0ab",
                borderBottom: active
                  ? `3px solid ${T.panelEdge}`
                  : "3px solid transparent",
                marginBottom: -1,
              }}
            >
              <Icon size={14} strokeWidth={2.2} />
              {name}
            </button>
          );
        })}
      </nav>

      {/* content */}
      <main style={{ maxWidth: 860, margin: "36px auto 0", padding: "0 24px" }}>
        {tab === "Overview" ? (
          <>
            <PlanNarrative p={p} />
            <FinancialSnapshot data={SNAPSHOT} />
            <SuccessOutlook goals={GOALS} retirement={RETIREMENT} />
            <KeyConcerns concerns={CONCERNS} />
          </>
        ) : tab === "Emergency Fund" ? (
          <EmergencyFund data={EMERGENCY_FUND} />
        ) : tab === "Protection" ? (
          <>
            <LifeInsurance data={LIFE_INSURANCE} />
            <HealthInsurance data={HEALTH_INSURANCE} />
          </>
        ) : tab === "Cash Flow" ? (
          <CashFlow data={CASH_FLOW} />
        ) : tab === "Debt" ? (
          <DebtSection data={DEBT} />
        ) : tab === "Tax" ? (
          <TaxSection />
        ) : tab === "Key Life Events" ? (
          <KeyLifeEvents data={KLE} />
        ) : tab === "Summary" ? (
          <SummarySection />
        ) : (
          <div
            style={{
              border: `1px dashed ${T.rule}`,
              background: T.softNeutral,
              padding: "56px 24px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                fontFamily: T.sans,
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: "0.14em",
                textTransform: "uppercase",
                color: T.label,
                marginBottom: 10,
              }}
            >
              {tab}
            </div>
            <p
              style={{
                fontFamily: T.sans,
                fontSize: 16,
                color: T.slateMute,
                margin: 0,
              }}
            >
              This section is coming next. The Overview is where your plan
              begins.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
