// Iconos lineales propios (sin recursos de terceros), con trazo animado.
const P: Record<string, string[]> = {
  check: ["M5 12.5l4.5 4.5L19 7.5"],
  idea: ["M9 18h6", "M10 21h4", "M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2V16h5v-.1c0-.8.4-1.5 1-2A6 6 0 0 0 12 3z"],
  target: ["M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18", "M12 7.5a4.5 4.5 0 1 0 0 9a4.5 4.5 0 1 0 0-9", "M12 11.2a.8.8 0 1 0 0 1.6a.8.8 0 1 0 0-1.6"],
  chart: ["M4 20h16", "M7 16v-4", "M12 16V8", "M17 16V5"],
  users: ["M9 11a3.5 3.5 0 1 0 0-7a3.5 3.5 0 0 0 0 7", "M2.5 20c.6-3.5 3.3-5.5 6.5-5.5s5.9 2 6.5 5.5", "M16 4.3a3.5 3.5 0 0 1 0 6.4", "M18 14.8c2 .7 3.2 2.5 3.5 5.2"],
  book: ["M4 5.5C4 4.7 4.7 4 5.5 4H11v16H5.5A1.5 1.5 0 0 1 4 18.5z", "M20 5.5c0-.8-.7-1.5-1.5-1.5H13v16h5.5a1.5 1.5 0 0 0 1.5-1.5z"],
  star: ["M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"],
  clock: ["M12 3a9 9 0 1 0 0 18a9 9 0 1 0 0-18", "M12 7v5l3.5 2"],
  alert: ["M12 3.5L2.5 20h19z", "M12 10v4.5", "M12 17.2v.3"],
  shield: ["M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5c-4.3-1.2-7.5-4.9-7.5-9.5V6z", "M8.5 12l2.5 2.5 4.5-4.5"],
  rocket: ["M14 4c3.5-1 6-.5 6-.5s.5 2.5-.5 6c-1 3.4-4 6-7.5 7.5L8 13c1.5-3.5 4.1-6.5 6-9z", "M8 13l-3.5 1 2-3.5", "M11 16l-1 3.5 3.5-2", "M15.5 8.5a1 1 0 1 0 0 .1"],
  chat: ["M4 5h16v11H9l-5 4z", "M8 9.5h8", "M8 12.5h5"],
  arrow: ["M4 12h15", "M13 6l6 6-6 6"],
  heart: ["M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.3A4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"],
};
export type IconName = keyof typeof P;

export const Icon: React.FC<{ name: IconName; size: number; color: string; progress?: number; strokeWidth?: number }> = ({
  name,
  size,
  color,
  progress = 1,
  strokeWidth = 1.8,
}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    {P[name].map((d, i) => (
      <path
        key={i}
        d={d}
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - progress}
      />
    ))}
  </svg>
);
