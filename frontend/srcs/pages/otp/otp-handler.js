const loadGoogleAuth = async () => {
  const gaDiv = document.getElementById("gaDiv");
  gaDiv.style.display = "block";

  await enable2FA();
  await load2FA();

  document.getElementById("removeGA").style.display = "inline";
  document.getElementById("startGA").style.display = "none";
};

document.getElementById("startGA").addEventListener("click", function (e) {
  e.preventDefault();
  loadGoogleAuth();
});

const removeGA = async () => {
  const gaDiv = document.getElementById("gaDiv");
  gaDiv.style.display = "none";

  document.getElementById("removeGA").style.display = "none";
  document.getElementById("startGA").style.display = "inline";

  await disable2FA();
};

document.getElementById("removeGA").addEventListener("click", function (e) {
  e.preventDefault();
  removeGA();
});


