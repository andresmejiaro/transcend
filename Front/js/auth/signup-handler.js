const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirmPassword");
const passwordHelp = document.getElementById("passwordHelp");
const confirmPasswordHelp = document.getElementById("confirmPasswordHelp");

function validatePassword() {
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  const passwordStrength = checkPasswordStrength(password);
  passwordHelp.innerText = `Password Strength: ${passwordStrength}`;

  if (password !== confirmPassword) {
    confirmPasswordHelp.innerText = "Passwords do not match";
    return false;
  } else {
    confirmPasswordHelp.innerText = "";
    return true;
  }
}

function checkPasswordStrength(password) {
  if (password.length >= 8) {
    return "Strong";
  } else {
    return "Weak";
  }
}

passwordInput.addEventListener("input", validatePassword);
confirmPasswordInput.addEventListener("input", validatePassword);

const tryFormPost = async () => {
  const username = document.getElementById("usernameSignupForm").value;
  const fullname = document.getElementById("fullname").value;
  const password = document.getElementById("password").value;

  token = await getCsrfToken();

  fetch("http://localhost:8000/api/user/signup/", {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({
      username: username,
      fullname: fullname,
      password: password,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "ok") {
        sessionStorage.setItem("username", username);
        sessionStorage.setItem("jwt", data.token);
        window.location.href = "/home";
      } else {
        console.error("Error:", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

const form = document.getElementById("signupForm");
form.addEventListener("submit", function (event) {
  event.preventDefault();
  if (!validatePassword()) {
    return;
  }
  tryFormPost();
});
