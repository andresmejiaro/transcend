let gameSocket;

const connectGameWebSocket = async (matchId,player1, player2, canvasMsg) => {
    const userId = await getIdFromUsername(sessionStorage.getItem("username"));

    return new Promise((resolve, reject) => {
        
        const WebSocketURL = `ws://localhost:8000/ws/pong/${matchId}/` +
            `?client_id=${userId}&player_1=${player1}&player_2=${player2}` +
            `&game_mode=${gameMode}`
        
        gameSocket = new WebSocket(WebSocketURL);

        gameSocket.addEventListener('open', (event) => {
            console.log('Game WebSocket connection opened:', event);
            resolve(gameSocket);  // Resolve with the WebSocket object
        });

        gameSocket.addEventListener('game_update', (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'game_update') {
                //procesar
                canvasMsg = data;
            }
        });

        gameSocket.addEventListener('close', (event) => {
            console.log('WebSocket connection closed:', event);
            reject(new Error('WebSocket connection closed.'));
        });

        gameSocket.addEventListener('error', (event) => {
            console.error('WebSocket error:', event);
            reject(new Error('WebSocket connection error.'));
        });
    });
};

const sendWebSocketGameMessage = (messageType, payload) => {
    if (gameSocket && gameSocket.readyState === WebSocket.OPEN) {
        gameSocket.send(JSON.stringify({
            type: messageType,
            ...payload,
        }));
    } else {
        console.error('WebSocket is not in the OPEN state.');
        // Handle the case where WebSocket is not open (e.g., display a user-friendly message)
    }
};


