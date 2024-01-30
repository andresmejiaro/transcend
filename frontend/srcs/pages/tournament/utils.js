const changeTournamentName = async (name) => {
  const tournamentName = document.getElementById("tournament-name");
  tournamentName.innerHTML = `Name: ${name}`;
};

const changeTournamentRound = (round) => {
  const tournamentRound = document.getElementById("tournament-round");
  tournamentRound.innerHTML = `round: ${round}`;
};

const changeTournamentStatus = (winner) => {
  const tournamentStatus = document.getElementById("tournament-status");
  if (winner) {
    const winnerHeading = document.createElement("h2");
    const statusAdminHeading = document.createElement("h2");

    winnerHeading.textContent = `Winner: ${winner}`;
    statusAdminHeading.textContent = "Tournament Ended";

    tournamentStatus.appendChild(winnerHeading);
    tournamentStatus.appendChild(statusAdminHeading);
  } else {
    const statusAdminHeading = document.createElement("h2");
    statusAdminHeading.classList.add = "text-white";
    statusAdminHeading.textContent = `waiting to start next round..`;
    tournamentStatus.appendChild(statusAdminHeading);
  }
};

const changeParticipants = async (players) => {
    let listParticipantsDiv = document.getElementById("list-participants");

	listParticipantsDiv.innerHTML = '';
	// listParticipantsDiv.querySelectorAll('*').forEach(n => n.remove());
	// while (listParticipantsDiv.firstChild) {
    //     listParticipantsDiv.removeChild(listParticipantsDiv.firstChild);
    // }
	
	for (const player of players) {
        const playerData = await getPlayerInfo(player.id);
        let listItem = document.createElement("div");
        listItem.className = "list-group-item";
        listItem.textContent = playerData.username;
        listParticipantsDiv.appendChild(listItem);
    }
};

