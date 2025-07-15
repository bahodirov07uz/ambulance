import React, { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import { connectSocket } from "./socket";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Marker ikonkani to‘g‘rilash (Leaflet default ikonkasini yuklamaydi)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

function MapUpdater({ coords }) {
  const map = useMap();
  useEffect(() => {
    if (coords) {
      map.setView([coords.lat, coords.lng], 15);
    }
  }, [coords, map]);
  return null;
}

export default function MapView() {
  const [coords, setCoords] = useState(null);

  useEffect(() => {
    const socket = connectSocket((data) => {
      console.log("Location update:", data);
      setCoords({ lat: data.lat, lng: data.lng });
    });
    return () => socket.close();
  }, []);

  return (
    <div style={{ height: "100vh" }}>
      <MapContainer center={[41.3, 69.3]} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution="© OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {coords && (
          <Marker position={[coords.lat, coords.lng]}>
            <Popup>User is here</Popup>
          </Marker>
        )}
        <MapUpdater coords={coords} />
      </MapContainer>
    </div>
  );
}
