import { useEffect, useRef, useState } from "react";
import { Pause, Play } from "lucide-react";
import { cn } from "@/lib/utils";

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const total = Math.floor(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${mins}:${String(secs).padStart(2, "0")}`;
}

type ForumAudioPlayerProps = {
  src: string;
  className?: string;
  /** Style plus compact (chat / aperçu). */
  compact?: boolean;
};

export function ForumAudioPlayer({
  src,
  className,
  compact = false,
}: ForumAudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playing, setPlaying] = useState(false);
  const [current, setCurrent] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    setPlaying(false);
    setCurrent(0);
    setDuration(0);
    audio.pause();
    audio.load();
  }, [src]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTime = () => setCurrent(audio.currentTime || 0);
    const onMeta = () => setDuration(audio.duration || 0);
    const onEnded = () => {
      setPlaying(false);
      setCurrent(0);
    };
    const onPlay = () => setPlaying(true);
    const onPause = () => setPlaying(false);

    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("loadedmetadata", onMeta);
    audio.addEventListener("durationchange", onMeta);
    audio.addEventListener("ended", onEnded);
    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);
    return () => {
      audio.removeEventListener("timeupdate", onTime);
      audio.removeEventListener("loadedmetadata", onMeta);
      audio.removeEventListener("durationchange", onMeta);
      audio.removeEventListener("ended", onEnded);
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
    };
  }, [src]);

  const toggle = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      void audio.play().catch(() => setPlaying(false));
    } else {
      audio.pause();
    }
  };

  const progress = duration > 0 ? Math.min(100, (current / duration) * 100) : 0;

  return (
    <div
      className={cn(
        "flex items-center gap-2.5 rounded-2xl border border-border bg-muted/50",
        compact ? "px-2.5 py-1.5" : "px-3 py-2.5",
        className
      )}
    >
      <audio ref={audioRef} src={src} preload="metadata" className="hidden" />
      <button
        type="button"
        onClick={toggle}
        aria-label={playing ? "Pause" : "Lecture"}
        className={cn(
          "flex shrink-0 items-center justify-center rounded-full bg-brand text-brand-foreground transition hover:bg-brand/90",
          compact ? "size-8" : "size-9"
        )}
      >
        {playing ? (
          <Pause className={cn(compact ? "size-3.5" : "size-4", "fill-current")} />
        ) : (
          <Play
            className={cn(compact ? "size-3.5" : "size-4", "ml-0.5 fill-current")}
          />
        )}
      </button>

      <div className="min-w-0 flex-1 space-y-1">
        <div className="flex items-center justify-between gap-2">
          <span className="text-[11px] font-medium text-muted-foreground">
            Vocal
          </span>
          <span className="text-[11px] tabular-nums text-muted-foreground">
            {formatTime(current)}
            {duration > 0 ? ` / ${formatTime(duration)}` : ""}
          </span>
        </div>
        <input
          type="range"
          min={0}
          max={duration || 0}
          step={0.05}
          value={current}
          aria-label="Progression du vocal"
          disabled={!duration}
          onChange={(event) => {
            const next = Number(event.target.value);
            const audio = audioRef.current;
            if (audio) audio.currentTime = next;
            setCurrent(next);
          }}
          className={cn(
            "h-1.5 w-full cursor-pointer appearance-none rounded-full",
            "disabled:cursor-default disabled:opacity-50",
            "[&::-webkit-slider-runnable-track]:h-1.5 [&::-webkit-slider-runnable-track]:rounded-full",
            "[&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:top-[-3px]",
            "[&::-webkit-slider-thumb]:size-3 [&::-webkit-slider-thumb]:appearance-none",
            "[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[hsl(var(--brand))]",
            "[&::-moz-range-track]:h-1.5 [&::-moz-range-track]:rounded-full",
            "[&::-moz-range-thumb]:size-3 [&::-moz-range-thumb]:rounded-full",
            "[&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:bg-[hsl(var(--brand))]"
          )}
          style={{
            background: `linear-gradient(to right, hsl(var(--brand)) ${progress}%, hsl(var(--border)) ${progress}%)`,
          }}
        />
      </div>
    </div>
  );
}
