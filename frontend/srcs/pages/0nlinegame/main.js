const joinQueue = async () => {
	const userId = await getUserId();
	sendWebSocketMessage("join_queue", {
		command: "join_queue",
		data: {
			queue_name: "global",
			user_id: userId,
		},
	});
};

const handleMatchmaking = async (data) => {
	console.log(data)
	await joinQueue();
}


player1 = new Player("adrgonza", {up:"UNUSED_DEFAULT_KEY", down:"UNUSED_DEFAULT_KEY",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");
player2 = new Player("ai", {up:"UNUSED_DEFAULT_KEY", down:"UNUSED_DEFAULT_KEY",
        left:"UNUSED_DEFAULT_KEY", right:"UNUSED_DEFAULT_KEY"},"left");

game = new Game(player1, player2, remote = 1);

game.start();