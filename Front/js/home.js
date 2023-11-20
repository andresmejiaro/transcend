const getMeInfo = async () => {
  const token = sessionStorage.getItem("jwt");
  if (!token) {
    console.log("JWT token not found");
    return;
  }
  const username = sessionStorage.getItem("username");
  if (!username) {
    console.log("username not found");
    return;
  }
  const url = "http://localhost:8000/api/user/info-me-jwt/" + "?token=" + token + "&username=" + username;
  const options = {
    method: "GET",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  };
  const data = await makeRequest(url, options);
  if (data.status == "ok") {
    const usernameH = document.getElementById("home-username");
    const fullnameH = document.getElementById("home-fullname");

    usernameH.innerHTML = "username: " + data.user.username;
    fullnameH.innerHTML = "fullname: " + data.user.fullname;
  }
};

getMeInfo();
