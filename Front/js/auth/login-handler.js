const tryFormPost = async () => {
  const username = document.getElementById("usernameLoginForm").value;
  const password = document.getElementById("password").value;

  token = await getCsrfToken();

  console.log(username, password, token)

  fetch("http://localhost:8000/api/user/login/", {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({
      username: username,
      password: password,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "ok") {
        sessionStorage.setItem("username", username);
        sessionStorage.setItem("jwt", data.token);
        window.location.href = "/";
      } else {
        console.error("Error:", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

const form = document.getElementById("loginForm");
form.addEventListener("submit", function (event) {
  event.preventDefault();
  tryFormPost();
});
