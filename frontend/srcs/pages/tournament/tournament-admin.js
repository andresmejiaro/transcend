// const startNextRound = document.getElementById("start-round-btn");
// startNextRound.addEventListener("click", function () {
// 	sendTorSocketMessage("command", {
// 		command: "start_round",
// 		data: {},
// 	});
// });

function showTournamentAdmin(canStartMatches, data) {
	let tournamentAdminDiv = document.getElementById("tournament-admin");
	if (tournamentAdminDiv) {
		tournamentAdminDiv.classList.remove("d-none");
		tournamentAdminDiv.classList.add("d-block");
	}

	if (!canStartMatches && !data.winner) {
		document.getElementById("status-admin").innerHTML = "Waiting for players...";
		startNextRound.disabled = true;
	}

	if (canStartMatches) {
		document.getElementById("status-admin").innerHTML = "Starting tournament, wait!";
		startNextRound.disabled = false;
	}

	if (data.winner) {
		document.getElementById("status-admin").innerHTML = "No ADMIN, tournament ended";
	}
}
