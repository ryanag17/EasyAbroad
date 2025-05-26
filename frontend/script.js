// ── 1) YOUR API BASE URL ─────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000/api/auth";
window.API_BASE = API_BASE;

// ── 2) QUICK “PING” AT ROOT ─────────────────────────────────────────────────────────
fetch("http://localhost:8000/")
  .then((res) => res.json())
  .then((data) => console.log(data));

// ── 3) DOM-READY LISTENERS ──────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  // form widgets
  initEmailChecker();
  initPasswordToggles();

  // FAQ collapse
  document
    .querySelectorAll("[unique-script-id='w-w-dm-id'] .faq .faq-question-container")
    .forEach((faq) =>
      faq.addEventListener("click", () =>
        faq.closest(".faq").classList.toggle("active")
      )
    );

  // Search filter
  const searchInput = document.getElementById("search");
  if (searchInput) {
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") e.preventDefault();
    });
    const faqs = document.querySelectorAll(".faq");
    searchInput.addEventListener("input", () => {
      const val = searchInput.value.toLowerCase();
      faqs.forEach((f) => {
        f.style.display = f.textContent.toLowerCase().includes(val) ? "" : "none";
      });
    });
  }

  // Log In button
  const loginBtn = document.querySelector(".login");
  if (loginBtn) {
    loginBtn.addEventListener("click", () => {
      if (validateLoginForm()) loginUser();
    });
  }

  // ── SINGLE REGISTER BUTTON BINDING ─────────────────────────────────────────────
  const registerBtn = document.getElementById("registerBtn");
  if (registerBtn) {
    registerBtn.addEventListener("click", async () => {
      if (!validateRegisterForm()) return;
      await registerUser();   // only ever called once per click
    });
  }
});

// ── 4) NETWORK HELPERS ──────────────────────────────────────────────────────────────
function getToken() {
  return localStorage.getItem("accessToken");
}
function isLoggedIn() {
  return !!getToken();
}
function logoutUser() {
  localStorage.removeItem("accessToken");
  window.location.href = "index.html";
}

// ── 5) UI WIDGETS ─────────────────────────────────────────────────────────────────
let currentIndex = 0;
function moveSlide(direction) {
  const slides = document.getElementById("slider-track");
  if (!slides) return;
  const total = slides.children.length;
  const width = slides.children[0].offsetWidth + 50;
  currentIndex = (currentIndex + direction + total) % total;
  slides.scrollTo({ left: width * currentIndex, behavior: "smooth" });
}

// ── 6) REGISTER / LOGIN / PASSWORD FLOWS ───────────────────────────────────────────
async function registerUser() {
  const name     = document.getElementById("name").value.trim();
  const surname  = document.getElementById("surname").value.trim();
  const role     = document.querySelector("input[name='role']:checked").value;
  const email    = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;

  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, surname, role, email, password })
    });

    const data = await res.json();
    console.log("Register response:", res.status, data);

    if (res.ok) {
      alert(data.message);
      window.location.href = "log-in.html";
    } else {
      alert("Registration failed: " + (data.detail || data.message));
    }
  } catch (err) {
    console.error("Network or JS error:", err);
    alert("An unexpected error occurred. See console for details.");
  }
}

async function loginUser() {
  const email    = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  console.log("Login response:", res.status, data);

  if (res.ok && data.access_token) {
    localStorage.setItem("accessToken", data.access_token);
    window.location.href = "student/home.html";
  } else {
    alert("Login failed: " + (data.detail || data.message));
  }
}

async function forgotPassword() {
  const email = document.getElementById("email-id").value.trim();
  const res = await fetch(`${API_BASE}/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  const data = await res.json();
  console.log("Forgot-pw response:", data);
  if (res.ok) document.getElementById("popup").style.display = "block";
  else alert("Error: " + (data.detail || data.message));
}

async function resetPassword() {
  const token    = new URLSearchParams(window.location.search).get("token");
  const password = document.getElementById("password-id").value;
  const res = await fetch(`${API_BASE}/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, password }),
  });
  const data = await res.json();
  console.log("Reset-pw response:", data);
  alert(data.message || "Password reset!");
}

// ── 7) FORM VALIDATORS ─────────────────────────────────────────────────────────────
function validateRegisterForm() {
  const n = document.getElementById("name").value.trim();
  const s = document.getElementById("surname").value.trim();
  const e = document.getElementById("email-id").value.trim();
  const p = document.getElementById("password-id").value;
  const r = document.getElementById("repeat").value;
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!n || !s || !e || !p || !r) {
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

// ── 8) HELPERS FOR EMAIL CHECKER & PASSWORD TOGGLE ─────────────────────────────────
function initEmailChecker() {
  const emailId = document.getElementById("email-id"),
        icon    = document.getElementById("icon"),
        error   = document.getElementById("error-msg"),
        re      = /^[a-zA-Z][a-zA-Z0-9\-\_\.]+@[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}$/;
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
    toggle.addEventListener("click", function () {
      const input = document.querySelector(this.getAttribute("toggle"));
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
      this.classList.toggle("fa-eye");
      this.classList.toggle("fa-eye-slash");
    });
  });
}

window.API_BASE         = API_BASE;
window.forgotPassword   = forgotPassword;