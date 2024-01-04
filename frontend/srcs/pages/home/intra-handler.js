function showButtons() {
	setTimeout(function () {
		document.getElementById("home-div").style.opacity = "1";
	}, 1000);
}

let buttonIntra = document.getElementById("intra");

const handleIntraAuth = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/oauth-init/`;

		const options = {
			method: "GET",
		};

		const data = await makeRequest(false, url, options);
		if (data) {
			window.location.href = data.url;
		}
	} catch (error) {
		console.error("Error:", error.message);
	}
};

buttonIntra.addEventListener("click", function (event) {
	event.preventDefault();
	handleIntraAuth();
});
