const startNextRound = document.getElementById("start-round-btn");
startNextRound.addEventListener("click", function () {
	sendTorSocketMessage("command", {
		command: "start_round",
		data: {},
	});
});

function showTournamentAdmin(data) {
	let tournamentAdminDiv = document.getElementById("tournament-admin");
	if (tournamentAdminDiv) {
		tournamentAdminDiv.classList.remove("d-none");
		tournamentAdminDiv.classList.add("d-block");
	}

	if (data.winner) {
		document.getElementById("status-admin").innerHTML = "No ADMIN, tournament ended";
	}
}
