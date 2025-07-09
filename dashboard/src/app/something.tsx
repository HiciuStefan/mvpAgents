import { Card, CardHeader, CardContent, CardTitle } from "~/components/ui/card";
import {
  Mail,
  Twitter,
  Globe,
  StickyNote,
  CheckCircle2 as Check,
  Clock3 as Snooze,
} from "lucide-react";

/**
 * Business Intelligence summary card – compact, dark-glass variant
 * Tweaked so text is always readable on light dashboards.
 */
export default function BusinessIntelligenceCard2({ className = "" }) {
  // --- Demo data (replace with live data) ---------------------------------
  const highUrgency = [
    { label: "Umbrella Corp – SLA overdue 36 h" },
    { label: "Initech – Prototype request (WhatsApp)" },
    { label: "Globex – RFP deadline tomorrow" },
  ];
  const counts = { high: 3, medium: 3, low: 4 };
  const channelCounts = { mail: 2, twitter: 2, web: 1, notes: 2 };
  const total = counts.high + counts.medium + counts.low;
  const widths = {
    high: (counts.high / total) * 100,
    medium: (counts.medium / total) * 100,
    low: (counts.low / total) * 100,
  };

  // -----------------------------------------------------------------------
  return (
    <Card
      className={
        `relative w-full max-w-lg overflow-hidden rounded-2xl bg-slate-900/90 p-0 shadow-xl ring-1 ring-white/15 backdrop-blur-md ${className}`
      }
    >
      {/* Subtle darker gradient accent */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-gradient-to-br from-indigo-800/30 via-purple-800/20 to-emerald-700/20" />

      {/* -- Header -- */}
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold tracking-tight text-white">
            Business Intelligence
          </CardTitle>
          <span className="text-[10px] uppercase tracking-wide text-white/60">
            Updated 2 min ago
          </span>
        </div>

        {/* Priority badges */}
        <div className="mt-3 flex items-center gap-2 text-xs font-medium text-white/90">
          <PriorityChip color="bg-red-500" label={counts.high} />
          <PriorityChip color="bg-orange-400" label={counts.medium} />
          <PriorityChip color="bg-emerald-500" label={counts.low} />
          <span className="ml-auto text-[9px] text-white/60">New 2</span>
        </div>

        {/* Heat-meter */}
        <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-slate-700/60">
          <span
            className="bg-red-500"
            style={{ width: `${widths.high}%` }}
          />
          <span
            className="bg-orange-400"
            style={{ width: `${widths.medium}%` }}
          />
          <span
            className="bg-emerald-500"
            style={{ width: `${widths.low}%` }}
          />
        </div>
      </CardHeader>

      {/* -- Content -- */}
      <CardContent className="space-y-4 pt-0 text-sm text-white">
        {/* High-urgency bucket */}
        <div>
          <p className="font-semibold">High‑Urgency · {highUrgency.length}</p>

          <ul className="mt-3 space-y-2">
            {highUrgency.slice(0, 3).map((item, idx) => (
              <li
                key={idx}
                className="flex items-start justify-between gap-3 rounded-lg px-2 py-1 transition-colors hover:bg-slate-800/60"
              >
                <div className="flex items-start gap-2">
                  <span className="mt-2 h-2 w-2 flex-shrink-0 rounded-full bg-red-500" />
                  <span className="line-clamp-2 text-xs leading-snug">
                    {item.label}
                  </span>
                </div>
                <div className="flex flex-shrink-0 gap-2 text-white/60">
                  <IconButton icon={Check} />
                  <IconButton icon={Snooze} />
                </div>
              </li>
            ))}
          </ul>

          <button
            className="mt-2 text-[10px] font-medium uppercase tracking-wide text-primary hover:underline"
          >
            See more
          </button>
        </div>

        {/* Severity totals */}
        <div className="flex items-center justify-between text-[11px] font-medium text-white/90">
          <span>Total {total}</span>
          <span className="text-white/60">Mid {counts.medium}</span>
          <span className="text-white/60">Low {counts.low}</span>
        </div>

        {/* Channel breakdown */}
        <div className="flex flex-wrap items-center gap-4 text-[11px] text-white/90">
          <ChannelChip icon={Mail} count={channelCounts.mail} />
          <ChannelChip icon={Twitter} count={channelCounts.twitter} />
          <ChannelChip icon={Globe} count={channelCounts.web} />
          <ChannelChip icon={StickyNote} count={channelCounts.notes} />
        </div>
      </CardContent>
    </Card>
  );
}

/* -------------------------------------------------------------------------- */

function PriorityChip({ color, label }) {
  return (
    <span className={`flex items-center gap-1 rounded-full px-2 py-[2px] ${color}/20`}> 
      <span className={`h-2 w-2 rounded-full ${color}`} /> {label}
    </span>
  );
}

function ChannelChip({ icon: Icon, count }) {
  return (
    <span className="flex items-center gap-1">
      <Icon className="h-4 w-4" /> {count}
    </span>
  );
}

function IconButton({ icon: Icon }) {
  return (
    <button
      className="rounded-md p-1 hover:bg-white/5"
    >
      <Icon className="h-3 w-3" />
    </button>
  );
}
