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
	}
};

getMeSettingsInfo();
