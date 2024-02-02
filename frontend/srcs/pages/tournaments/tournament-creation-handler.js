const createRequest = async () => {
	const name = document.getElementById("nameTournament").value;
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/tournament/create/`;
		const options = {
			method: "POST",
			mode: "cors",
			credentials: "include",
			body: JSON.stringify({
				name: name,
			}),
		};

		const data = await makeRequest(true, url, options, "");
		if (data.status == "ok") {
			// window.location = `/tournament?id=${tournamentId}`
			getListofTournaments();
			addEventListenerButtons();
		}
	} catch (error) {
		console.log(error);
	}
};

const form = document.getElementById("createTornForm");

form.addEventListener("submit", function (event) {
	event.preventDefault();
	console.log("From submitted!");
	let closeButton = document.querySelector("#exampleModal .close-modal");
	closeButton.click();
	createRequest();
});
