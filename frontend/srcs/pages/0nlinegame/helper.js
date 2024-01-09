
function SetUpListeners() {
	
		const uri = `ws://localhost:8001/ws/pong2/${matchIdInput.value}/?token=${sessionStorage.getItem("jwt")}`;

		ws = new WebSocket(uri);

		ws.addEventListener("open", () => {
			console.log("WebSocket connection opened.");
		});

		ws.addEventListener("close", () => {
			console.log("WebSocket connection closed.");
		});

		ws.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);
			//console.log(data);
			updateGameCanvas(data, game);
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
	if (data.type == "message"){
		game.connStatus = data.data.message;
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
		 } 
		} else if (data.type == "screen_report"){
			game.receiveRemoteCanvas(data);
		}
		 else {
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

function handleArrowKeyRelease(key) {
	// Customize this based on your game's key bindings
	switch (key) {
		case 'ArrowUp':
			sendRelease('up');
			break;
		case 'ArrowDown':
			sendRelease('down');
			break;
		case 'ArrowLeft':
			sendRelease('left');
			break;
		case 'ArrowRight':
			sendRelease('right');
			break;
	}
}

const activateGame = async () => {
	const param = '{"command":"start_ball"}';
	sendJson(param);
};

function handleArrowKeyPress(key) {
	// Customize this based on your game's key bindings
	//console.log(key);
	switch (key) {
		case 'ArrowUp':
			sendKeyPress('up');
			break;
		case 'ArrowDown':
			sendKeyPress('down');
			break;
		case 'ArrowLeft':
			sendKeyPress('left');
			break;
		case 'ArrowRight':
			sendKeyPress('right');
			break;
	}
}
