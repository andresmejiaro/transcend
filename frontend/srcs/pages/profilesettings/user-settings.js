document.getElementById("updateAvatarForm").addEventListener(
	"submit",
	function (e) {
		e.preventDefault();
		changeAvatar();
	},
	false
);

const changeAvatar = async () => {
	const avatarInput = document.getElementById("avatar");
	const username = sessionStorage.getItem("username");

	if (!username) {
		console.log("username not found");
		return;
	}

	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/user/update-avatar/`;

		const formData = new FormData();
		formData.append("avatar", avatarInput.files[0]);

		const options = {
			method: "POST",
			mode: "cors",
			credentials: "include",
			body: formData,
		};

		const response = await makeRequest(true, url, options);

		const msg = document.getElementById("avatarMsg");

		if (response.status === "ok") {
			msg.innerText = response.message;
			msg.classList.add("text-success");
			setTimeout(function () {
				location.reload();
			}, 1000);
		} else {
			msg.innerText = response.error;
			msg.classList.add("text-error");
		}
	} catch (error) {
		console.error("Error:", error.message);
	}
};

const getMeSettingsInfo = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/user/info-me/`;

		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const data = await makeRequest(true, url, options);

		if (data.status === "ok") {
			const usernameElement = document.getElementById("userSettingsUsername");
			const fullnameElement = document.getElementById("userSettingsFullname");
			const emailElement = document.getElementById("userSettingsEmail");
			const avatarImage = document.getElementById("avatarImageUserSettings");

			usernameElement.placeholder = data.user.username;
			fullnameElement.placeholder = data.user.fullname;
			emailElement.placeholder = data.user.email;

			if (data.user.avatar_url) {
				const completeAvatarUrl = `${window.DJANGO_API_BASE_URL}${data.user.avatar_url}`;
				avatarImage.src = completeAvatarUrl;
			}
		}
	} catch (error) {
		console.error("Error:", error.message);
		// Handle error actions, e.g., display an error message
	}
};

getMeSettingsInfo();

const loadGoogleAuth = async () => {
	document.getElementById("gaDiv").style.display = "block";
	await enable2FA();
	await load2FA();
};

let startGAClicked = false;

document.getElementById("startGA").addEventListener("click", function (e) {
	e.preventDefault();
	loadGoogleAuth();
	document.getElementById("removeGA").style.display = "block";
	document.getElementById("startGA").style.display = "none";
});

const removeGA = async () => {
	document.getElementById("gaDiv").style.display = "none";
	await disable2FA();
	startGAClicked = false;
};

document.getElementById("removeGA").addEventListener("click", function (e) {
	e.preventDefault();
	removeGA();
	document.getElementById("removeGA").style.display = "none";
	document.getElementById("startGA").style.display = "block";
});

const handleGoogleAuthActivated = async () => {
	document.getElementById("div-ga-active").style.display = "block";
	document.getElementById("div-ga-not-active").style.display = "none";
};

const removeGaA = async () => {
	await removeGA();
	document.getElementById("div-ga-active").style.display = "none";
	document.getElementById("div-ga-not-active").style.display = "block";
	showAlertDanger("GA removed succesfully");
};

document.getElementById("removeGAActive").addEventListener("click", function (e) {
	e.preventDefault();
	removeGaA();
});

const checkIfGoogleAuthActivated = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/is_2fa_setup_complete/`;

		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const data = await makeRequest(true, url, options);
		if (data.status) handleGoogleAuthActivated();
	} catch (error) {
		console.error(error);
	}
};

checkIfGoogleAuthActivated();
