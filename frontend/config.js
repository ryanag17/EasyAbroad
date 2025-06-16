// config.js

// Base API URL (adjust this when deploying)
const API_BASE = "http://localhost:8000";

// Grouped endpoints
const AUTH_API      = `${API_BASE}/auth`;
const PROFILE_API   = `${API_BASE}/profile`;
const MESSAGE_API   = `${API_BASE}/messages`;
const APPOINT_API   = `${API_BASE}/appointments`;
const LANGUAGES_API = `${API_BASE}/languages`;
const SUPPORT_API   = `${API_BASE}/support`;
const NOTIFY_API    = `${API_BASE}/notifications`;

// Optional: export as one object
const AppConfig = {
  API_BASE,
  AUTH: AUTH_API,
  PROFILE: PROFILE_API,
  MESSAGES: MESSAGE_API,
  APPOINTMENTS: APPOINT_API,
  LANGUAGES: LANGUAGES_API,
  SUPPORT: SUPPORT_API,
  NOTIFICATIONS: NOTIFY_API
};

// Optionally expose globally for debugging
window.API_BASE   = API_BASE;
window.AUTH_API   = AUTH_API;
window.PROFILE_API= PROFILE_API;
window.MESSAGE_API= MESSAGE_API;
window.AppConfig  = AppConfig;
