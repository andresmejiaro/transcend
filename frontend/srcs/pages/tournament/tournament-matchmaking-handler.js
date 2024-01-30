const handleMatchmakingTor = async (data) => {
	const userId = await getUserId();

	for (const matchInfo of Object.values(data.matches)) {
		const { match_id, player1, player2, active } = matchInfo;

		if (player1 === userId || player2 === userId) {
			await joinTorMatch(match_id, player1, player2);
		}
	}
};
