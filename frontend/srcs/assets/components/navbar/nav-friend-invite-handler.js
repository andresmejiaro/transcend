const handleInviteSent = async () => {
  const modalBody = document.getElementById("modal-body-friends");
  const isInputVisible = modalBody.querySelector("#invitationInput") !== null;
  if (isInputVisible) {
    modalBody.innerHTML = initialContent;
  }
  await listInvitationFriends();
};

const inviteFriend = async (inviteId) => {
  sendWebSocketMessage("command", {
    command: "send_friend_request",
    data: {
      client_id: `${inviteId}`,
    },
  });
};
