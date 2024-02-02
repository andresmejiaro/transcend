let torSocket;

const connectWebSocketTor = async () => {
	const authToken = sessionStorage.getItem("jwt");

	return new Promise((resolve, reject) => {
		const uri = `${window.DAPHNE_BASE_URL}/ws/tournament/${tournamentId}/?token=${authToken}`;
		torSocket = new WebSocket(uri);

		torSocket.addEventListener("open", (event) => {
			console.log("WebSocket connection opened:", event);
			resolve(torSocket);
		});

		torSocket.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);

			if (data.type === "message") {
				console.log(data);
			}
		});

		torSocket.addEventListener("close", (event) => {
			console.log("WebSocket connection closed:", event);
			reject(new Error("WebSocket connection closed."));
		});

		torSocket.addEventListener("error", (event) => {
			console.error("WebSocket error:", event);
			reject(new Error("WebSocket connection error."));
			window.location.href = '/play!'
		});
	});
};

const sendTorSocketMessage = async (messageType, payload) => {
	const sleep = (duration) => new Promise((resolve) => setTimeout(resolve, duration));

	// Loop until the WebSocket is open
	while (!torSocket || torSocket.readyState !== WebSocket.OPEN) {
		// Wait for a short period before checking again
		await sleep(50);
	}

	return new Promise((resolve, reject) => {
		if (torSocket && torSocket.readyState === WebSocket.OPEN) {
			torSocket.send(
				JSON.stringify({
					type: messageType,
					...payload,
				})
			);
			resolve();
		} else {
			console.error("WebSocket is not in the OPEN state.");
			reject(new Error("WebSocket is not open"));
		}
	});
};

const getInfo = async (tournamentId) => {
	try {
		await connectWebSocketTor(tournamentId);

		torSocket.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);
			handleTorData(data);
		});

		// sendWebSocketMessage('command', { command: 'get_website_group_list', data: {} });
	} catch (error) {
		console.error("Error while connecting to WebSocket:", error.message);
	}
};

const handleTorData = async (data) => {
	let canStartMatches = 0;

	console.log("Tor WebSocket message received:", data);

	if (data.type == "new_player") handleNewPlayer(data.data.players);
	else if (data.type == "player_joined") {
		handleNewPlayer(data.data.registered_players);
		changeTournamentName(data.data.tournament_name);
	} else if (data.type == "tournament_ready") {
		canStartMatches = 1;
		// handleNewPlayer(data.data.registered_players);
	} else if (data.type == "matchmaking_info") {
		await handleMatchmakingTor(data.data);
	} else if (data.type == "matches_finished") {
		leaveTorMatch();
		const playersss = data.data.registered_players;
		console.log(playersss)
		console.log(playersss.length)
		if (playersss.length >= 2)
			showSecondTorTable(playersss);
		else
			showlastTorTable(playersss);
	}
	else if (data.type == "match_finished") {
		console.log(data)
	} else if (data.type == "tournament_ended") {
		handleTournamentFinished(data.data.tournament_winner);
	} else if (data.type === "player_disconnected") {
		const sleep = (duration) => new Promise(resolve => setTimeout(resolve, duration));
		torSocket.close(1000);
		window.location.href = '/play!'
		await sleep(1000);
		showAlertDanger("Player disconnected, tournament ended.");
	} else if (data.type === "error") {
		window.location.href = '/play!'
		showAlertDanger("No such tournament")
	}

// 	const userId = await getUserId();
// 	if (data?.data?.tournament_admin_id) {
// 		if (data.data.tournament_admin_id == userId) {
// 			showTournamentAdmin(canStartMatches, data);
// 		} else {
// 			changeTournamentStatus(null, canStartMatches);
// 		}
// 	}
};

const handleNewPlayer = (data) => {
	changeParticipants(data);
};

const joinTournamentLobby = async (tournamentId) => {
	try {
		await getInfo(tournamentId);
	} catch (error) {
		console.error("Error while connecting to WebSocket:", error.message);
	}
};
