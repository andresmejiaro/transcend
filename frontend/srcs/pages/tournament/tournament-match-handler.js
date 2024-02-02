const torInfoContent = document.getElementById("tor-cont-one")
const torMatchContent = document.getElementById("tor-cont-two");
const joinTorMatch = async (match_id, player1Id, player2Id) => {
	torInfoContent.style.display = "none";
	torMatchContent.style.display = "block";
	
	const me = await getPlayerInfo(player1Id);
	const other = await getPlayerInfo(player2Id);

	player1 = new Player(me.username, { up: "UNUSED_DEFAULT_KEY", down: "UNUSED_DEFAULT_KEY", left: "UNUSED_DEFAULT_KEY", right: "UNUSED_DEFAULT_KEY" }, "left");
	player2 = new Player(other.username, { up: "UNUSED_DEFAULT_KEY", down: "UNUSED_DEFAULT_KEY", left: "UNUSED_DEFAULT_KEY", right: "UNUSED_DEFAULT_KEY" }, "left");
	game = new Game(player1, player2, (remote = 1));

	gameSock = await connectGameSocket({match_id: match_id});

	await game.start();
};

const leaveTorMatch = () => {
	torInfoContent.style.display = "block";
	torMatchContent.style.display = "none";
}