const tryFormPost = async () => {
  const username = document.getElementById("usernameLoginForm").value;
  const password = document.getElementById("password").value;

  const placeholderPassword = "AUTH0_USER_NO_PASSWORD";
  if (password == placeholderPassword) {
    console.log("invalid password autho");
    return;
  }
  try {
    const token = await getCsrfToken();
    const response = await fetch("http://localhost:8000/api/user/login/", {
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
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    if (data.status === "ok") {
      sessionStorage.setItem("username", username);
      sessionStorage.setItem("jwt", data.token);
      window.location.href = "/home";
    } else {
      console.error("Error:", data.message);
      displayError(data.message);
    }
  } catch (error) {
    console.error("Error:", error.message);
    displayError("Invalid credentials. Please try again.");
  }
};

function displayError(message) {
  console.log("helo");
  const errorAlert = document.getElementById("errorAlert");
  errorAlert.textContent = message;
  errorAlert.style.display = "block";
}

const form = document.getElementById("loginForm");
form.addEventListener("submit", function (event) {
  event.preventDefault();
  tryFormPost();
});
