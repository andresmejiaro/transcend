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

			usernameElement.innerHTML = data.user.username;
			
			if (data.user.avatar_url) {
				const completeAvatarUrl = `${window.DJANGO_API_BASE_URL}${data.user.avatar_url}`;
				avatarImage.src = completeAvatarUrl;

			}
			// Get user ID from local storage token

			updateStats();
			updateMatchHistory();
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
		winRateElement.innerText = Math.round(statsData.winrate) + "%";
		tournamentsWonElement.innerText = statsData.tournaments_won;
		
    } catch (error) {
        console.error("Error fetching stats:", error.message);
    }
};

const updateMatchHistory = async () => {
    try {
        const matchHistoryUrl = `${window.DJANGO_API_BASE_URL}/api/user/match/`;

        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        const matchHistoryData = await makeRequest(true, matchHistoryUrl, options);

        const matchHistoryList = document.getElementById("matchHistoryList");

        // Clear existing items
        matchHistoryList.innerHTML = "";

        // Check if matchHistoryData.data is an array
        if (Array.isArray(matchHistoryData.data)) {
            // Limit the number of matches to 20
            const limitedMatches = matchHistoryData.data.slice(0, 100);

            // Populate match history list
            limitedMatches.forEach(match => {
                const listItem = document.createElement("li");
                listItem.classList.add("list-group-item");
                listItem.textContent = `Match ID: ${match.id}, Winner: ${match.winner}, Scores: ${match.player1_score} - ${match.player2_score}`;
                matchHistoryList.appendChild(listItem);
            });
        } else {
            console.error("Error: matchHistoryData.data is not an array");
        }
    } catch (error) {
        console.error("Error fetching match history:", error.message);
    }
};

getMeSettingsInfoProfile();
