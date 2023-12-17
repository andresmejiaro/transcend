let notificationInfo = [];

const updateNotifications = async (data) => {
	notificationInfo = data.data;
	const bellSpan = document.getElementById("nav-notification-bell-span");
  if (notificationInfo.length)
    bellSpan.innerHTML = notificationInfo.length;
};