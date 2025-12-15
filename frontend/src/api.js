const API_BASE = "http://localhost:8000/api/v1"; 

// Helper to manage a fake session ID for the browser
const getSessionId = () => {
  let id = localStorage.getItem("story_session_id");
  if (!id) {
    id = "sess_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("story_session_id", id);
  }
  return id;
};

export const apiCall = async (endpoint, payload) => {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: getSessionId(),
        ...payload
      }),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "API Error");
    }

    return await response.json();
  } catch (error) {
    console.error("API Request Failed:", error);
    alert(`Error: ${error.message}`);
    return null;
  }
};