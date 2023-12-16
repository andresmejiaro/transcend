let friendList = [];
let pendingFriendInvitationList = [];
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
  updatedFriendList.forEach((friend) => {
    const friendUserId = friend.userId;
    if (friendUserId in data.online_users) {
      nowOnlineFriends++;
      friend.online = true;
    }
  });
  friendList = updatedFriendList;
  listFriends();
  listInvitationFriends();
};


const updateSendFriendRequests = async (data) => {
  if (data.data.message == "Friend request sent")
    await handleInviteSent();
}

const updateReceiveFriendRequests = async (data) => {
  console.log("Received an invite", data.client_id)
  console.log(data);
  updateNavNotification(1);
}