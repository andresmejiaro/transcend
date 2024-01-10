const getMeSettingsInfoProfile = async () => {
	try {
		const url = `${window.DJANGO_API_BASE_URL}/api/user/info-me/`;

		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};
		const data = await makeRequest(true, url, options);

		if (data.status === "ok") {
			const usernameElement = document.getElementById("user-username");
			const avatarImage = document.getElementById("avatarImageUser");

			console.log(data);

			usernameElement.innerHTML = data.user.username;
			
			if (data.user.avatar_url) {
				const completeAvatarUrl = `${window.DJANGO_API_BASE_URL}${data.user.avatar_url}`;
				avatarImage.src = completeAvatarUrl;

			}
			// Get user ID from local storage token

			updateStats();
		}
	} catch (error) {
		console.error("Error:", error.message);
	}
};

const updateStats = async () => {
    try {
        const statsUrl = `${window.DJANGO_API_BASE_URL}/api/user/stats/`;

		const options = {
			method: "GET",
			mode: "cors",
			credentials: "include",
			headers: {
				"Content-Type": "application/json",
			},
		};

        const statsData = await makeRequest(true, statsUrl, options);
		console.log(statsData);

        
		const gamesPlayedElement = document.getElementById("gamesPlayedNumber");
		const winsElement = document.getElementById("winsNumber");
		const winRateElement = document.getElementById("winRateNumber");
		const tournamentsWonElement = document.getElementById("tournamentsWonNumber");
		
		// Set just the number without any accompanying text
		gamesPlayedElement.innerText = statsData.games_played;
		winsElement.innerText = statsData.wins;
		winRateElement.innerText = Math.round(statsData.winrate);
		tournamentsWonElement.innerText = statsData.tournaments_won;
		
    } catch (error) {
        console.error("Error fetching stats:", error.message);
    }
};

getMeSettingsInfoProfile();
