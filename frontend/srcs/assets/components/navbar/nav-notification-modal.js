const handleModalForNotifications = async () => {
	function createNotificationElement(data) {
		const notificationContainer = document.getElementById("notifications-list");

		const notificationDiv = document.createElement("div");
		notificationDiv.classList.add("d-flex");
		notificationDiv.classList.add("justify-content-between");

		const descriptionDiv = document.createElement("div");
		const descriptionParagraph = document.createElement("p");
		if (data.invite_type === "match") {
			descriptionParagraph.textContent = `${data.username} invited you to a Match`;
		} else {
			if (data.username.length > 10) {
				descriptionParagraph.textContent = `${data.username.substring(0, 10)}... wants to be your friend`;
			} else {
				descriptionParagraph.textContent = `${data.username} wants to be your friend`;
			}
		}
		

		descriptionDiv.appendChild(descriptionParagraph);

		const actionsDiv = document.createElement("div");

		const acceptButton = document.createElement("button");
		acceptButton.type = "button";
		acceptButton.classList.add("accept-btn");
		acceptButton.innerHTML = '<i class="bi bi-check"></i>';
		acceptButton.addEventListener("click", async () => {
			if (data.invite_type !== "match") {
				(async () => {
					await acceptFriendRequest(data);
				})();
			} else {
        (async () => {
					await acceptMatchRequest(data);
				})();
			}
		});

		const rejectButton = document.createElement("button");
		rejectButton.type = "button";
		rejectButton.classList.add("reject-btn");
		rejectButton.innerHTML = '<i class="bi bi-x"></i>';
		rejectButton.addEventListener("click", async () => {
			if (data.invite_type !== "match") {
				(async () => {
					await rejectFriendRequest(data);
				})();
			} else {
        (async () => {
					await rejectMatchRequest(data);
				})();
			}
		});

		actionsDiv.appendChild(acceptButton);
		actionsDiv.appendChild(rejectButton);

		notificationDiv.appendChild(descriptionDiv);
		notificationDiv.appendChild(actionsDiv);

		notificationContainer.appendChild(notificationDiv);
	}

	const notificationContainer = document.getElementById("notifications-list");
	notificationContainer.innerHTML = "";
	receivedFriendsNotifications.forEach(createNotificationElement);
	updateNavNotification(receivedFriendsNotifications.length);
};

// const btn = document.getElementById("notificationsModalInvite");
document.getElementById("notificationsModal").addEventListener("shown.bs.modal", function (event) {
	event.preventDefault();
	handleModalForNotifications();
});

// if (notificationInfo.length) {
//   updateNavNotification(notificationInfo.length)
// }

const handleCloseNotificationModal = () => {
	const closeModalBtn = document.querySelector(".btn-close.btn-close-white.btn-notifications-close");
	closeModalBtn.click();
};

const handleCloseNotificationModalMsg = (msg) => {
	const closeModalBtn = document.querySelector(".btn-close.btn-close-white.btn-notifications-close");
	closeModalBtn.click();
	showSimpleToast(msg);
};
