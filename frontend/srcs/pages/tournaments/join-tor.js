let torSocket;

const connectWebSocket = async (tournamentId) => {
    return new Promise((resolve, reject) => {
        torSocket = new WebSocket(`ws://localhost:8001/ws/touurnament/?id=${tournamentId}`);

        torSocket.addEventListener('open', (event) => {
            console.log('WebSocket connection opened:', event);
            resolve(torSocket);  // Resolve with the WebSocket object
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

const getOnlineUsers = async () => {
    try {
        await connectWebSocket();

		torSocket.addEventListener('message', (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);
        });

        sendWebSocketMessage('command', { command: 'get_website_group_list', data: {} });
    } catch (error) {
        console.error('Error while connecting to WebSocket:', error.message);
    }
};


const sendWebSocketMessage = (messageType, payload) => {
    if (torSocket && torSocket.readyState === WebSocket.OPEN) {
        torSocket.send(JSON.stringify({
            type: messageType,
            ...payload,
        }));
    } else {
        console.error('WebSocket is not in the OPEN state.');
        // Handle the case where WebSocket is not open (e.g., display a user-friendly message)
    }
};

const handleJoinTorSocket = async (tournamentId) => {
	await connectWebSocket(tournamentId);
};


const handleJoinTor = async (tournamentId, userId) => {
  const url = `http://localhost:8000/api/tournament/${tournamentId}/`;
  const options = {
    method: "PUT",
    mode: "cors",
    credentials: "include",
    body: JSON.stringify({
      players: [userId],
    }),
  };

  try {
    const data = await makeRequest(true, url, options, "");
    if (data.status == "ok") {
      window.location = `/tournament?id=${tournamentId}`;
    }
  } catch (error) {
    console.log(error);
  }
};

const handleJoin = async (tournamentId) => {
	const userId = await getUserId();
	await handleJoinTor(tournamentId, userId);
	// await handleJoinTorSocket(tournamentId);
};
