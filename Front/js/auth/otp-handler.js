let userID = 0;

const getUserId = async () => {
  const username = sessionStorage.getItem("username");

  try {
    const response = await fetch(
      `http://localhost:8000/api/get_user_id/${username}`
    );
    const data = await response.json();
    return data.user_id;
  } catch (error) {
    console.error("Error getting user ID:", error);
    return null;
  }
};

const load2FA = async () => {
  try {
    const id = await getUserId();
    userID = id;
    if (id !== null) {
      const response = await fetch(
        `http://localhost:8000/api/display_qr_code/${id}/`
      );
      const data = await response.json();

      console.log(data);
      document.getElementById("qrcodeImage").src =
        "http://localhost:8000/" + data.qrcode_path;
    } else {
      console.error("User ID is null");
    }
  } catch (error) {
    console.error("Error loading 2FA:", error);
  }
};

function verifyTOTP() {
  const totpCode = document.getElementById("totpCode").value;

  fetch("http://localhost:8000/api/verify_totp_code/", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: JSON.stringify({
      user_id: userID,
      totp_code: totpCode,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("statusMessage").innerText = data.message;
      window.location.href = "/home";
      // Handle further actions based on the verification result
    });
}

async function enable2FA() {
  userID = await getUserId();
  await fetch(`http://localhost:8000/api/enable_2fa/${userID}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("qrcodeImage").src = data.qrcode_path;
      document.getElementById("statusMessage").innerText = data.message;
    });
}

async function disable2FA() {
  await fetch(`http://localhost:8000/api/disable_2fa/${userID}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("statusMessage").innerText = data.message;
    });
}


const loadGoogleAuth = async () => {
  document.getElementById("gaDiv").style.display = "block";
  await enable2FA();
  await load2FA();
}

document.getElementById("startGA").addEventListener("click", function (e) {
  e.preventDefault();
  loadGoogleAuth();
});


const removeGA = async () => {
  document.getElementById("gaDiv").style.display = "none";
  await disable2FA();
}

document.getElementById("removeGA").addEventListener("click", function (e) {
  e.preventDefault();
  removeGA();
});


document.getElementById("noGA").addEventListener("click", function (e) {
  e.preventDefault();
  removeGA();
  window.location.href = "/home-logged"
});