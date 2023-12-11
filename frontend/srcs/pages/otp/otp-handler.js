const loadGoogleAuth = async () => {
  document.getElementById("gaDiv").style.display = "block";
  await enable2FA();
  await load2FA();
};

document.getElementById("startGA").addEventListener("click", function (e) {
  e.preventDefault();
  loadGoogleAuth();
});

const removeGA = async () => {
  document.getElementById("gaDiv").style.display = "none";
  await disable2FA();
};

document.getElementById("removeGA").addEventListener("click", function (e) {
  e.preventDefault();
  removeGA();
});

document.getElementById("noGA").addEventListener("click", function (e) {
  e.preventDefault();
  removeGA();
  window.location.href = "/play!";
});