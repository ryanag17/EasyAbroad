fetch('http://localhost:8000/')
  .then(response => response.json())
  .then(data => console.log(data));

  
  
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.login').addEventListener('click', () => {
        console.log('Log in button clicked');
    });

    document.querySelector('.register').addEventListener('click', () => {
        console.log('Register button clicked');
    });
});

// Index picture slider

let currentIndex = 0;

function moveSlide(direction) {
    const slides = document.getElementById("slider-track");
    const totalSlides = slides.children.length;
    const slideWidth = slides.children[0].offsetWidth + 50;

    currentIndex += direction;

    if (currentIndex < 0) {
        currentIndex = totalSlides - 1;
    } else if (currentIndex >= totalSlides) {
        currentIndex = 0;
    }

    slides.scrollTo({
        left: slideWidth * currentIndex,
        behavior: 'smooth'
    });
}

// Register password icon btn

document.addEventListener("DOMContentLoaded", function () {
  const toggles = document.querySelectorAll(".toggle-password");

  toggles.forEach(toggle => {
    toggle.addEventListener("click", function () {
      const input = document.querySelector(this.getAttribute("toggle"));
      const type = input.getAttribute("type") === "password" ? "text" : "password";
      input.setAttribute("type", type);
      this.classList.toggle("fa-eye");
      this.classList.toggle("fa-eye-slash");
    });
  });
});



// FAQ
document.addEventListener("DOMContentLoaded", () => {
  const faqs = document.querySelectorAll("[unique-script-id='w-w-dm-id'] .faq .faq-question-container");

  faqs.forEach(faq => {
    faq.addEventListener("click", () => {
      faq.closest(".faq").classList.toggle("active");
    });
  });
});


document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search");

  // Prevent Enter from submitting the form
  if (searchInput) {
    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        e.preventDefault(); // Stops page reload
      }
    });

    const faqs = document.querySelectorAll(".faq");

    searchInput.addEventListener("input", () => {
      const value = searchInput.value.toLowerCase();
      faqs.forEach(faq => {
        const text = faq.textContent.toLowerCase();
        faq.style.display = text.includes(value) ? "" : "none";
      });
    });
  }
});




// V2_Log-in_page

let emailId = document.getElementById("email-id");
let errorMsg = document.getElementById("error-msg");
let icon = document.getElementById("icon");
let mailRegex = /^[a-zA-Z][a-zA-Z0-9\-\_\.]+@[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}$/;

function checker(){
    icon.style.display="none";
    if(emailId.value.match(mailRegex)){
        icon.innerHTML = '<i class="fas fa-check-circle"></i>';
        icon.style.color = '#2ecc71';
        errorMsg.style.display = 'none';
        emailId.style.border = '2px solid #2ecc71';
    }
    else if(emailId.value == ""){
        icon.style.display = 'none';
        errorMsg.style.display = 'none';
        emailId.style.border = '2px solid #d1d3d4';
    }
    else{
        icon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
        icon.style.color = '#ff2851';
        errorMsg.style.display = 'block';
        emailId.style.border = '2px solid #ff2851';
    }

}


const passwordInput = document.getElementById('password-id');
const toggleCheckbox = document.getElementById('togglePassword');

toggleCheckbox.addEventListener('change', function () {
  if (this.checked) {
    passwordInput.type = 'text';
  } else {
    passwordInput.type = 'password';
  }
});



// ---------------------------------------------------
// START



// Backend part (Vanya & Ximena)


// --- REGISTER ---
async function registerUser() {
  const name = document.getElementById("name").value;
  const surname = document.getElementById("surname").value;
  const role = document.querySelector("input[name='role']:checked").value;
  const email = document.getElementById("email-id").value;
  const password = document.getElementById("password-id").value;

  const response = await fetch(`${API_BASE}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, surname, role, email, password }),
  });

  const data = await response.json();
  console.log(data);
  alert(data.message || "Registered!");
}

// --- LOGIN ---
function loginUser() {
  const email = document.getElementById("email-id").value;
  const password = document.getElementById("password-id").value;

  fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: email,
      password: password
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.token) {
        localStorage.setItem('authToken', data.token);
        window.location.href = 'index.html';
      } else {
        alert('Login failed');
      }
    })
    .catch(error => {
      console.error('Login error:', error);
      alert('Login failed');
    });
  
}


function logoutUser() {
  localStorage.removeItem("auth_token");
  alert("You have been logged out.");
  window.location.href = "index.html"; // or login page
}


function getAuthToken() {
  return localStorage.getItem("auth_token");
}


// --- FORGOT PASSWORD ---
async function forgotPassword() {
  const email = document.getElementById("email-id").value.trim();
  const popup = document.getElementById("popup");

  const response = await fetch("http://localhost:8000/api/auth/forgot-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  const data = await response.json();
  console.log(data);

  if (response.ok) {
    popup.style.display = "block";  
  } else {
    alert(data.error || "Something went wrong. Please try again.");
  }
}

// --- RESET PASSWORD ---
async function resetPassword() {
  const urlParams = new URLSearchParams(window.location.search);
  const token = urlParams.get("token"); // expects ?token=abc123
  const password = document.getElementById("password-id").value;

  const response = await fetch(`${API_BASE}/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, password }),
  });

  const data = await response.json();
  console.log(data);
  alert(data.message || "Password reset!");
}


function validateRegisterForm() {
  const name = document.getElementById("name").value.trim();
  const surname = document.getElementById("surname").value.trim();
  const email = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;
  const repeat = document.getElementById("repeat").value;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!name || !surname || !email || !password || !repeat) {
    alert("All fields are required.");
    return false;
  }

  if (!emailRegex.test(email)) {
    alert("Please enter a valid email address.");
    return false;
  }

  if (password.length < 6) {
    alert("Password must be at least 6 characters long.");
    return false;
  }

  if (password !== repeat) {
    alert("Passwords do not match.");
    return false;
  }

  return true;
}


function validateLoginForm() {
  const email = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!email || !password) {
    alert("Please fill in both email and password.");
    return false;
  }

  if (!emailRegex.test(email)) {
    alert("Invalid email format.");
    return false;
  }

  return true;
}


function validateForgotPasswordForm() {
  const email = document.getElementById("email-id").value.trim();

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!email) {
    alert("Please enter your email address.");
    return false;
  }

  if (!emailRegex.test(email)) {
    alert("Invalid email format.");
    return false;
  }

  return true;
}


function validateResetPasswordForm() {
  const password = document.getElementById("password-id").value;
  const repeat = document.getElementById("repeat").value;

  if (!password || !repeat) {
    alert("Please fill in both password fields.");
    return false;
  }

  if (password.length < 6) {
    alert("Password must be at least 6 characters long.");
    return false;
  }

  if (password !== repeat) {
    alert("Passwords do not match.");
    return false;
  }

  return true;
}


async function fetchCurrentUser() {
  const token = getAuthToken();

  if (!token) {
    alert("No authentication token found. Please log in first.");
    return;
  }

  const response = await fetch("http://localhost:8000/api/auth/me", {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  const data = await response.json();

  if (response.ok) {
    alert(`Logged in as user with ID: ${data.id} and role: ${data.role}`);
  } else {
    alert(data.error || "Failed to fetch user details.");
  }
}






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
