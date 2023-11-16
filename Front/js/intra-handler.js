var button = document.getElementById("intra");

const handleButtonClick = async () => {
    const clientId = "u-s4t2ud-ca3a07a81bac42c6b896a950e6bcce0a4072c14b72a8aea1e48f732b55dd58e2"
    const redirectUri = "your-redirect-uri";

    // const authUrl = `https://api.intra.42.fr/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}`;
    const authUrl = `https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-ca3a07a81bac42c6b896a950e6bcce0a4072c14b72a8aea1e48f732b55dd58e2&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback&response_type=code`;

    window.location.href = authUrl;


};

button.addEventListener("click", handleButtonClick);
