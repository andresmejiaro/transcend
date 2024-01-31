const startNextRound = document.getElementById("start-round-btn");
startNextRound.addEventListener("click", function () {
	sendTorSocketMessage("command", {
		command: "start_round",
		data: {},
	});
});

function showTournamentAdmin(canStartMatches, data) {
	let tournamentAdminDiv = document.getElementById("tournament-admin");
	if (tournamentAdminDiv) {
		tournamentAdminDiv.classList.remove("d-none");
		tournamentAdminDiv.classList.add("d-block");
	}

	if (!canStartMatches && !data.winner) {
		document.getElementById("status-admin").innerHTML = "Waiting to be 4 players to be able to start the tournament";
		startNextRound.disabled = true;
	}

	if (canStartMatches) {
		document.getElementById("status-admin").innerHTML = "On your click, tournament starts";
		startNextRound.disabled = false;
	}

	if (data.winner) {
		document.getElementById("status-admin").innerHTML = "No ADMIN, tournament ended";
	}
}
