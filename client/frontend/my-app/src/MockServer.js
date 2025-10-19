const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080 });

console.log("✅ Mock WebSocket server running on ws://localhost:8080");

wss.on("connection", (ws, req) => {
  const clientAddress = req.socket.remoteAddress;
  console.log(`🔌 New client connected from ${clientAddress}`);

  ws.on("message", (data, isBinary) => {
    const message = isBinary ? data : data.toString();
    console.log(`📩 Received from ${clientAddress}:`, message);

    ws.send(JSON.stringify({ type: "echo", data: message }));

    // Try to parse JSON (optional)
    try {
      const json = JSON.parse(message);
      console.log("🧩 Parsed message object:", json);
    } catch {
      console.log("⚠️ Message not valid JSON");
    }

    // Echo back a response for testing
    ws.send(JSON.stringify({ type: "echo", data: message }));
  });

  ws.on("close", () => {
    console.log(`❌ Connection closed from ${clientAddress}`);
  });

  // Send a welcome message on connect
  ws.send(JSON.stringify({ type: "welcome", msg: "Connected to mock server" }));
});
