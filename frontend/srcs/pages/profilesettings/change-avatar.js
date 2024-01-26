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
