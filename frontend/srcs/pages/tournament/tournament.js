
const urlParams = new URLSearchParams(window.location.search);
const tournamentId = urlParams.get('id');

const getTournamentInfo = async (tournamentId) => {
	const url = `http://localhost:8000/api/tournament/${tournamentId}/`;
	const options = {
	  method: "GET",
	  mode: "cors",
	  credentials: "include",
	};
  
	try {
	  const data = await makeRequest(true, url, options, "");
	  console.log(data)
	  if (data.status == "ok") {
		const tournamentName = document.getElementById("tournament-name");
		tournamentName.innerHTML = 	`Name: ${data.data.name}`;

		const tournamentRound = document.getElementById("tournament-round");
		tournamentRound.innerHTML = `round: ${data.data.round}`;

		const tournamentStatus = document.getElementById("tournament-status");
		if (data.data.winner !== null) {
			const winnerHeading = document.createElement("h2");
			const statusAdminHeading = document.createElement("h2");

			winnerHeading.textContent = `Winner: ${data.data.winner}`;
			statusAdminHeading.textContent = "Tournament Ended";
			
			tournamentStatus.appendChild(winnerHeading);
			tournamentStatus.appendChild(statusAdminHeading);
		} else {
			const statusAdminHeading = document.createElement("h2");
			statusAdminHeading.classList.add = "text-white"
			statusAdminHeading.textContent = `waiting to start next round..`;
			tournamentStatus.appendChild(statusAdminHeading);
		}

		let listParticipantsDiv = document.getElementById("list-participants");
		data.data.players.forEach(function(name) {
			let listItem = document.createElement("div");
			listItem.className = "list-group-item";
			listItem.textContent = name;
			listParticipantsDiv.appendChild(listItem);
		});	

		const userId = await getUserId();
		if (data.data.tournament_admin == userId) {
			showTournamentAdmin(data.data);
		}
	  }
	} catch (error) {
	  console.log(error);
	}
  }

getTournamentInfo(tournamentId);