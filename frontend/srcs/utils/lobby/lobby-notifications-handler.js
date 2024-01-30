let notificationInfoSent = [];
let notificationInfoReceived = [];
let receivedFriendsNotifications = [];

const updateNotifications = async (data) => {
    const bellSpan = document.getElementById("nav-notification-bell-span");
    if (data && data.length)
    bellSpan.innerHTML = data.length;
else
bellSpan.innerHTML = "";
};

let invitationListFriendsData = [];
let invitationListMatchData = [];
const handleListSentInvites = async (data) => {
    let notificationInfoSent = data.data || data;

    const matchInvites = notificationInfoSent.filter(user => user.invite_type === 'match');
    const friendRequestInvites = notificationInfoSent.filter(user => user.invite_type === 'friend_request');

    invitationListMatchData = await Promise.all(matchInvites.map(async (user) => {
        const userInfo = await getPlayerInfo(user.invite_id);
        return {
            ...userInfo,
            id: user.invite_id,
            invite_type: user.invite_type,
        };
    }));

    invitationListFriendsData = await Promise.all(friendRequestInvites.map(async (user) => {
        const userInfo = await getPlayerInfo(user.invite_id);
        return {
            ...userInfo,
            id: user.invite_id,
            invite_type: user.invite_type,
        };
    }));

    await listInvitationFriendsNav();
    await listInvitationMatchNav();
};

const handleListReceivedInvites = async (data) => {
    if (data.data)
        notificationInfoReceived = data.data;
    else
        notificationInfoReceived = data;
	updateNotifications(notificationInfoReceived);

	const updatedInfo = await Promise.all(notificationInfoReceived.map(async (user) => {
        const userInfo = await getPlayerInfo(user.invite_id);
        return {
            ...userInfo,
            id: user.invite_id,
            invite_type: user.invite_type,
        };
    }));
    receivedFriendsNotifications = updatedInfo;
};

const handleCancelFriendRequest = async (data) => {
    const clientIdToRemove = data.data.client_id;
    const newData = invitationListFriendsData.filter(user => user.id !== clientIdToRemove);
    await handleListSentInvites(newData);
    handleCloseFriendsModalMsg("Friend Request Removed Succesfully");
};


const handleCanceledAFriendRequest = async (data) => {
    const clientIdToRemove = data.data.client_id;
    const canceledUser = receivedFriendsNotifications.find(user => user.id === clientIdToRemove);
    const newData = receivedFriendsNotifications.filter(user => user.id !== clientIdToRemove);
    await handleListReceivedInvites(newData);
    if (canceledUser) {
        const toastMessage = `${canceledUser.username} canceled the friend request`;
        showToast(toastMessage);
    }
};

