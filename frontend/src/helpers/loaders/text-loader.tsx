
import React from "react";

interface TextLoaderProps {
  lines?: number;
  className?: string;
  randomWidth?: boolean;
}

export const TextLoader: React.FC<TextLoaderProps> = ({
  lines = 3,
  className = "",
  randomWidth = true
}) => {
  const getRandomWidth = (index: number, totalLines: number) => {
    if (!randomWidth) return "100%";
    const widths = ["90%", "95%", "100%", "85%", "75%"];
    if (index === totalLines - 1) return "60%";
    return widths[Math.floor(Math.random() * widths.length)];
  };

  return (
    <div className={`space-y-2 animate-pulse ${className}`} aria-label="Loading content">
      {Array.from({ length: lines }).map((_, i) => (
        <div 
          key={i}
          className="h-4 bg-muted rounded"
          style={{
            width: getRandomWidth(i, lines),
            opacity: 1 - (i * 0.1)
          }}
        />
      ))}
    </div>
  );
};