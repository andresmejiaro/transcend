document.getElementById("friendsModal").addEventListener("shown.bs.modal", function (event) {
	event.preventDefault();

	const btn = document.getElementById("back-modal-btn");
	btn.removeEventListener("click", handleBackButtonClick);
	btn.addEventListener("click", handleBackButtonClick);

	const btnn = document.getElementById("friendsModalInvite");
	btnn.addEventListener("click", function (event) {
		event.preventDefault();
		handleModalForInvite();
	});
});

const handleModalForInvite = async () => {
	const modalBodyFriends = document.getElementById("modal-body-friends-invite");
	const modalBodyList = document.getElementById("modal-body-friends-list");
	// Toggle the visibility of modal bodies
	if (modalBodyFriends.style.display === 'none') {
		modalBodyFriends.style.display = 'block';
		modalBodyList.style.display = 'none';
		await listInvitationFriendsNav(); // Update content for friends if needed
	}
	
	// Remove existing event listeners
	const btn = document.getElementById("back-modal-btn");
	btn.removeEventListener("click", handleBackButtonClick);
	btn.addEventListener("click", handleBackButtonClick);
	const sendInvitationBtn = document.getElementById("sendInvitationBtn");
	sendInvitationBtn.removeEventListener("click", handleSendInvitationClick);
	sendInvitationBtn.addEventListener("click", handleSendInvitationClick);
};

const handleBackButtonClick = async () => {
	const modalBodyFriends = document.getElementById("modal-body-friends-invite");
	const modalBodyList = document.getElementById("modal-body-friends-list");
	modalBodyFriends.style.display = 'none';
	modalBodyList.style.display = 'block';

	const btn = document.getElementById("back-modal-btn");


	// if (btn) {
	// 	btn.removeEventListener("click", handleBackButtonClick);
	// 	btn.addEventListener("click", handleBackButtonClick);
	// }

	await listInvitationFriendsNav(); // Update content for friends if needed
};

const handleSendInvitationClick = async (event) => {
	event.preventDefault();
	const clientUsername = document.getElementById("invitationInput").value;
	await inviteFriend(clientUsername);
};
