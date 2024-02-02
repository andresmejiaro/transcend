function validateUsername() {
	const usernameInput = document.getElementById("userSettingsUsername");
	const usernameHelp = document.getElementById("userSettingsUsernameHelp");
	const username = usernameInput.value;

	const maxCharLimit = 20;

	if (username.length == 0) {
		return true;
	} else if (username.length < 4) {
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

function validateFullname() {
	const fullnameInput = document.getElementById("userSettingsFullname");
	const fullnameHelp = document.getElementById("userSettingsFullnameHelp");
	const fullname = fullnameInput.value;

	const maxCharLimit = 20;

	if (fullname.length == 0) {
		return true;
	} else if (fullname.length < 4) {
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

function validateEmail() {
	const emailInput = document.getElementById("userSettingsEmail");
	const emailHelp = document.getElementById("userSettingsEmailHelp");
	const email = emailInput.value;

	if (email.length == 0) {
		return true;
	} else if (!email.includes("@")) {
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

const userEditInfo = async () => {
	const usernameElement = document.getElementById("userSettingsUsername");
	const fullnameElement = document.getElementById("userSettingsFullname");
	const emailElement = document.getElementById("userSettingsEmail");

	const username = usernameElement.value;
	const fullname = fullnameElement.value;
	const email = emailElement.value;

	const requestBody = {
		...(username && { username }),
		...(fullname && { fullname }),
		...(email && { email }),
	};

	if (Object.keys(requestBody).length === 0) {
		console.log("No user input");
		return;
	}

	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/user/update/`;
		const response = await makeRequest(true, url, {
			method: "PUT",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(requestBody),
		});


		if (response.status === "ok") {
			sessionStorage.setItem("jwt", response.token);
		}
		if (response.message && response.message === "Something went wrong") {
			// TODO: show better message
			showAlertDanger(response.message);
		}
	} catch (error) {
		console.error("Error:", error.message);
		//displayError("Invalid credentials. Please try again.");
	}
};

const form = document.getElementById("userSettingForm");
form.addEventListener(
	"submit",
	function (event) {
		event.preventDefault();
		if (!validateUsername() || !validateFullname() || !validateEmail()) {
			return;
		}
		userEditInfo();
	},
	false
);
z