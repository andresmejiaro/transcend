const tryLoginFormPost = async (data) => {
  const username = data.login;
  const password = "AUTH0_USER_NO_PASSWORD";
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

async function handleUpload(username, avatarUrl, token) {
  await fetch(`http://localhost:8000/api/user/update-avatar/${username}/`, {
    method: 'POST',
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({ avatar_url: avatarUrl }),
  })
    .then(response => response.json())
    .then(data => {
      // console.log(data);
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred while uploading the avatar.');
    });
}

const tryFormPost = async (data, token) => {
  const username = data.login;
  const fullname = data.displayname;
  const placeholderPassword = "AUTH0_USER_NO_PASSWORD";
  const email = data.email;

  await fetch("http://localhost:8000/api/user/signup/", {
    method: "POST",
    mode: "cors",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": token,
    },
    body: JSON.stringify({
      username: username,
      fullname: fullname,
      email: email,
      password: placeholderPassword,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "ok") {
        sessionStorage.setItem("username", username);
        sessionStorage.setItem("jwt", data.token);
      } else {
        console.error("Error:", data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

const getInfoMe = async (username) => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/get_user_id/${username}/`,
      {
        method: "GET",
        mode: "cors",
        credentials: "include",
      }
    );
    if (response.ok) {
      const data = await response.json();
      if (data.username) return true;
      else return false;
    } else return false;
  } catch (error) {
    return false;
  }
};

const intrahandler = async (userData) => {
  const exists = await getInfoMe(userData.login)
  token = await getCsrfToken();
  if (exists)
    tryLoginFormPost(userData);
  else {
    await tryFormPost(userData, token);
    await handleUpload(userData.login, userData.image.link, token);
    window.location.href = "/home";
  }
};

async function getUserInfo(accessToken) {
  const apiUrl = "https://api.intra.42.fr/v2/me";
  let userData = "";
  try {
    const response = await fetch(apiUrl, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    userData = await response.json();
    document.getElementById("user").innerHTML = userData.displayname;
    intrahandler(userData);
  } catch (error) {
    console.error("Error fetching user information:", error.message);
  }
}

async function handleCallback() {
  // Extract the authorization code from the URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const authorizationCode = urlParams.get("code");

  if (authorizationCode) {
    // Replace with your actual client ID, client secret, and redirect URI
    const clientId =
      "u-s4t2ud-ca3a07a81bac42c6b896a950e6bcce0a4072c14b72a8aea1e48f732b55dd58e2";
    const clientSecret =
      "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"; // Replace with your actual client secret
    const redirectUri = "http://localhost:3000/callback";

    const tokenUrl = "https://api.intra.42.fr/oauth/token";

    const response = await fetch(tokenUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `grant_type=authorization_code&client_id=${clientId}&client_secret=${clientSecret}&code=${authorizationCode}&redirect_uri=${encodeURIComponent(
        redirectUri
      )}`,
    });

    const tokenData = await response.json();

    getUserInfo(tokenData.access_token);
  }
}

handleCallback();
