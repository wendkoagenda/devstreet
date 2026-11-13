import { useEffect, useRef, useState } from "react";
import { Pause, Play, Volume2, VolumeX } from "lucide-react";
import { buildMediaUrl } from "@/helpers/displayers/media-url-builder";
import { cn } from "@/lib/utils";

/** Un seul autoplay à la fois dans le fil (comportement type LinkedIn). */
let activeFeedVideo: HTMLVideoElement | null = null;

type FeedVideoPlayerProps = {
  src: string;
  label?: string;
  className?: string;
  /** Boucle courte en aperçu muet */
  loopPreview?: boolean;
};

export function FeedVideoPlayer({
  src,
  label,
  className,
  loopPreview = true,
}: FeedVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [inView, setInView] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(true);
  const [userActivated, setUserActivated] = useState(false);
  const mediaSrc = buildMediaUrl(src);
  // #t=0.1 force le navigateur à décoder une 1re frame (poster natif)
  const previewSrc = mediaSrc.includes("#")
    ? mediaSrc
    : `${mediaSrc}#t=0.1`;

  useEffect(() => {
    const node = videoRef.current;
    if (!node) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        setInView(Boolean(entry?.isIntersecting && entry.intersectionRatio >= 0.55));
      },
      { threshold: [0, 0.55, 0.8] }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const node = videoRef.current;
    if (!node) return;

    if (inView && !userActivated) {
      if (activeFeedVideo && activeFeedVideo !== node) {
        activeFeedVideo.pause();
      }
      activeFeedVideo = node;
      node.muted = true;
      setMuted(true);
      void node.play().then(() => setPlaying(true)).catch(() => setPlaying(false));
      return;
    }

    if (!inView && !userActivated) {
      node.pause();
      setPlaying(false);
      if (activeFeedVideo === node) activeFeedVideo = null;
    }
  }, [inView, userActivated]);

  useEffect(() => {
    return () => {
      if (activeFeedVideo === videoRef.current) activeFeedVideo = null;
    };
  }, []);

  const togglePlay = () => {
    const node = videoRef.current;
    if (!node) return;
    setUserActivated(true);
    if (node.paused) {
      if (activeFeedVideo && activeFeedVideo !== node) {
        activeFeedVideo.pause();
      }
      activeFeedVideo = node;
      void node.play().then(() => setPlaying(true)).catch(() => setPlaying(false));
    } else {
      node.pause();
      setPlaying(false);
    }
  };

  const toggleMute = () => {
    const node = videoRef.current;
    if (!node) return;
    setUserActivated(true);
    node.muted = !node.muted;
    setMuted(node.muted);
  };

  return (
    <div
      className={cn(
        "group/video relative overflow-hidden rounded-xl bg-muted",
        className
      )}
    >
      <video
        ref={videoRef}
        src={previewSrc}
        muted={muted}
        playsInline
        loop={loopPreview && !userActivated}
        preload="metadata"
        className="max-h-80 w-full object-cover"
        aria-label={label || "Vidéo"}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onClick={togglePlay}
      />
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-foreground/35 via-transparent to-transparent opacity-80" />
      <div className="absolute bottom-2 left-2 flex items-center gap-1">
        <button
          type="button"
          onClick={togglePlay}
          className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-background/90 text-foreground shadow-sm"
          aria-label={playing ? "Pause" : "Lecture"}
        >
          {playing ? (
            <Pause className="h-3.5 w-3.5" />
          ) : (
            <Play className="h-3.5 w-3.5" />
          )}
        </button>
        <button
          type="button"
          onClick={toggleMute}
          className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-background/90 text-foreground shadow-sm"
          aria-label={muted ? "Activer le son" : "Couper le son"}
        >
          {muted ? (
            <VolumeX className="h-3.5 w-3.5" />
          ) : (
            <Volume2 className="h-3.5 w-3.5" />
          )}
        </button>
      </div>
      {!userActivated && muted ? (
        <span className="pointer-events-none absolute right-2 top-2 rounded-md bg-background/85 px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
          Aperçu muet
        </span>
      ) : null}
    </div>
  );
}
