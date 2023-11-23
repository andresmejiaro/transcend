
function validateUsername() {
  const usernameInput = document.getElementById("usernameLoginForm");
  const usernameHelp = document.getElementById("usernameHelp");
  const username = usernameInput.value;

  if (username.length < 4) {
    usernameHelp.innerText = "Write at least 4 characters";
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

function checkPasswordStrength(password) {
  if (password.length >= 8) return true;
  else return false;
}

function validatePassword() {
  const password = passwordInput.value;

  if (!checkPasswordStrength(password)) {
    passwordHelp.innerText = "Expected 8 or more characters";
    passwordInput.classList.add("is-invalid");
    passwordInput.classList.remove("is-valid");
  } else {
    passwordInput.classList.remove("is-invalid");
    passwordInput.classList.add("is-valid");
  }
}

const tryFormPost = async () => {
  const username = document.getElementById("usernameLoginForm").value;
  const password = document.getElementById("password").value;
  const placeholderPassword = "AUTH0_USER_NO_PASSWORD";
  if (password == placeholderPassword) {
    console.log("invalid password autho");
    return;
  }
  try {
    const token = await getCsrfToken();
    const response = await fetch("http://localhost:8000/api/user/login/", {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": token,
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    if (data.status === "ok") {
      sessionStorage.setItem("username", username);
      sessionStorage.setItem("jwt", data.token);
      window.location.href = "/home";
    } else {
      console.error("Error:", data.message);
      displayError(data.message);
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

document.getElementById("usernameLoginForm").addEventListener("input", validateUsername);
const passwordInput = document.getElementById("password");
const passwordHelp = document.getElementById("passwordHelp");

const form = document.getElementById("loginForm");
form.addEventListener("submit", function (event) {
  event.preventDefault();
  console.log("HELO")
  if (!validateUsername())
    return;
  tryFormPost();
}, false);


document.getElementById('togglePassword').addEventListener('click', function () {
  togglePassword();
});

function togglePassword() {
  var passwordInput = document.getElementById('password');
  var eyeIcon = document.getElementById('togglePassword');
  
  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    eyeIcon.classList.remove('bi-eye');
    eyeIcon.classList.add('bi-eye-slash');
  } else {
    passwordInput.type = 'password';
    eyeIcon.classList.remove('bi-eye-slash');
    eyeIcon.classList.add('bi-eye');
  }
}
