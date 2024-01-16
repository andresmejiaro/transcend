
const showInFrontMatchFinish = (data) => {
	const wholeContent = document.getElementById("content");
    wholeContent.classList.add("game-over-container");
	
	const gameScreen = document.getElementById("onlineGameScreen");
    const gameOverContainer = document.createElement("div");

    const winnerHeading = document.createElement("h1");
    winnerHeading.innerText = `winner: ${data.winner_id}`;
    winnerHeading.style.color = "#f00";

    // const scoreParagraph = document.createElement("p");
    // scoreParagraph.classList.add("score");
    // scoreParagraph.innerText = "Score: " + score;

    gameOverContainer.appendChild(winnerHeading);
    // gameOverContainer.appendChild(scoreParagraph);

    gameScreen.appendChild(gameOverContainer);
}

const handleFinishedMatchUpdate = async (data) => {
	showInFrontMatchFinish(data);
}