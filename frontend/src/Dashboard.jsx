import React, { useEffect, useState } from "react";
import { updateLocation } from "./api";
import { connectSocket } from "./socket";
import MapView from "./MapView";

export default function Dashboard() {
  const [location, setLocation] = useState({ latitude: "", longitude: "" });
  const [messages, setMessages] = useState([]);
  const [lastCoord, setLastCoord] = useState(null); // Map uchun

  useEffect(() => {
    const socket = connectSocket((data) => {
      setMessages((prev) => [...prev, data]);
      setLastCoord({ lat: data.lat, lng: data.lng }); // Mapga marker joylash
    });
    return () => socket && socket.close();
  }, []);

  const handleSendLocation = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Iltimos login qiling!");
      return;
    }

    await updateLocation(token, {
      latitude: parseFloat(location.latitude),
      longitude: parseFloat(location.longitude),
    });
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Dashboard</h2>

      <div className="mb-4 space-x-2">
        <input
          className="border px-2 py-1"
          placeholder="Latitude"
          onChange={(e) =>
            setLocation({ ...location, latitude: e.target.value })
          }
        />
        <input
          className="border px-2 py-1"
          placeholder="Longitude"
          onChange={(e) =>
            setLocation({ ...location, longitude: e.target.value })
          }
        />
        <button
          className="bg-blue-500 text-white px-4 py-1 rounded"
          onClick={handleSendLocation}
        >
          Send Location
        </button>
      </div>

      <h3 className="text-lg font-semibold mb-2">Real-time Updates:</h3>
      <ul className="list-disc pl-6 mb-6">
        {messages.map((msg, idx) => (
          <li key={idx}>
            User {msg.user_id}: {msg.lat}, {msg.lng}
          </li>
        ))}
      </ul>

      {/* Real-time map */}
      <MapView coords={lastCoord} />
    </div>
  );
}
