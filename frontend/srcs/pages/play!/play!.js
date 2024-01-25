const playOnlineGameClickHandler = async function (e) {
	e.preventDefault();
	const targetUrl = "/onlinegame";
	await navigateTo(targetUrl);
};

const playSinglePlayerClickHandler = async function (e) {
	e.preventDefault();
	const targetUrl = "/1plygame";
	await navigateTo(targetUrl);
};

const playTwoPlayersClickHandler = async function (e) {
	e.preventDefault();
	const targetUrl = "/2plygame";
	await navigateTo(targetUrl);
};

document.getElementById("onlineGameBtn").addEventListener("click", playOnlineGameClickHandler);
document.getElementById("singlePlayerBtn").addEventListener("click", playSinglePlayerClickHandler);
document.getElementById("twoPlayersBtn").addEventListener("click", playTwoPlayersClickHandler);
