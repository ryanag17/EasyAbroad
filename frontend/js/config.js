// const API_BASE = "http://localhost:8000";
const API_BASE = "https://easy-abroad.de/api";

const AUTH_API        = `${API_BASE}/auth`;
const PROFILE_API     = `${API_BASE}/profile`;
const MESSAGE_API     = `${API_BASE}/messages`;
const APPOINT_API     = `${API_BASE}/appointments`;
const SUPPORT_API     = `${API_BASE}/support`;
const NOTIFY_API      = `${API_BASE}/notifications`;
const ADMIN_API       = `${API_BASE}/admin`;
const CONSULTANCY_API = `${API_BASE}/consultancy`;
const STATISTICS_API  = `${API_BASE}/statistics`;
const USERS_API       = `${API_BASE}/users`;
const PAYMENT_API     = `${API_BASE}/payment`;

const AppConfig = {
  API_BASE,
  AUTH: AUTH_API,
  PROFILE: PROFILE_API,
  MESSAGES: MESSAGE_API,
  APPOINTMENTS: APPOINT_API,
  SUPPORT: SUPPORT_API,
  NOTIFICATIONS: NOTIFY_API,
  ADMIN: ADMIN_API,
  CONSULTANCY: CONSULTANCY_API,
  STATISTICS: STATISTICS_API,
  USERS: USERS_API,
  PAYMENT: PAYMENT_API
};

window.AppConfig = AppConfig;