const loginForm = document.getElementById('login-form');
const loginStatus = document.getElementById('login-status');

loginForm.addEventListener('submit', (event) => {
  event.preventDefault(); // Prevent default form submission

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // Example hardcoded credentials for demo purposes
  const validCredentials = {
    "1234": "password123",
    "5678": "mypassword"
  };

  // Check if credentials are valid
  if (validCredentials[username] && validCredentials[username] === password) {
    loginStatus.style.color = "green";
    loginStatus.textContent = "Login successful!";
    // Redirect to attendance dashboard (replace with your dashboard URL)
    setTimeout(() => {
      window.location.href = "dashboard.html";
    }, 1500);
  } else {
    loginStatus.style.color = "red";
    loginStatus.textContent = "Invalid Employee ID or Password.";
  }
});
