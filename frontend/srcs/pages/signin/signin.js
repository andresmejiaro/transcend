async function validateOTP(username, userId, jwt) {
	try {
		const totpCode = document.getElementById("otpLoginForm").value;
		const url = `${window.DJANGO_API_BASE_URL}/api/verify_totp_code/`;

		const response = await makeRequest(false, url, {
			method: "POST",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				user_id: userId,
				totp_code: totpCode,
			}),
		});

		if (response.status == "ok") {
			sessionStorage.setItem("jwt", response.token);
			window.location.href = "/play!";
		} else {
			displayGAError(response.message);
		}
	} catch (error) {
		console.error("Error:", error.message);
		displayGAError("Error validating OTP. Please try again.");
	}
}

const handle2fA = async (username, userId) => {
	var loginModal = new bootstrap.Modal(document.getElementById("loginModal"));
	loginModal.show();
	document.getElementById("checkOTP").addEventListener("click", function () {
		validateOTP(username, userId);
	});
};

function validateUsername() {
	const usernameInput = document.getElementById("usernameLoginForm");
	const usernameHelp = document.getElementById("usernameHelp");
	const username = usernameInput.value;

	const maxCharLimit = 20;

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
			sessionStorage.setItem("jwt", response.token);
			window.location.href = "/play!";
		} else if (response.status === "2FA") {
			handle2fA(username, response.user_id);
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

function displayGAError(message) {
	const errorAlert = document.getElementById("errorGaAlert");
	errorAlert.textContent = message;
	errorAlert.style.display = "block";
}

document.getElementById("usernameLoginForm").addEventListener("input", validateUsername);
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

document.getElementById("togglePassword").addEventListener("click", function () {
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
