import React, { useEffect, useState } from "react";
import axios from "axios";

const LocationTable = ({ token }) => {
  const [locations, setLocations] = useState([]);

  useEffect(() => {
    axios
      .get("http://localhost:8000/locations/", {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      .then((res) => setLocations(res.data))
      .catch((err) => console.error("Error fetching locations:", err));
  }, [token]);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-2">Joylashuvlar Tarixi</h2>
      <table className="table-auto w-full border border-gray-300">
        <thead>
          <tr className="bg-gray-200">
            <th className="px-4 py-2 border">ID</th>
            <th className="px-4 py-2 border">Latitude</th>
            <th className="px-4 py-2 border">Longitude</th>
            <th className="px-4 py-2 border">Vaqt</th>
          </tr>
        </thead>
        <tbody>
          {locations.map((loc) => (
            <tr key={loc.id} className="text-center">
              <td className="px-4 py-2 border">{loc.id}</td>
              <td className="px-4 py-2 border">{loc.latitude}</td>
              <td className="px-4 py-2 border">{loc.longitude}</td>
              <td className="px-4 py-2 border">{new Date(loc.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LocationTable;
