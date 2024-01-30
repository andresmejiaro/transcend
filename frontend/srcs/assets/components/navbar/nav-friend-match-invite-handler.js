const createAndJoinMatchFriend = async (userId) => {
	const url = `${window.DJANGO_API_BASE_URL}/api/match/create/`;
	const response = await makeRequest(true, url, {
		method: "POST",
		mode: "cors",
		credentials: "include",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			player1: userId,
		}),
	});
	return response.match_id;
	// startGame(response.match_id, userId, "", userId, 11);
};

const handleInviteFriendToMatch = async (friend) => {
	try {
		const friendId = friend.userId;
		const userId = await getUserId();
		const matchId = await createAndJoinMatchFriend(userId);

		await sendWebSocketMessage("command", {
			command: "invite_to_match",
			data: {
				client_id: `${friendId}`,
				match_id: `${matchId}`,
			},
		});

		// Esperar para redirigir
		//   await new Promise(resolve => setTimeout(resolve, 500));
		//   window.location.href = `/2plygame?matchid=${matchId}`;
		handleCloseFriendsModal();
		showAlertSuccess("Match Invite sent succesfully, waiting for friend to accept request");
	} catch (error) {
		console.error("Error:", error);
	}
};
