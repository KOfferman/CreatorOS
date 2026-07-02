export function IgIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={{ flexShrink: 0 }}>
      <defs>
        <linearGradient id="igG" x1="0" y1="1" x2="1" y2="0">
          <stop offset="0%" stopColor="#F58529" />
          <stop offset="50%" stopColor="#E1306C" />
          <stop offset="100%" stopColor="#833AB4" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="20" height="20" rx="6" fill="url(#igG)" />
      <circle cx="12" cy="12" r="4.2" stroke="white" strokeWidth="1.6" fill="none" />
      <circle cx="17.4" cy="6.6" r="1.1" fill="white" />
    </svg>
  );
}

export function TtIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={{ flexShrink: 0 }}>
      <rect x="2" y="2" width="20" height="20" rx="6" fill="#010101" />
      <path
        d="M15.8 8.6a4.4 4.4 0 0 1-2.6.8v3.8a3 3 0 1 1-1.2-2.4V9a5.2 5.2 0 1 0 5.2 5.2V9.6a6.8 6.8 0 0 1-3.8-1"
        fill="none"
        stroke="white"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function YtIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" style={{ flexShrink: 0 }}>
      <rect x="2" y="2" width="20" height="20" rx="6" fill="#FF0000" />
      <polygon points="10,9 17,12 10,15" fill="white" />
    </svg>
  );
}
