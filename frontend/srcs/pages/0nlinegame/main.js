const handleFoundOpponent = async (data) => {
	data = data.data;
	const me = await getPlayerInfo(data.client_id);
	const other = await getPlayerInfo(data.opponent_id);

	player1 = new Player(me.username, { up: "UNUSED_DEFAULT_KEY", down: "UNUSED_DEFAULT_KEY", left: "UNUSED_DEFAULT_KEY", right: "UNUSED_DEFAULT_KEY" }, "left");
	player2 = new Player(other.username, { up: "UNUSED_DEFAULT_KEY", down: "UNUSED_DEFAULT_KEY", left: "UNUSED_DEFAULT_KEY", right: "UNUSED_DEFAULT_KEY" }, "left");
	game = new Game(player1, player2, (remote = 1));

	gameSock = await connectGameSocket(data);

	await game.start();
};

const joinQueue = async () => {
	const userId = await getUserId();
	sendWebSocketMessage("join_queue", {
		command: "join_queue",
		data: {
			queue_name: "global",
			user_id: userId,
		},
	});
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.font = '30pt VT323';
	ctx.fillText(`Waiting for players..!`, 240, 120);

};

joinQueue();
