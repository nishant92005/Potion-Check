export function DNASpinner({ className = "h-12 w-12" }) {
  return (
    <svg viewBox="0 0 80 80" className={className} aria-hidden="true">
      <g>
        <animateTransform attributeName="transform" type="rotate" from="0 40 40" to="360 40 40" dur="1.5s" repeatCount="indefinite" />
        {Array.from({ length: 7 }).map((_, index) => {
          const y = 12 + index * 9;
          const left = 26 + Math.sin(index) * 8;
          const right = 54 - Math.sin(index) * 8;
          return (
            <g key={index}>
              <line x1={left} y1={y} x2={right} y2={y} stroke="#E8F4FD" strokeOpacity=".45" strokeWidth="2" />
              <circle cx={left} cy={y} r="4" fill="#00FFB2" />
              <circle cx={right} cy={y} r="4" fill="#7B61FF" />
            </g>
          );
        })}
      </g>
    </svg>
  );
}
