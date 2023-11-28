function showBootstrapAlert() {
  var alertElement = document.getElementById("myAlert");
  console.log(alertElement)
  alertElement.classList.add("show");
  setTimeout(function () {
    alertElement.classList.remove("show");
  }, 3000);
}

document.getElementById("playButton").addEventListener("click", function (e) {
  console.log("HELo")
  showBootstrapAlert();
});
