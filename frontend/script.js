// ── 1) YOUR API BASE URL ─────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000/api/auth";
window.API_BASE = API_BASE;

// ── 2) PING BACKEND ─────────────────────────────────────────────────────────────────
fetch("http://localhost:8000/")
  .then((res) => res.json())
  .then((data) => console.log("Backend:", data))
  .catch(() => console.warn("Backend ping failed"));

// ── 3) DOM-READY LISTENERS ──────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  // form helpers
  initEmailChecker();
  initPasswordToggles();

  // Register button
  const registerBtn = document.getElementById("registerBtn");
  if (registerBtn) {
    registerBtn.addEventListener("click", async () => {
      console.log("🔘 Register clicked");
      if (!validateRegisterForm()) return;
      if (!document.getElementById("terms-checkbox").checked) {
        return alert("Please agree to the Terms and Conditions.");
      }
      await registerUser();
    });
  }

  // Log In button (if present)
  const loginBtn = document.querySelector(".login");
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      if (validateLoginForm()) loginUser();
    });
  }
});

// ── 4) REGISTER / LOGIN / PASSWORD FLOWS ───────────────────────────────────────────
async function registerUser() {
  const first_name = document.getElementById("name").value.trim();
  const last_name  = document.getElementById("surname").value.trim();
  const role       = document.querySelector("input[name='role']:checked").value;
  const birthday   = document.getElementById("birthday").value;       // YYYY-MM-DD
  const email      = document.getElementById("email-id").value.trim();
  const password   = document.getElementById("password-id").value;

  const payload = { first_name, last_name, role, birthday, email, password };
  console.log("📡 POST /register payload:", payload);

  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    console.log("📶 Status:", res.status);
    const data = await res.json();
    console.log("↩️ Response:", data);

    if (res.ok) {
      alert(data.message);
      window.location.href = "log-in.html";
    } else {
      alert("Registration failed: " + (data.detail || data.message));
    }
  } catch (err) {
    console.error("⚠️ registerUser error:", err);
    alert("An unexpected error occurred. See console for details.");
  }
}

async function loginUser() {
  const email    = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    console.log("Login status:", res.status);
    const data = await res.json();
    console.log("Login response:", data);

    if (res.ok && data.access_token) {
      localStorage.setItem("accessToken", data.access_token);
      window.location.href = "student/home.html";
    } else {
      alert("Login failed: " + (data.detail || data.message));
    }
  } catch (err) {
    console.error("⚠️ loginUser error:", err);
    alert("Network error. See console.");
  }
}

async function forgotPassword() {
  const email = document.getElementById("email-id").value.trim();
  try {
    const res = await fetch(`${API_BASE}/forgot-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    console.log("Forgot-pw status:", res.status);
    const data = await res.json();
    console.log("Forgot-pw response:", data);

    if (res.ok) {
      document.getElementById("popup").style.display = "block";
    } else {
      alert("Error: " + (data.detail || data.message));
    }
  } catch (err) {
    console.error("⚠️ forgotPassword error:", err);
    alert("Network error. See console.");
  }
}

async function resetPassword() {
  const token    = new URLSearchParams(window.location.search).get("token");
  const password = document.getElementById("password-id").value;

  try {
    const res = await fetch(`${API_BASE}/reset-password`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password }),
    });
    console.log("Reset-pw status:", res.status);
    const data = await res.json();
    console.log("Reset-pw response:", data);

    alert(data.message || data.detail || "Password reset!");
    if (res.ok) window.location.href = "log-in.html";
  } catch (err) {
    console.error("⚠️ resetPassword error:", err);
    alert("Network error. See console.");
  }
}

// ── 5) FORM VALIDATORS ─────────────────────────────────────────────────────────────
function validateRegisterForm() {
  const n = document.getElementById("name").value.trim();
  const s = document.getElementById("surname").value.trim();
  const b = document.getElementById("birthday").value;
  const e = document.getElementById("email-id").value.trim();
  const p = document.getElementById("password-id").value;
  const r = document.getElementById("repeat").value;
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!n || !s || !b || !e || !p || !r) {
    alert("All fields are required.");
    return false;
  }
  if (!emailRe.test(e)) {
    alert("Please enter a valid email.");
    return false;
  }
  if (p.length < 6) {
    alert("Password must be at least 6 characters long.");
    return false;
  }
  if (p !== r) {
    alert("Passwords do not match.");
    return false;
  }
  return true;
}

function validateLoginForm() {
  const e = document.getElementById("email-id").value.trim();
  const p = document.getElementById("password-id").value;
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!e || !p) {
    alert("Please fill in both email and password.");
    return false;
  }
  if (!emailRe.test(e)) {
    alert("Invalid email format.");
    return false;
  }
  return true;
}

// ── 6) EMAIL CHECKER & PASSWORD TOGGLE ─────────────────────────────────────────────
function initEmailChecker() {
  const emailId = document.getElementById("email-id"),
        icon    = document.getElementById("icon"),
        error   = document.getElementById("error-msg"),
        re      = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailId) return;
  emailId.addEventListener("input", () => {
    icon.style.display = "none";
    if (re.test(emailId.value)) {
      icon.innerHTML = '<i class="fas fa-check-circle"></i>';
      icon.style.color = "#2ecc71";
      error.style.display = "none";
      emailId.style.border = "2px solid #2ecc71";
    } else if (!emailId.value) {
      error.style.display = "none";
      emailId.style.border = "2px solid #d1d3d4";
    } else {
      icon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
      icon.style.color = "#ff2851";
      error.style.display = "block";
      emailId.style.border = "2px solid #ff2851";
    }
  });
}

function initPasswordToggles() {
  document.querySelectorAll(".toggle-password").forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const input = document.querySelector(toggle.getAttribute("toggle"));
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
      toggle.classList.toggle("fa-eye");
      toggle.classList.toggle("fa-eye-slash");
    });
  });
}
