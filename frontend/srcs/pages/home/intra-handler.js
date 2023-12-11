function showButtons() {
  setTimeout(function() {
    document.getElementById('home-div').style.opacity = '1';
  }, 1000);
}

let button = document.getElementById("intra");

const handleButtonClick = async () => {
  const clientId = "u-s4t2ud-8a3d7b6ac3c28259758ac83a1d842d4a448f4bc3d0afadbc90eb50f6c29083c7";
  const redirectUri = "http%3A%2F%2Flocalhost%3A3000%2Fintra";
  const authUrl = `https://api.intra.42.fr/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code`;
  window.location.href = authUrl;
};

button.addEventListener("click", function (event) {
  event.preventDefault();
  handleButtonClick();
});
