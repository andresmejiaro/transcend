function validateUsername() {
  const usernameInput = document.getElementById("usernameSignupForm");
  const usernameHelp = document.getElementById("usernameHelp");
  const username = usernameInput.value;

  const maxCharLimit = 20; // Set the maximum character limit

  if (username.length < 4) {
    usernameHelp.innerText = "Username must be at least 4 characters";
    usernameInput.classList.add("is-invalid");
    usernameInput.classList.remove("is-valid");
    return false;
  } else if (username.length > maxCharLimit) {
    usernameHelp.innerText = `Username cannot exceed ${maxCharLimit} characters`;
    usernameInput.classList.add("is-invalid");
    usernameInput.classList.remove("is-valid");
    return false;
  } else {
    usernameHelp.innerText = "";
    usernameInput.classList.remove("is-invalid");
    usernameInput.classList.add("is-valid");
    return true;
  }
}

// Validation function for fullname
function validateFullname() {
  const fullnameInput = document.getElementById("fullname");
  const fullnameHelp = document.getElementById("fullnameHelp");
  const fullname = fullnameInput.value;

  const maxCharLimit = 20; // Set the maximum character limit

  if (fullname.length < 4) {
    fullnameHelp.innerText = "Fullname must be at least 4 characters";
    fullnameInput.classList.add("is-invalid");
    fullnameInput.classList.remove("is-valid");
    return false;
  } else if (fullname.length > maxCharLimit) {
    fullnameHelp.innerText = `Fullname cannot exceed ${maxCharLimit} characters`;
    fullnameInput.classList.add("is-invalid");
    fullnameInput.classList.remove("is-valid");
    return false;
  } else {
    fullnameHelp.innerText = "";
    fullnameInput.classList.remove("is-invalid");
    fullnameInput.classList.add("is-valid");
    return true;
  }
}

// Validation function for email
function validateEmail() {
  const emailInput = document.getElementById("email");
  const emailHelp = document.getElementById("emailHelp");
  const email = emailInput.value;

  // You can add more sophisticated email validation logic here
  if (!email.includes("@")) {
    emailHelp.innerText = "Invalid email address";
    emailInput.classList.add("is-invalid");
    emailInput.classList.remove("is-valid");
    return false;
  } else {
    emailHelp.innerText = "";
    emailInput.classList.remove("is-invalid");
    emailInput.classList.add("is-valid");
    return true;
  }
}

// Event listeners for input validation
document
  .getElementById("usernameSignupForm")
  .addEventListener("input", validateUsername);
document.getElementById("fullname").addEventListener("input", validateFullname);
document.getElementById("email").addEventListener("input", validateEmail);

const passwordInput = document.getElementById("passwordSignup");
const confirmPasswordInput = document.getElementById("confirmPasswordSignup");
const passwordHelp = document.getElementById("passwordHelpSignup");
const confirmPasswordHelp = document.getElementById(
  "confirmPasswordHelpSignup"
);

function checkPasswordStrength(password) {
  if (password.length >= 8) return true;
  else return false;
}

function validatePassword() {
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  if (!checkPasswordStrength(password)) {
    passwordHelp.innerText = "Expected 8 or more characters";
    passwordInput.classList.add("is-invalid");
    passwordInput.classList.remove("is-valid");
  } else {
    passwordInput.classList.remove("is-invalid");
    passwordInput.classList.add("is-valid");
    passwordHelp.innerText = "";
  }

  if (password !== confirmPassword) {
    confirmPasswordHelp.innerText = "Passwords do not match";
    return false;
  } else {
    confirmPasswordHelp.innerText = "";
    return true;
  }
}

// Validation function for confirm password
function validateConfirmPassword() {
  const confirmPassword = confirmPasswordInput.value;
  const password = passwordInput.value;

  if (confirmPassword !== password) {
    confirmPasswordHelp.innerText = "Passwords do not match";
    confirmPasswordInput.classList.add("is-invalid");
    confirmPasswordInput.classList.remove("is-valid");
    return false;
  } else {
    confirmPasswordInput.classList.remove("is-invalid");
    confirmPasswordInput.classList.add("is-valid");
    confirmPasswordHelp.innerText = "";
    return true;
  }
}

// Event listeners for input validation
document
  .getElementById("passwordSignup")
  .addEventListener("input", validatePassword);
document
  .getElementById("confirmPasswordSignup")
  .addEventListener("input", validateConfirmPassword);

const tryFormPost = async () => {
  const username = document.getElementById("usernameSignupForm").value;
  const fullname = document.getElementById("fullname").value;
  const password = document.getElementById("passwordSignup").value;
  const email = document.getElementById("email").value;

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/signup/`;

    const response = await makeRequest(false, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        fullname: fullname,
        email: email,
        password: password,
      }),
    });
    if (response.status === "ok") {
      sessionStorage.setItem("jwt", response.token);
      window.location.href = "/otp";
    } else {
      console.error("Error:", response.message);
      displayError(`${response.message}. Please try again.`);
    }
  } catch (error) {
    console.error("Error:", error.message);
    displayError("Invalid credentials. Please try again.");
  }
};

function displayError(message) {
  const errorAlert = document.getElementById("errorAlert");
  errorAlert.textContent = message;
  errorAlert.style.display = "block";
}

const form = document.getElementById("signupForm");
form.addEventListener(
  "submit",
  function (event) {
    event.preventDefault();
    if (
      !validateUsername() ||
      !validateFullname() ||
      !validateEmail() ||
      !validatePassword() ||
      !validateConfirmPassword()
    ) {
      return;
    }
    tryFormPost();
  },
  false
);

document
  .getElementById("togglePassword")
  .addEventListener("click", function () {
    togglePassword();
  });

document
  .getElementById("toggleRePassword")
  .addEventListener("click", function () {
    toggleRePassword();
  });

function togglePassword() {
  var passwordInput = document.getElementById("passwordSignup");
  var eyeIcon = document.getElementById("togglePassword");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeIcon.classList.remove("bi-eye");
    eyeIcon.classList.add("bi-eye-slash");
  } else {
    passwordInput.type = "password";
    eyeIcon.classList.remove("bi-eye-slash");
    eyeIcon.classList.add("bi-eye");
  }
}

function toggleRePassword() {
  var passwordInput = document.getElementById("confirmPasswordSignup");
  var eyeIcon = document.getElementById("toggleRePassword");

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    eyeIcon.classList.remove("bi-eye");
    eyeIcon.classList.add("bi-eye-slash");
  } else {
    passwordInput.type = "password";
    eyeIcon.classList.remove("bi-eye-slash");
    eyeIcon.classList.add("bi-eye");
  }
}