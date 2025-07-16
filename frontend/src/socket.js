// src/socket.js

export const connectSocket = (onMessage) => {
  const token = localStorage.getItem("token");
  if (!token) {
    console.error("Token topilmadi");
    return;
  }

  const socket = new WebSocket(`ws://localhost:8000/location/ws/location?token=${token}`);

  socket.onopen = () => {
    console.log("WebSocket connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  socket.onclose = () => {
    console.log("WebSocket disconnected");
  };

  return socket;
};
