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

		const gamesPlayedElement = document.getElementById("gamesPlayedNumber");
		const winsElement = document.getElementById("winsNumber");
		const winRateElement = document.getElementById("winRateNumber");
		const tournamentsWonElement = document.getElementById("tournamentsWonNumber");

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

		matchHistoryList.innerHTML = "";

		if (Array.isArray(matchHistoryData.data)) {
			const limitedMatches = matchHistoryData.data.slice(0, 100);

			limitedMatches.forEach((match) => {
				const listItem = document.createElement("li");
				listItem.classList.add("list-group-item");
				const formattedDate = new Date(match.date_played).toLocaleDateString();
				listItem.textContent = `Date: ${formattedDate}, Winner: ${match.winner}, Scores: ${match.player1_score} - ${match.player2_score}`;
				matchHistoryList.appendChild(listItem);
			});
		} else {
			console.error("Error: matchHistoryData.data is not an array");
		}
	} catch (error) {
		console.error("Error fetching match history:", error.message);
	}
};

let isModalOpen = false;

function searchUser() {
    // Get the entered username from the input field
    const username = document.getElementById('searchUsername').value;

    // Perform a check to ensure the username is not empty
    if (username.trim() === '') {
        showAlertDanger('Please enter a username!');
        return;
    }

    // Check if a modal is already open
    if (isModalOpen) {
        closeUserInfoPopup();
    }

    // Call your API endpoint to fetch user stats based on the entered username
    fetchUserStats(username);
}

function closeUserInfoPopup() {
    // Remove the modal container if it exists
    const modalContainer = document.querySelector(".user-info-modal");
    const overlay = document.querySelector(".overlay");

    if (modalContainer) {
        document.body.removeChild(modalContainer);
        document.body.removeChild(overlay); // Remove the overlay
        isModalOpen = false;
    }
}

async function fetchUserStats(username) {
    try {
		// Construct the API endpoint URLs
		const infoUrl = `${window.DJANGO_API_BASE_URL}/api/user/info-user/${username}/`;
		const statsUrl = `${window.DJANGO_API_BASE_URL}/api/user/stats/${username}/`;
		const matchHistoryUrl = `${window.DJANGO_API_BASE_URL}/api/user/match/${username}/`;

        // Create the request options
        const options = {
            method: "GET",
            mode: "cors",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        };

        // Make the API calls
        const infoData = await makeRequest(true, infoUrl, options);
        const statsData = await makeRequest(true, statsUrl, options);
		const matchHistoryData = await makeRequest(true, matchHistoryUrl, options);
		
        if (infoData.status === "ok" && statsData.status === "ok" && matchHistoryData.status === "ok") {
            // User found, display the user info and stats
            displayUserInfoPopup(infoData.user, statsData.data, matchHistoryData.data);
        } else {
            // User not found or error in fetching stats, show a message
            showAlertDanger('User not found or error in fetching stats');
        }
    } catch (error) {
        console.error("Error:", error.message);
    }
}

function displayUserInfoPopup(userData, statsData, matchHistoryData) {
    console.log("Displaying user info and stats:", userData, statsData, matchHistoryData);

    // Set isModalOpen to true
    isModalOpen = true;

    // Create a modal container
    const modalContainer = document.createElement("div");
    modalContainer.classList.add("user-info-modal");

    // Create the overlay element
    const overlay = document.createElement("div");
    overlay.classList.add("overlay");

    // Add the overlay to the document body
    document.body.appendChild(overlay);

    // Show the overlay
    overlay.style.display = "block";

    // Create elements to display user info
    const usernameElement = document.createElement("p");
	usernameElement.style.textAlign = "center";
    usernameElement.textContent = `${userData.username}`;

    // Create avatar image element
    const avatarImageElement = document.createElement("img");
    avatarImageElement.alt = "User Avatar";
    avatarImageElement.style.width = "320px";

    // Check if the user has an avatar URL
    if (userData.avatar_url) {
        // Create an image object to check if the image exists
        const img = new Image();
        img.onload = function () {
            // Image exists, set the src attribute
            avatarImageElement.src = `${window.DJANGO_API_BASE_URL}${userData.avatar_url}`;
        };
        img.onerror = function () {
            // Image does not exist, set a default avatar or leave it blank
            avatarImageElement.src = `${window.DJANGO_API_BASE_URL}/srcs/assets/imgs/default-avatar.jpeg`; // You can replace this with the path to your default avatar
        };
        img.src = `${window.DJANGO_API_BASE_URL}${userData.avatar_url}`;
    } else {
        // User does not have an avatar URL, set a default avatar or leave it blank
        avatarImageElement.src = `${window.DJANGO_API_BASE_URL}/srcs/assets/imgs/default-avatar.jpeg`; // You can replace this with the path to your default avatar
    }

    // Create elements to display user stats
    const gamesPlayedElement = document.createElement("p");
    gamesPlayedElement.textContent = `Games Played: ${statsData.games_played}`;

    const winsElement = document.createElement("p");
    winsElement.textContent = `Wins: ${statsData.wins}`;

	const winRateElement = document.createElement("p");
	winRateElement.textContent = `Win Rate: ${Math.round(statsData.winrate)}%`;

	const tournamentsWonElement = document.createElement("p");
	tournamentsWonElement.textContent = `Tournaments Won: ${statsData.tournaments_won}`;

	// Create element to display match history similar to the one on the profile page
	const matchHistoryList = document.createElement("ul");
	matchHistoryList.classList.add("list-group");
	matchHistoryList.style.maxHeight = "300px";
	matchHistoryList.style.height = "auto"; // Set a fixed height for the scrollable area
	matchHistoryList.style.overflowY = "auto"; // Enable vertical scrolling


	// Check if matchHistoryData is an array
	if (Array.isArray(matchHistoryData)) {
		// Limit the number of matches to 20
		const limitedMatches = matchHistoryData.slice(0, 100);

		// Populate match history list
		limitedMatches.forEach(match => {
			const listItem = document.createElement("li");
			listItem.classList.add("list-group-item");
			const formattedDate = new Date(match.date_played).toLocaleDateString();
			listItem.textContent = `Date: ${formattedDate}, Winner: ${match.winner}, Scores: ${match.player1_score} - ${match.player2_score}`;
			matchHistoryList.appendChild(listItem);
		}
		);
	} else {
		console.error("Error: matchHistoryData is not an array");
	}
	
	// Create close button
	const closeButton = document.createElement("span");
	closeButton.classList.add("close-modal");
	closeButton.innerHTML = "&times;"; // Use the 'times' character (X)
	closeButton.style.fontSize = "24px"; // Set the font size
	closeButton.style.color = "red";
	closeButton.style.padding = "10px"; // Set padding to provide more clickable area

    // Add elements to the modal container
    modalContainer.appendChild(closeButton);
    modalContainer.appendChild(usernameElement);
    modalContainer.appendChild(avatarImageElement);
    modalContainer.appendChild(gamesPlayedElement);
    modalContainer.appendChild(winsElement);
	modalContainer.appendChild(winRateElement);
	modalContainer.appendChild(tournamentsWonElement);
	modalContainer.appendChild(matchHistoryList);
	
    // Add the modal container to the document body
    document.body.appendChild(modalContainer);

    // Show the modal
    modalContainer.style.display = "block";

	// Close the modal when clicking the close button or outside the modal
	closeButton.onclick = () => {
		closeUserInfoPopup();
	};

	window.onclick = (event) => {
		if (event.target === modalContainer) {
			closeUserInfoPopup();
		}
    };
}


getMeSettingsInfoProfile();
