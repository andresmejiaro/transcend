const playOnlineGameClickHandler = async function () {
	const targetUrl = "/onlinegame";
	await navigateTo(targetUrl);
};

const playSinglePlayerClickHandler = async function () {
	const targetUrl = "/1plygame";
	await navigateTo(targetUrl);
};

const playTwoPlayersClickHandler = async function () {
	const targetUrl = "/2plygame";
	await navigateTo(targetUrl);
};

document.body.addEventListener("click", function (event) {
	const target = event.target;
	if (target.id === "onlineGameBtn") {
		playOnlineGameClickHandler();
	} else if (target.id === "singlePlayerBtn") {
		playSinglePlayerClickHandler();
	} else if (target.id === "twoPlayersBtn") {
		playTwoPlayersClickHandler();
	}
});
