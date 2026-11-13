import { useEffect, useRef, useState } from "react";
import { Loader2, Mic, Square, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useUploadForumMediaMutation } from "../api";

type VoiceRecorderButtonProps = {
  disabled?: boolean;
  onRecorded: (payload: {
    url: string;
    kind: "AUDIO";
    texte_alternatif: string;
  }) => void | Promise<void>;
  className?: string;
  /** Variante compacte pour le chat */
  compact?: boolean;
  confirmLabel?: string;
};

function pickMimeType() {
  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/mp4",
    "audio/ogg",
  ];
  for (const type of candidates) {
    if (
      typeof MediaRecorder !== "undefined" &&
      MediaRecorder.isTypeSupported(type)
    ) {
      return type;
    }
  }
  return "";
}

export function VoiceRecorderButton({
  disabled,
  onRecorded,
  className,
  compact = false,
  confirmLabel = "Joindre",
}: VoiceRecorderButtonProps) {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewBlob, setPreviewBlob] = useState<Blob | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);
  const [uploadMedia, { isLoading: uploading }] =
    useUploadForumMediaMutation();

  useEffect(() => {
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
      streamRef.current?.getTracks().forEach((track) => track.stop());
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const clearPreview = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setPreviewBlob(null);
    setSeconds(0);
  };

  const startRecording = async () => {
    if (
      typeof navigator === "undefined" ||
      !navigator.mediaDevices?.getUserMedia
    ) {
      toast.error("Micro non supporté sur ce navigateur");
      return;
    }
    try {
      clearPreview();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mimeType = pickMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        stream.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        if (blob.size < 800) {
          toast.error("Enregistrement trop court");
          setRecording(false);
          return;
        }
        const url = URL.createObjectURL(blob);
        setPreviewBlob(blob);
        setPreviewUrl(url);
        setRecording(false);
      };
      recorder.start(200);
      setRecording(true);
      setSeconds(0);
      timerRef.current = window.setInterval(() => {
        setSeconds((value) => {
          if (value >= 120) {
            stopRecording();
            return value;
          }
          return value + 1;
        });
      }, 1000);
    } catch {
      toast.error("Autorise l'accès au micro pour enregistrer");
    }
  };

  const stopRecording = () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    } else {
      setRecording(false);
    }
  };

  const sendRecording = async () => {
    if (!previewBlob) return;
    const ext = previewBlob.type.includes("mp4")
      ? "m4a"
      : previewBlob.type.includes("ogg")
        ? "ogg"
        : "webm";
    const file = new File(
      [previewBlob],
      `vocal-${Date.now()}.${ext}`,
      { type: previewBlob.type || "audio/webm" }
    );
    try {
      const uploaded = await uploadMedia({
        file,
        kind: "AUDIO",
      }).unwrap();
      await onRecorded({
        url: uploaded.url,
        kind: "AUDIO",
        texte_alternatif: "Message vocal",
      });
      clearPreview();
    } catch {
      toast.error("Impossible d'envoyer le vocal");
    }
  };

  if (previewUrl && previewBlob) {
    return (
      <div
        className={cn(
          "flex items-center gap-2 rounded-xl border border-border bg-muted/40 px-2 py-1.5",
          className
        )}
      >
        <audio src={previewUrl} controls className="h-8 max-w-[180px]" />
        <Button
          type="button"
          size="sm"
          variant="ghost"
          className="h-8 w-8 p-0"
          aria-label="Supprimer le vocal"
          onClick={clearPreview}
        >
          <Trash2 className="h-3.5 w-3.5" />
        </Button>
        <Button
          type="button"
          size="sm"
          className="h-8"
          disabled={uploading}
          onClick={() => void sendRecording()}
        >
          {uploading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            confirmLabel
          )}
        </Button>
      </div>
    );
  }

  if (recording) {
    return (
      <div
        className={cn(
          "inline-flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/5 px-2 py-1",
          className
        )}
      >
        <span className="h-2 w-2 animate-pulse rounded-full bg-destructive" />
        <span className="text-xs font-medium tabular-nums text-destructive">
          {String(Math.floor(seconds / 60)).padStart(2, "0")}:
          {String(seconds % 60).padStart(2, "0")}
        </span>
        <Button
          type="button"
          size="sm"
          variant="destructive"
          className="h-8 gap-1"
          onClick={stopRecording}
        >
          <Square className="h-3 w-3 fill-current" />
          Stop
        </Button>
      </div>
    );
  }

  return (
    <Button
      type="button"
      size={compact ? "icon" : "sm"}
      variant="ghost"
      className={cn(compact ? "h-8 w-8" : "h-8 gap-1 px-2", className)}
      disabled={disabled || uploading}
      aria-label="Enregistrer un message vocal"
      title="Message vocal"
      onClick={() => void startRecording()}
    >
      <Mic className="h-3.5 w-3.5" />
      {compact ? null : "Vocal"}
    </Button>
  );
}
