import { createContext, useContext, useEffect, useRef } from "react";

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/cheat");

    ws.current.onopen = () => console.log("Connected");
    ws.current.onmessage = (e) => console.log("Message:", e.data);
    ws.current.onclose = () => console.log("Closed");

    return () => ws.current?.close();
  }, []);

  return (
    <WebSocketContext.Provider value={ws}>{children}</WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);
