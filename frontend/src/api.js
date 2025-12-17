// src/api.js

const API_BASE = "http://localhost:8000/api/v1";

// Generic Helper
export const apiCall = async (endpoint, payload) => {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("API Error");
    return await response.json();
  } catch (err) {
    console.error(err);
    alert("Error connecting to AI. Check console.");
    return null;
  }
};

// --- NEW DB FUNCTIONS ---

export const fetchProjects = async () => {
  const res = await fetch(`${API_BASE}/projects`);
  return await res.json();
};

export const fetchProjectDetails = async (id) => {
  const res = await fetch(`${API_BASE}/projects/${id}`);
  return await res.json();
};

export const saveProjectToDB = async (payload) => {
  const res = await fetch(`${API_BASE}/projects/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return await res.json();
};