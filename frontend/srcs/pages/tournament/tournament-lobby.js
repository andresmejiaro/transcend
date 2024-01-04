let torSocket;

const connectWebSocketTor = async () => {
    const authToken = sessionStorage.getItem("jwt");
    
    return new Promise((resolve, reject) => {
		const uri = `${window.DAPHNE_BASE_URL}/ws/tournament/${tournamentId}/?token=${authToken}`
        torSocket = new WebSocket(uri);

        torSocket.addEventListener('open', (event) => {
            console.log('WebSocket connection opened:', event);
            resolve(torSocket);
        });

        torSocket.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'message') {
                console.log(data.group_name, data.message);
            }
        });

        torSocket.addEventListener('close', (event) => {
            console.log('WebSocket connection closed:', event);
            reject(new Error('WebSocket connection closed.'));
        });

        torSocket.addEventListener('error', (event) => {
            console.error('WebSocket error:', event);
            reject(new Error('WebSocket connection error.'));
        });
    });
};

const getInfo = async (tournamentId) => {
    try {
        await connectWebSocketTor(tournamentId);

		torSocket.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);
			handleTorData(data);
        });
		
        // sendWebSocketMessage('command', { command: 'get_website_group_list', data: {} });
    } catch (error) {
		console.error('Error while connecting to WebSocket:', error.message);
    }
};

const handleTorData = (data) => {
	console.log('WebSocket message received:', data);
	if (data.type == "new_player")
		handleNewPlayer(data.data.players);
}

const handleNewPlayer = (data) => {
	changeParticipants(data);
}

const joinTournamentLobby = async (tournamentId) => {
  try {
	await getInfo(tournamentId);
  } catch (error) {
	console.error("Error while connecting to WebSocket:", error.message);
  }
};
