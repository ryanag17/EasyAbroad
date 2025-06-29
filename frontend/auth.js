// ─────────────────────────────────────────────
// auth.js — Authentication Helper
// ─────────────────────────────────────────────

// Config
const HOME_REDIRECTS = {
  student: "student/home.html",
  consultant: "consultant/home.html",
  admin: "admin/home.html"
};

// 1) Utility functions
function isLoggedIn() {
  return !!sessionStorage.getItem("accessToken");
}

function getUserType() {
  return sessionStorage.getItem("userType");
}

function requireAuth(redirectIfMissing = "log-in.html") {
  if (!isLoggedIn() || !getUserType()) {
    window.location.href = redirectIfMissing;
  }
}

async function requireRole(requiredRole) {
  const token = sessionStorage.getItem("accessToken");
  const currentRole = sessionStorage.getItem("userType");

  if (!token || !currentRole || currentRole !== requiredRole) {
    window.location.href = "../log-in.html";
    return;
  }

  const endpointMap = {
    student: "http://localhost:8000/profile/student",
    consultant: "http://localhost:8000/profile/consultant",
    admin: "http://localhost:8000/profile/admin"
  };

  try {
    const res = await fetch(endpointMap[currentRole], {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("Unauthorized");

  } catch (err) {
    sessionStorage.clear();
    window.location.href = "../log-in.html";
  }
}

async function autoEnforceRoleFromPath() {
  const path = window.location.pathname;
  if (path.includes("/student/")) {
    await requireRole("student");
  } else if (path.includes("/consultant/")) {
    await requireRole("consultant");
  } else if (path.includes("/admin/")) {
    await requireRole("admin");
  }
}


async function redirectIfAuthenticated() {
  const token = sessionStorage.getItem("accessToken");
  const role = sessionStorage.getItem("userType");

  if (!token || !role) return;

  const API_BASE = "http://localhost:8000/profile";

  const profileEndpoints = {
    student: `${API_BASE}/student`,
    consultant: `${API_BASE}/consultant`,
    admin: `${API_BASE}/admin`
  };

  const redirectPaths = {
    student: "student/home.html",
    consultant: "consultant/home.html",
    admin: "admin/home.html"
  };

  const endpoint = profileEndpoints[role];
  const redirectPath = redirectPaths[role];

  if (!endpoint || !redirectPath) {
    console.warn("Invalid role or endpoint config for role:", role);
    sessionStorage.clear();
    return;
  }

  try {
    const res = await fetch(endpoint, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      credentials: "include"
    });

    if (res.ok) {
      window.location.href = redirectPath;
    } else {
      sessionStorage.clear();
    }
  } catch (err) {
    console.error("Token validation failed:", err);
    sessionStorage.clear();
  }
}

// 2) Header injection
function injectHeader() {
  const userType = getUserType();
  const header = document.getElementById("dynamic-header");
  const base = userType ? `${userType}/` : ""; // e.g., "student/", "admin/"
  if (!header) return;

  let headerHTML = "";
  let signOutModal = "";

  if (userType === "student") {
    headerHTML = `
      <a href="${base}home.html" class="to_the_main"><div class="logo"><img src="images/logo.png" alt="" class="pic_logo"></div></a>
      <div class="bell-menu">
        <a href="${base}notifications.html" class="bell-div"><div class="bell-image"><img src="images/bell.png" alt="" class="pic_logo"></div></a>
        <div id="menuHamToggle">
          <input type="checkbox"><span></span><span></span><span></span>
          <ul id="mainMenu">
            <a href="${base}profile.html"><li>Profile</li></a>
            <a href="${base}appointments.html"><li>Appointments</li></a>
            <a href="${base}messages.html"><li>Messages</li></a>
            <a href="${base}support-tickets.html"><li>Support Tickets</li></a>
            <a href="${base}settings.html"><li>Settings</li></a>
            <a href="#" onclick="showSignOutModal()"><li>Sign Out</li></a>
          </ul>
        </div>
      </div>
    `;
  } else if (userType === "consultant") {
    headerHTML = `
      <a href="${base}home.html" class="to_the_main"><div class="logo"><img src="images/logo.png" alt="" class="pic_logo"></div></a>
      <div class="bell-menu">
        <a href="${base}notifications.html" class="bell-div"><div class="bell-image"><img src="images/bell.png" alt="" class="pic_logo"></div></a>
        <div id="menuHamToggle">
          <input type="checkbox"><span></span><span></span><span></span>
          <ul id="mainMenu">
            <a href="${base}profile.html"><li>Profile</li></a>
            <a href="${base}appointments.html"><li>Appointments</li></a>
            <a href="${base}messages.html"><li>Messages</li></a>
            <a href="${base}consultancy-areas.html"><li>Consultancy Areas</li></a>
            <a href="${base}timetable.html"><li>Timetable</li></a>
            <a href="${base}support-tickets.html"><li>Support Tickets</li></a>
            <a href="${base}settings.html"><li>Settings</li></a>
            <a href="#" onclick="showSignOutModal()"><li>Sign Out</li></a>
          </ul>
        </div>
      </div>
    `;
  } else if (userType === "admin") {
    headerHTML = `
      <a href="${base}home.html" class="to_the_main"><div class="logo"><img src="images/logo.png" alt="" class="pic_logo"></div></a>
      <div class="bell-menu">
        <a href="${base}notifications.html" class="bell-div"><div class="bell-image"><img src="images/bell.png" alt="" class="pic_logo"></div></a>
        <div id="menuHamToggle">
          <input type="checkbox"><span></span><span></span><span></span>
          <ul id="mainMenu">
            <a href="${base}profile.html"><li>Profile</li></a>
            <a href="${base}user-management.html"><li>User Management</li></a>
            <a href="${base}consultant-verification.html"><li>Consultant Verification</li></a>
            <a href="${base}support-tickets.html"><li>Support Tickets</li></a>
            <a href="${base}settings.html"><li>Settings</li></a>
            <a href="#" onclick="showSignOutModal()"><li>Sign Out</li></a>
          </ul>
        </div>
      </div>
    `;
  } else {
    // Guest fallback
    headerHTML = `
      <a href="/" class="to_the_main"><div class="logo"><img src="images/logo.png" alt="" class="pic_logo"></div></a>
      <div class="nav-buttons">
        <a href="log-in.html"><button class="login">Log in</button></a>
        <a href="register.html"><button class="register">Register</button></a>
      </div>
    `;
  }

  header.className = userType ? "user-header" : "";
  header.innerHTML = headerHTML;

  // Inject modal if logged in
  if (userType && !document.getElementById("signOutModal")) {
    const modalHTML = `
      <div id="signOutModal" class="modal-overlay" style="display:none;">
        <div class="modal-content">
          <p>Are you sure you want to sign out?</p>
          <div class="modal-buttons">
            <button onclick="confirmSignOut()">Yes</button>
            <button onclick="closeModal()">No</button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML("beforeend", modalHTML);
  }
}

// 3) Modal functions
function showSignOutModal() {
  document.getElementById('signOutModal').style.display = 'flex';
}
function closeModal() {
  document.getElementById('signOutModal').style.display = 'none';
}

async function confirmSignOut() {
  try {
    await fetch("http://localhost:8000/auth/logout", {
      method: "POST",
      credentials: "include", // Needed to send the refresh_token cookie
    });
  } catch (err) {
    console.warn("Logout failed:", err);
  }

  sessionStorage.clear(); // Clear access token + role info
  window.location.href = "/"; // Redirect to landing or login
}

window.confirmSignOut = confirmSignOut;


// 4) Expose
window.isLoggedIn = isLoggedIn;
window.getUserType = getUserType;
window.requireAuth = requireAuth;
window.redirectIfAuthenticated = redirectIfAuthenticated;
window.injectHeader = injectHeader;
window.showSignOutModal = showSignOutModal;
window.closeModal = closeModal;
window.confirmSignOut = confirmSignOut;
