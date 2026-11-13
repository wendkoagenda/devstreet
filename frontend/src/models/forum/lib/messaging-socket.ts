import { io, type Socket } from "socket.io-client";
import type { PrivateMessage } from "../api";

type MessageHandler = (message: PrivateMessage) => void;

let socket: Socket | null = null;
const messageHandlers = new Set<MessageHandler>();

function getSocket(): Socket {
  if (socket) return socket;

  socket = io("/", {
    path: "/socket.io",
    withCredentials: true,
    transports: ["websocket", "polling"],
    autoConnect: true,
  });

  socket.on("message:new", (payload: PrivateMessage) => {
    messageHandlers.forEach((handler) => handler(payload));
  });

  socket.on("connect_error", (error) => {
    console.error("Socket.IO messagerie :", error.message);
  });

  return socket;
}

export function connectMessagingSocket(): Socket {
  return getSocket();
}

export function joinConversationRoom(conversationId: number): void {
  const s = getSocket();
  if (!s.connected) {
    s.once("connect", () => {
      s.emit("join_conversation", { conversation_id: conversationId });
    });
    s.connect();
    return;
  }
  s.emit("join_conversation", { conversation_id: conversationId });
}

export function leaveConversationRoom(conversationId: number): void {
  if (!socket?.connected) return;
  socket.emit("leave_conversation", { conversation_id: conversationId });
}

export function subscribeToNewMessages(handler: MessageHandler): () => void {
  getSocket();
  messageHandlers.add(handler);
  return () => {
    messageHandlers.delete(handler);
  };
}
