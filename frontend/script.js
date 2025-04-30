const API_BASE = "http://localhost:8000/api";

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
