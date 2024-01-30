const loadGoogleAuthSettings = async () => {
	document.getElementById("gaDiv").style.display = "block";
	await enable2FA();
	await load2FA();
};

let startGAClicked = false;

document.getElementById("startGA").addEventListener("click", function (e) {
	e.preventDefault();
	loadGoogleAuthSettings();
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

const handleVerifyTotpProfileSettings = async () => {
	const res = await verifyTOTP();
	if (res) {
		setTimeout(function () {
			handleGoogleAuthActivated();
		}, 1000);
	}
};

document.getElementById("totpForm").addEventListener("submit", function (event) {
	event.preventDefault();
	handleVerifyTotpProfileSettings();
});
