import axios from "axios";
const API_URL = "http://localhost:8000";

export const login = (username, password) =>
  axios.post(`${API_URL}/token`, new URLSearchParams({ username, password }));

export const register = (data) =>
  axios.post(`${API_URL}/users/`, data);

export const updateLocation = (token, data) =>
  axios.post(`${API_URL}/location/update_location`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const getDrivers = (token) =>
  axios.get(`${API_URL}/drivers/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
