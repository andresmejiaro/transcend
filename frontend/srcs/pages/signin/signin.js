const getUserId = async (username) => {
  try {
	const url = `${window.DJANGO_API_BASE_URL}/api/get_user_id/${username}`;
	const response = await makeRequest(true, url);

	if (response) {
	  return response.user_id;
	} else {
	  console.error("Error getting user ID:", response.message);
	  return null;
	}
  } catch (error) {
	console.error("Error getting user ID:", error.message);
	return null;
  }
};

async function validateOTP(username, token) {
  try {
	const totpCode = document.getElementById("otpLoginForm").value;
	const userID = await getUserId(username);
	const url = `${window.DJANGO_API_BASE_URL}/api/verify_totp_code/`;

	const response = await makeRequest(true, url, {
	  method: "POST",
	  headers: {
		"Content-Type": "application/json",
	  },
	  body: JSON.stringify({
		user_id: userID,
		totp_code: totpCode,
	  }),
	});

	if (response.ok) {
	  window.location.href = "/play!";
	} else {
	  console.error("Error:", response.message);
	  displayError(response.message);
	}
  } catch (error) {
	console.error("Error:", error.message);
	displayError("Error validating OTP. Please try again.");
  }
}

const handle2fA = async (username, token) => {
  var loginModal = new bootstrap.Modal(document.getElementById("loginModal"));
  loginModal.show();
  document.getElementById("checkOTP").addEventListener("click", function () {
	validateOTP(username, token);
  });
};

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
	console.log("Invalid password autho");
	return;
  }

  try {
	const url = `${window.DJANGO_API_BASE_URL}/api/user/login/`;

	const response = await makeRequest(false, url, {
	  method: "POST",
	  mode: "cors",
	  credentials: "include",
	  headers: {
		"Content-Type": "application/json",
	  },
	  body: JSON.stringify({
		username: username,
		password: password,
	  }),
	});

	if (response.status === "ok") {
	  sessionStorage.setItem("username", username);
	  sessionStorage.setItem("jwt", response.token);
	  window.location.href = "/play!";
	} else if (response.status === "2FA") {
	  handle2fA(username, response.token);
	} else {
	  console.error("Error:", response.message);
	  displayError(response.message);
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

document
  .getElementById("usernameLoginForm")
  .addEventListener("input", validateUsername);
const passwordInput = document.getElementById("password");
const passwordHelp = document.getElementById("passwordHelp");

const form = document.getElementById("loginForm");
form.addEventListener(
  "submit",
  function (event) {
	event.preventDefault();
	if (!validateUsername()) return;
	tryFormPost();
  },
  false
);

document
  .getElementById("togglePassword")
  .addEventListener("click", function () {
	togglePassword();
  });

function togglePassword() {
  var passwordInput = document.getElementById("password");
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
