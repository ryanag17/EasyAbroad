// ── 1) YOUR API BASE URL ─────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000/auth";

// ── 2) PING BACKEND ─────────────────────────────────────────────────────────────────
fetch("http://localhost:8000/")
  .then(res => res.json())
  .then(data => console.log("Backend is running:", data))
  .catch(() => console.warn("Backend ping failed"));

// ── 3) FORM HELPERS ─────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  initEmailChecker();
  initPasswordToggles();
});

// ── 4) REGISTER USER ───────────────────────────────────────────────────────────────
async function registerUser() {
  const payload = {
    name:     document.getElementById("name").value.trim(),
    surname:  document.getElementById("surname").value.trim(),
    role:     document.querySelector("input[name='role']:checked").value,
    email:    document.getElementById("email-id").value.trim(),
    password: document.getElementById("password-id").value
  };
  console.log("📡 POST /register payload:", payload);

  const res = await fetch(`${API_BASE}/register`, {
    method:      "POST",
    headers:     { "Content-Type": "application/json" },
    credentials: 'include',  // send/receive refresh_token cookie
    body:         JSON.stringify(payload)
  });
  console.log("📶 Status:", res.status);

  if (res.ok) {
    // Registration sets refresh cookie; redirect to login
    window.location.href = "log-in.html";
  } else {
    const data = await res.json();
    alert("Registration failed: " + (data.detail || data.message || res.status));
  }
}

// ── 5) LOGIN USER ──────────────────────────────────────────────────────────────────
async function loginUser() {
  const email    = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;

  const res = await fetch(`${API_BASE}/login`, {
    method:      "POST",
    headers:     { "Content-Type": "application/json" },
    credentials: 'include',
    body:         JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (res.ok && data.access_token) {
    // store tokens
    sessionStorage.setItem("accessToken", data.access_token);
    // redirect based on role
    if (data.role === "student") {
      window.location.href = "student/home.html";
    } else if (data.role === "consultant") {
      window.location.href = "consultant/home.html";
    } else {
      alert("Unknown role: " + data.role);
    }
  } else {
    alert("Login failed: " + (data.detail || data.message));
  }
}


// ── 6) FETCH PROFILE (example) ─────────────────────────────────────────────────────
async function fetchProfile(role) {
  const token = sessionStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE}/${role}/profile`, {
    method:      "GET",
    headers:     {
      "Content-Type":  "application/json",
      "Authorization": `Bearer ${token}`
    },
    credentials: 'include'
  });
  if (!res.ok) throw new Error(`Failed to fetch ${role} profile (${res.status})`);
  return await res.json();
}

// Expose to global for inline handlers
window.registerUser = registerUser;
window.loginUser    = loginUser;
window.fetchProfile = fetchProfile;
