let gameSock;

const connectGameSocket = async (gameInfo) => {
	const authToken = sessionStorage.getItem("jwt");

	const matchId = gameInfo.match_id;
	console.log(matchId);
	return new Promise((resolve, reject) => {
		gameSock = new WebSocket(`${window.DAPHNE_BASE_URL}/ws/pong2/${matchId}/?token=${authToken}`);

		gameSock.addEventListener("open", (event) => {
			resolve(gameSock);
		});

		gameSock.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);
			updateGameCanvas(data, game);
		});

		gameSock.addEventListener("close", (event) => {
			console.log("WebSocket connection closed:", event);
			reject(new Error("WebSocket connection closed."));
		});
	});
};

const sendGameSocketMessage = (messageType, payload) => {
	return new Promise((resolve, reject) => {
	  if (gameSock && gameSock.readyState === WebSocket.OPEN) {
		gameSock.send(
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

const sendStartBallToSocket = async (data) => {
	sendGameSocketMessage("command", {
		command: "start_ball",
	});
}

const handleFoundOpponent = async (data) => {
	data = data.data;
	console.log(data);
	const ws = await connectGameSocket(data, game);
	await sendStartBallToSocket();
};

// GAME HELPERSS

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
	} else if (data.type === "screen_report") {
		console.log(data)
		drawPongGame(data.data)
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

const activateGame = async () => {
	const param = '{"command":"start_game"}';
	sendJson(param);
};


