document.getElementById("admin-login-form").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent default form submission behavior
  
    // Get input values
    const adminId = document.getElementById("admin-id").value.trim();
    const password = document.getElementById("password").value;
    const loginStatus = document.getElementById("login-status");
  
    // Validate Admin ID (4 digits)
    const isAdminIdValid = /^\d{4}$/.test(adminId);
  
    // Validate Password (alphanumeric)
    const isPasswordValid = /^[a-zA-Z0-9]+$/.test(password);
  
    // Display appropriate validation messages
    if (!isAdminIdValid) {
      loginStatus.textContent = "Admin ID must be 4 digits.";
      loginStatus.style.color = "red";
      return;
    }
    if (!isPasswordValid) {
      loginStatus.textContent = "Password must be alphanumeric.";
      loginStatus.style.color = "red";
      return;
    }
  
    // Redirect to admin.html without restrictions
    loginStatus.textContent = "Login successful! Redirecting...";
    loginStatus.style.color = "green";
  
    setTimeout(() => {
      window.location.href = "ad_home.html"; // Redirect to admin page
    }, 1500); // Delay for success message display
  });
  