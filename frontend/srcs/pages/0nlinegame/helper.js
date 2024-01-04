function SetUpListeners(matchId, player1Id, player2Id, clientId, scoreLimit, game) {
	return new Promise((resolve, reject) => {
		const uri = `${window.DAPHNE_BASE_URL}/ws/pong/${matchId}/?player_1_id=${player1Id}&player_2_id=${player2Id}&client_id=${clientId}&scorelimit=${scoreLimit}`;

		ws = new WebSocket(uri);

		ws.addEventListener("open", () => {
			//console.log("WebSocket connection opened.");
			resolve(ws); // Resolve the promise with the WebSocket instance
		});

		ws.addEventListener("close", () => {
			//console.log("WebSocket connection closed.");
			reject("WebSocket connection closed."); // Reject the promise with an error message
		});

		ws.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);

			updateGameCanvas(data, game);
		});

		//ws.addEventListener("player_list", (event) => {
		//  const data = JSON.parse(event.data);

		//  console.log("Received message:", data);
		//manejar de manera sensible
		//  game.updatePlayerNames(data);
		//});

		// add event listener for game_update
	});
}

function sendJson(jsonMessage) {
	//console.log("WebSocket readyState:", ws.readyState);

	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.send(jsonMessage);
		//console.log("Sent JSON message:", jsonMessage);
	} else {
		//console.error("WebSocket connection not open.");
	}
}

function updateGameCanvas(data, game) {
	//console.log("Updating game canvas with data:", data);
	//console.log(data)
	if (data.type === "player_list") {
		//console.log("Received player list:", data.data);
		game.updatePlayerNames(data);
	} else if (data.type === "update_buffer") {
		// Handle game update data
		//console.log("game data:", data.data);
		k = data.data.length;
		game.receiveRemoteCanvas(data);
		game.scoreUpdate(data.data[k - 1]["score_update"]);
	} else if (data.type === "keyup") {
		// Handle game update data
		//console.log("game data:", data.data);
		game.remoteKeyUpHandling(data);
	} else if (data.type === "game_end") {
		// Handle game update data
		//console.log("game data:", data.data);
		game.remoteGameEnd();
	} else {
		// Handle game update data
		console.log("game data:", data.data);
		console.error("Invalid message type:", data.type);
	}
}

function sendKeyPress(key, side, frame) {
	const jsonMessage = JSON.stringify({
		command: "keyboard",
		key_status: "on_press",
		key: key,
		side: side,
		frame: frame,
	});

	// Send the JSON message to the server
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.send(jsonMessage);
		//console.log("Sent JSON message:", jsonMessage);
	} else {
		console.error("WebSocket connection not open.");
	}
}

function sendRelease(key, side, frame) {
	const jsonMessage = JSON.stringify({
		command: "keyboard",
		key_status: "on_release",
		key: key,
		side: side,
		frame: frame,
	});

	// Send the JSON message to the server
	if (ws && ws.readyState === WebSocket.OPEN) {
		ws.send(jsonMessage);
		//console.log("Sent JSON message:", jsonMessage);
	} else {
		console.error("WebSocket connection not open.");
	}
}

// const userId = await getUserId();

const canJoinAGame = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/match/available`;

		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

		const data = await makeRequest(true, url, options);

		if (data.status == "ok") {
			return data.id;
		}

		return null;
	} catch (error) {
		console.error("Error:", error.message);
	}
};

const joinMatch = async (matchId, game) => {
	const playerId = await getUserId();
	const matchData = await getMatchInfo(matchId);
	await updateMatchInDb(matchId, playerId);
	await SetUpListeners(matchId, matchData.data.player1, playerId, playerId, 11, game);
};

const activateGame = async () => {
	const param = '{"command":"start_game"}';
	sendJson(param);
};

const createAndJoinMatch = async (game) => {
	const userId = await getUserId();

	const url = `${window.DJANGO_API_BASE_URL}/api/match/create/`;
	const response = await makeRequest(true, url, {
		method: "POST",
		mode: "cors",
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			player1: userId,
		}),
	});

	//console.log(response);

	SetUpListeners(response.match_id, userId, "", userId, 11, game);
};

const handleMatchmaking = async (game) => {
	const hasToJoinMatch = await canJoinAGame();
	if (hasToJoinMatch) {
		await joinMatch(hasToJoinMatch, game);
		//activateGame();
	} else {
		createAndJoinMatch(game);
	}
};
