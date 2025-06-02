// ─────────────────────────────────────────────────────────────
// Frontend JS Functions
// DO NOT DELETE
// ─────────────────────────────────────────────────────────────
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

if (toggleCheckbox && passwordInput) {
  toggleCheckbox.addEventListener('change', function () {
    if (this.checked) {
      passwordInput.type = 'text';
    } else {
      passwordInput.type = 'password';
    }
  });
}


// ─────────────────────────────────────────────────────────────
// DO NOT DELETE
// Frontend JS Functions END
// ─────────────────────────────────────────────────────────────





// ─────────────────────────────────────────────────────────────
// Backend JS Functions START
// ─────────────────────────────────────────────────────────────

// 1) YOUR API BASE URL
const API_BASE = "http://localhost:8000/auth";

// 2) PING BACKEND
fetch("http://localhost:8000/")
  .then((res) => res.json())
  .then((data) => console.log("Backend is running:", data))
  .catch(() => console.warn("Backend ping failed"));

// 3) REGISTER USER
async function registerUser() {
  const payload = {
    name: document.getElementById("name").value.trim(),
    surname: document.getElementById("surname").value.trim(),
    role: document.querySelector("input[name='role']:checked").value,
    email: document.getElementById("email-id").value.trim(),
    password: document.getElementById("password-id").value,
    birthday: document.getElementById("birthday").value || null,
  };

  console.log("📡 POST /auth/register payload:", payload);

  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // HttpOnly refresh_token cookie
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      alert("✅ Registration successful! Redirecting to login…");
      window.location.href = "log-in.html";
    } else {
      const data = await res.json();
      alert("❌ Registration failed: " + (data.detail || data.message || res.status));
    }
  } catch (err) {
    console.error("Error during register:", err);
    alert("❌ Registration failed due to network error");
  }
}

// 4) LOGIN USER
async function loginUser() {
  const email = document.getElementById("email-id").value.trim();
  const password = document.getElementById("password-id").value;

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method:      "POST",
      headers:     { "Content-Type": "application/json" },
      credentials: "include",
      body:        JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (res.ok && data.access_token) {
      // 1) store the JWT
      sessionStorage.setItem("accessToken", data.access_token);

      // 2) redirect based on the role
      if (data.role === "student") {
        window.location.href = "student/home.html";
      }
      else if (data.role === "consultant") {
        window.location.href = "consultant/home.html";
      }
      else if (data.role === "admin") {
        window.location.href = "admin/home.html";
      }
      else {
        alert("Unknown role: " + data.role);
      }
    }
    else {
      alert("Login failed: " + (data.detail || data.message));
    }
  }
  catch (err) {
    console.error("Error during login:", err);
    alert("❌ Login failed due to network error");
  }
}


// 5) FETCH PROFILE
async function fetchProfile(role) {
  const token = sessionStorage.getItem("accessToken");
  const res = await fetch(`${API_BASE}/${role}/profile`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    credentials: "include",
  });
  if (!res.ok) throw new Error(`Failed to fetch ${role} profile (${res.status})`);
  return await res.json();
}

// 6) Validate Register Form
function validateRegisterForm() {
  const nameVal    = document.getElementById("name").value.trim();
  const surnameVal = document.getElementById("surname").value.trim();
  const emailVal   = document.getElementById("email-id").value.trim();
  const pwVal      = document.getElementById("password-id").value;
  const repeatVal  = document.getElementById("repeat").value;

  if (!nameVal) {
    alert("Please enter your name.");
    document.getElementById("name").focus();
    return false;
  }
  if (!surnameVal) {
    alert("Please enter your surname.");
    document.getElementById("surname").focus();
    return false;
  }
  const mailRegex = /^[a-zA-Z][a-zA-Z0-9\-\_\.]+@[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}$/;
  if (!emailVal.match(mailRegex)) {
    alert("Please enter a valid email address.");
    document.getElementById("email-id").focus();
    return false;
  }
  if (pwVal.length < 6) {
    alert("Password must be at least 6 characters.");
    document.getElementById("password-id").focus();
    return false;
  }
  if (pwVal !== repeatVal) {
    alert("Passwords do not match.");
    document.getElementById("repeat").focus();
    return false;
  }
  return true;
}

function validateLoginForm() {
  const email = document.getElementById("email-id").value.trim();
  const pw    = document.getElementById("password-id").value;

  // 1) Basic email check
  const mailRegex = /^[a-zA-Z][a-zA-Z0-9\-_\.]+@[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}$/;
  if (!email.match(mailRegex)) {
    alert("Please enter a valid email address.");
    document.getElementById("email-id").focus();
    return false;
  }

  // 2) Ensure password is not empty
  if (!pw) {
    alert("Please enter your password.");
    document.getElementById("password-id").focus();
    return false;
  }

  return true;
}

// Expose it so the login HTML can see it:
window.validateLoginForm = validateLoginForm;

// Expose functions for inline use
window.registerUser   = registerUser;
window.loginUser      = loginUser;
window.fetchProfile   = fetchProfile;
window.validateRegisterForm = validateRegisterForm;
window.validateLoginForm = validateLoginForm;

// ─────────────────────────────────────────────────────────────
// Backend JS Functions END
// ─────────────────────────────────────────────────────────────