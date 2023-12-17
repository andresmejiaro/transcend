const handleInviteSent = async (inviteId) => {
  const userId = await getUserId();
  if (userId == inviteId) {
    showAlertDanger("Can´t add yourself as friend")
    return;
  }
  handleBackButtonClick();
};

const inviteFriend = async (inviteId) => {
  const userId = await getUserId();
  if (userId == inviteId) {
    handleCloseModal();
    showAlertDanger("Can´t add yourself as friend")
    return;
  }
  sendWebSocketMessage("command", {
    command: "send_friend_request",
    data: {
      client_id: `${inviteId}`,
    },
  });
  handleCloseModalMsg("Invite send succesfully");
};
