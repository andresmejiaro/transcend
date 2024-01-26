const leaveQueue = async () => {
	const userId = await getUserId();
	sendWebSocketMessage("leave_queue", {
		command: "leave_queue",
		data: {
			queue_name: "global",
			user_id: userId,
		},
	});
};

const handleExitOnlineGamePage = async () => {
	await leaveQueue();
};

const ifLoggedRedirect = (location) => {
	if (!isLogged()) {
		if (!allowedLocations.includes(window.location.pathname)) {
			console.log("router logout");
			handleLogout();
		}
	} else {
		if (allowedLocations.includes(location)) {
			window.location.pathname = "/play!";
		}
	}
};
