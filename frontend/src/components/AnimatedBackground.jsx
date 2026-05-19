export function AnimatedBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden animated-bg animate-universe">
      <svg className="absolute inset-0 h-full w-full animate-hexPulse" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="hexGrid" width="56" height="48" patternUnits="userSpaceOnUse">
            <path d="M14 1h28l14 23-14 23H14L0 24 14 1Z" fill="none" stroke="#00FFB2" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#hexGrid)" />
      </svg>
      {Array.from({ length: 44 }).map((_, index) => (
        <span
          key={index}
          className="absolute h-1 w-1 rounded-full bg-mint opacity-20 animate-drift"
          style={{
            left: `${(index * 29) % 100}%`,
            animationDuration: `${10 + (index % 8)}s`,
            animationDelay: `${index * -0.55}s`
          }}
        />
      ))}
    </div>
  );
}
