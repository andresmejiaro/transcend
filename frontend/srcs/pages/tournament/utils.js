const changeTournamentName = async (name) => {
	const tournamentName = document.getElementById("tournament-name");
	const displayName = name.length > 17 ? name.substring(0, 17) + "..." : name;
	tournamentName.innerHTML = `${displayName}`;
};

const changeTournamentRound = (round) => {
	const tournamentRound = document.getElementById("tournament-round");
	tournamentRound.innerHTML = `round: ${round}`;
};

const changeTournamentStatus = (winner, canStartMatches) => {
	const tournamentStatus = document.getElementById("tournament-status");
	if (winner) {
		const winnerHeading = document.createElement("h2");
		const statusAdminHeading = document.createElement("h2");

		winnerHeading.textContent = `Winner: ${winner}`;
		statusAdminHeading.textContent = "Tournament Ended";

		tournamentStatus.appendChild(winnerHeading);
		tournamentStatus.appendChild(statusAdminHeading);
	} else {
		const tournamentStatusText = document.getElementById("tournament-status-t");
		if (canStartMatches) tournamentStatusText.innerHTML = `waiting to start next round..`;
		else tournamentStatusText.innerHTML = `Waiting for players..`;
	}
};

const changeParticipants = async (players) => {
	const tournamentRoundDiv = document.getElementById("tournament-first-round");
	tournamentRoundDiv.innerHTML = "";

	if (players.length % 2 !== 0) {
		for (const player of players) {
			const playerData = await getPlayerInfo(player.id);
			let listItem = document.createElement("div");
			listItem.className = "list-group-item";
			listItem.textContent = playerData.username;
			tournamentRoundDiv.appendChild(listItem);
		}
	} else {
		for (let i = 0; i < players.length - 1; i += 2) {
			const player1Data = await getPlayerInfo(players[i].id);
			let player2Data;
			if (players[i + 1]) player2Data = await getPlayerInfo(players[i + 1].id);
			else player2Data.username = "Waiting...";

			const matchDiv = document.createElement("div");
			matchDiv.className = "match";

			const player1Div = document.createElement("div");
			player1Div.className = "player";
			player1Div.id = `player${i + 1}tor`;
			player1Div.textContent = player1Data.username;

			const player2Div = document.createElement("div");
			player2Div.className = "player";
			player2Div.id = `player${i + 2}tor`;
			player2Div.textContent = player2Data.username;

			matchDiv.appendChild(player1Div);
			matchDiv.appendChild(player2Div);

			tournamentRoundDiv.appendChild(matchDiv);
		}
	}
};

const showSecondTorTable = async (players) => {
	const tournamentRoundDiv = document.getElementById("tournament-second-round");
	tournamentRoundDiv.innerHTML = "";

	for (let i = 0; i < players.length - 1; i += 2) {
		const player1Data = await getPlayerInfo(players[i].id);
		const player2Data = await getPlayerInfo(players[i + 1].id);

		const matchDiv = document.createElement("div");
		matchDiv.className = "match";

		const player1Div = document.createElement("div");
		player1Div.className = "player";
		player1Div.id = `player${i + 1}tor`;
		player1Div.textContent = player1Data.username;

		const player2Div = document.createElement("div");
		player2Div.className = "player";
		player2Div.id = `player${i + 2}tor`;
		player2Div.textContent = player2Data.username;

		matchDiv.appendChild(player1Div);
		matchDiv.appendChild(player2Div);

		tournamentRoundDiv.appendChild(matchDiv);
	}
};

const showlastTorTable = async (players) => {
    const tournamentRoundDiv = document.getElementById("tournament-winner-round");
    tournamentRoundDiv.innerHTML = "";
    const player = players[0];

    const matchDiv = document.createElement("div");
    matchDiv.className = "match";

    const player1Div = document.createElement("div");
    player1Div.className = "player";
    player1Div.textContent = player.username;

    const crownEmojiBefore = document.createElement("span");
    crownEmojiBefore.textContent = "👑 "; // Emoji de corona antes del nombre

    const crownEmojiAfter = document.createElement("span");
    crownEmojiAfter.textContent = " 👑"; // Emoji de corona después del nombre

    player1Div.prepend(crownEmojiBefore); // Agrega la corona antes del nombre del jugador
    player1Div.appendChild(crownEmojiAfter); // Agrega la corona después del nombre del jugador

    matchDiv.appendChild(player1Div);
    tournamentRoundDiv.appendChild(matchDiv);
};
