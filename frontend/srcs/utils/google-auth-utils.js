const load2FA = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/display_qr_code/`;
		const response = await makeRequest(true, url, {
			method: "GET",
			mode: "cors",
			credentials: "include",
		});
		if (response) {
			document.getElementById("qrcodeImage").src = `${window.DJANGO_API_BASE_URL}/${response.qrcode_path}`;
		} else {
			console.error("Error loading 2FA:", response.message);
		}
	} catch (error) {
		console.error("Error loading 2FA:", error.message);
	}
};

async function verifyTOTP() {
	const totpCode = document.getElementById("totpCode").value;
	const id = await getUserId();

	if (id == null) return;

	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/verify_totp_code/`;
		const response = await makeRequest(true, url, {
			method: "POST",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
			},
			body: JSON.stringify({
				user_id: id,
				totp_code: totpCode,
			}),
		});

		const status = response.status;
		const statusTotp = document.getElementById("statusMessage");
		statusTotp.innerText = response.message;
		if (status == "error") {
			statusTotp.style.color = "red";
			return false;
		} else {
			statusTotp.style.color = "green";
			return true;
		}
	} catch (error) {
		console.error("Error verifying TOTP:", error.message);
	}
}

async function enable2FA() {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/enable_2fa/`;
		const response = await makeRequest(true, url, {
			method: "POST",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
			},
		});

		if (response.success) {
			document.getElementById("qrcodeImage").src = `${window.DJANGO_API_BASE_URL}/${response.qrcode_path}`;
			document.getElementById("statusMessage").innerText = response.success;
		}
		// return response;
	} catch (error) {
		console.error("Error enabling 2FA:", error.message);
	}
}

async function disable2FA() {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/disable_2fa/`;
		const response = await makeRequest(true, url, {
			method: "POST",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/x-www-form-urlencoded",
			},
		});

		document.getElementById("statusMessage").innerText = response.message;
	} catch (error) {
		console.error("Error disabling 2FA:", error.message);
	}
}
