document.getElementById('employee-login-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent default form submission behavior
  
    // Get input values
    const employeeId = document.getElementById('employee-id').value.trim();
    const password = document.getElementById('password').value;
  
    // Validate Employee ID (4 digits)
    const isEmployeeIdValid = /^\d{4}$/.test(employeeId);
  
    // Validate Password (alphanumeric)
    const isPasswordValid = /^[a-zA-Z0-9]+$/.test(password);
  
    const loginStatus = document.getElementById('login-status');
  
    // Check validation and display appropriate message
    if (!isEmployeeIdValid) {
      loginStatus.textContent = "Employee ID must be 4 digits.";
      loginStatus.style.color = "red";
      return;
    }
    if (!isPasswordValid) {
      loginStatus.textContent = "Password must be alphanumeric.";
      loginStatus.style.color = "red";
      return;
    }
  
    // Allow redirection to home.html regardless of inputs
    loginStatus.textContent = "Login successful! Redirecting...";
    loginStatus.style.color = "green";
  
    setTimeout(() => {
      window.location.href = "home.html"; // Redirect to home page
    }, 1500); // Delay to show the success message
    
  });
  