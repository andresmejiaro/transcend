let friendList = [];
let nowOnlineFriends;

const getListFriends = async () => {
  const userId = await getUserId();

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/user/${userId}/friendlist/`;

    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options);

    if (data.status == "ok") {
      return data.data;
    }
  } catch (error) {
    console.error("Error:", error.message);
  }
};

const getMyFriends = async () => {
  const friendData = await getListFriends();
  if (friendData) {
    return friendData.map((friend) => ({
      userId: friend.id,
      username: friend.username,
      online: false,
    }));
  } else {
    return null;
  }
};

const updateFriendStatus = async (data) => {
  const updatedFriendList = await getMyFriends();
  data = data.data;
  if (!updatedFriendList) return null;
  nowOnlineFriends = 0;
  if (data.online_users) data = data.online_users;
  updatedFriendList.forEach((friend) => {
    const friendUserId = friend.userId;
    if (friendUserId in data) {
      nowOnlineFriends++;
      friend.online = true;
    }
  });
  friendList = updatedFriendList;
  await listFriendsNav();
  await listInvitationFriendsNav();
};

const handleSendFriendRequest = async (data) => {
  await handleInviteSent(data.data.invite_id);
};

const handleReceivedFriendRequest = async (data) => {
  showToast(data.type);
  await getPendingNotifications();
};

const updateFriendStatusNow = async (data) => {
  const updatedFriendList = await getMyFriends();
  if (!updatedFriendList) return null;
  const targetId = data.data.client_id;
  nowOnlineFriends = 0;
  if (data) {
    updatedFriendList.forEach((friend) => {
      const friendUserId = friend.userId;
      if (friendUserId == targetId) {
        nowOnlineFriends++;
        friend.online = true;
      }
    });
  }
  friendList = updatedFriendList;
  await listFriendsNav();
  invitationListFriendsData = invitationListFriendsData.filter(friend => friend.id !== targetId);
  await listInvitationFriendsNav();
};

const handleMeAcceptedFriendRequest = async (data) => {
  showToast(data.type);
  await updateFriendStatusNow(data);
  handleCloseNotificationModal();
  receivedFriendsNotifications = receivedFriendsNotifications.filter(user => user.id !== data.data.client_id);
  handleModalForNotifications()
};

const handleAcceptedFriendRequest = async (data) => {
  showToast(data.type);
  await updateFriendStatusNow(data);
};

const handleMeRejectedFriendRequest = async (data) => {
  showToast(data.type);
  await updateFriendStatusNow(data);
  handleCloseNotificationModal();
  receivedFriendsNotifications = receivedFriendsNotifications.filter(user => user.id !== data.data.client_id);
  handleModalForNotifications();
};

const handleRejectedFriendRequest = async (data) => {
  const userObj = await getPlayerInfo(data.data.client_id);
  const toastMessage = `${userObj.username} rejected the friend request`;
  showToast(toastMessage);
  invitationListFriendsData = invitationListFriendsData.filter(user => user.id !== data.data.client_id);
  listInvitationFriendsNav();
};
