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
  if (!updatedFriendList) return null;
  nowOnlineFriends = 0;
  updatedFriendList.forEach((friend) => {
    if (data.includes(friend.userId)) {
	    nowOnlineFriends++;
      friend.online = true;
    }
  });
  friendList = updatedFriendList;
  listFriends();
};
