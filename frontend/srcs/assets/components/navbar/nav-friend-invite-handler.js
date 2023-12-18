const handleInviteSent = async (inviteId) => {
  sendWebSocketMessage("command", {
    command: "list_sent_invites",
    data: {},
  });
  handleBackButtonClick();
};

const canInviteFriend = async (inviteId, userId) => {
  if (userId === inviteId) {
    return {
      status: false,
      msg: "Can't add yourself as a friend",
    };
  }

  const isInvitationPending = invitationListFriendsData.some(user => user.id == inviteId);
  const isAlreadyFriend = friendList.some(user => user.userId == inviteId);  
  if (isInvitationPending || isAlreadyFriend) {
    return {
      status: false,
      msg: isInvitationPending ? "There is already an invitation going on" : "User is already a friend",
    };
  }

  return {
    status: true,
    msg: "Success",
  };
};

const inviteFriend = async (clientUsername) => {
  const inviteId = await getIdFromUsername(clientUsername);
  if (!inviteId) {
    handleCloseFriendsModal();
    showAlertDanger("User not found");
    return;
  }
  
  const userId = await getUserId();
  const invite = await canInviteFriend(inviteId, userId);
  if (!invite.status) {
    handleCloseFriendsModal();
    showAlertDanger(invite.msg);
    return;
  }

  sendWebSocketMessage("command", {
    command: "send_friend_request",
    data: {
      client_id: `${inviteId}`,
    },
  });
  handleCloseFriendsModalMsg("Invite send succesfully");
};

