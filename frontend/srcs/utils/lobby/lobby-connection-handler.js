let lobbySocket;

const sendWebSocketMessage = async(messageType, payload) => {
	const sleep = (duration) => new Promise(resolve => setTimeout(resolve, duration));

    // Loop until the WebSocket is open
    while (!lobbySocket || lobbySocket.readyState !== WebSocket.OPEN) {
        // Wait for a short period before checking again
        await sleep(50);
    }

	return new Promise((resolve, reject) => {
		if (lobbySocket && lobbySocket.readyState === WebSocket.OPEN) {
			lobbySocket.send(
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

const connectWebSocket = async () => {
	const authToken = sessionStorage.getItem("jwt");

	if (lobbySocket && lobbySocket.readyState === WebSocket.OPEN) {
		console.log("WebSocket is already connected.");
		return Promise.resolve(lobbySocket);
	}

	return new Promise((resolve, reject) => {
		lobbySocket = new WebSocket(`${window.DAPHNE_BASE_URL}/ws/lobby/?token=${authToken}`);
		console.log("LobbySocket connection....")

		lobbySocket.addEventListener("open", (event) => {
			resolve(lobbySocket); // Resolve with the WebSocket object
		});

		lobbySocket.addEventListener("message", (event) => {
			const data = JSON.parse(event.data);
			if (data.type === "message") {
				console.log(data.group_name, data.message);
			}
		});

		lobbySocket.addEventListener("close", (event) => {
			console.log("WebSocket connection closed:", event);
			reject(new Error("WebSocket connection closed."));
		});

		lobbySocket.addEventListener("error", (event) => {
			console.error("WebSocket error:", event);
			reject(new Error("WebSocket connection error."));
		});
	});
};

const getOnlineUsers = async () => {
	try {
		await connectWebSocket();

		lobbySocket.addEventListener("message", (event) => {
			handleMessage(event.data);
		});

		// lobbySocket.onmessage = (event) => {
		//   handleMessage(event.data);
		// };

		sendWebSocketMessage("command", {
			command: "list_of_users",
			data: {},
		});
	} catch (error) {
		// handleLogout();
		console.error("Error while connecting to WebSocket:", error.message);
	}
};

const getPendingNotifications = async () => {
	const userId = await getUserId();
	sendWebSocketMessage("command", {
		command: "list_sent_invites",
		data: {
			client_id: userId,
		},
	});
	sendWebSocketMessage("command", {
		command: "list_received_invites",
		data: {
			client_id: userId,
		},
	});
};

const joinLobby = async () => {
	try {
		await getOnlineUsers();
		await getPendingNotifications();
	} catch (error) {
		console.error("Error while connecting to WebSocket:", error.message);
		// Handle error as needed (e.g., display an error message to the user)
	}
};

console.log("joining lobby")
joinLobby();
