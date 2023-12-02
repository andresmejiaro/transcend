let userID = 0;

const getUserId = async () => {
  try {
    const username = sessionStorage.getItem("username");
    const url = `${window.DJANGO_API_BASE_URL}/api/get_user_id/${username}`;
    const response = await makeRequest(true, url);

    if (response) {
      return response.user_id;
    } else {
      console.error("Error getting user ID:", response.message);
      return null;
    }
  } catch (error) {
    console.error("Error getting user ID:", error.message);
    return null;
  }
};

const load2FA = async () => {
  try {
    const id = await getUserId();
    userID = id;

    if (id !== null) {
      const url = `${window.DJANGO_API_BASE_URL}/api/display_qr_code/${id}/`;
      const response = await makeRequest(true, url);

      if (response) {
        document.getElementById(
          "qrcodeImage"
        ).src = `${window.DJANGO_API_BASE_URL}/${response.qrcode_path}`;
      } else {
        console.error("Error loading 2FA:", response.message);
      }
    } else {
      console.error("User ID is null");
    }
  } catch (error) {
    console.error("Error loading 2FA:", error.message);
  }
};

async function verifyTOTP() {
  const totpCode = document.getElementById("totpCode").value;

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/verify_totp_code/`;
    const response = await makeRequest(true, url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: JSON.stringify({
        user_id: userID,
        totp_code: totpCode,
      }),
    });

    document.getElementById("statusMessage").innerText = response.message;

    if (response.ok) {
      window.location.href = "/home";
      // Handle further actions based on the verification result
    }
  } catch (error) {
    console.error("Error verifying TOTP:", error.message);
    // Handle error actions, e.g., display an error message
  }
}

async function enable2FA() {
  try {
    const id = await getUserId();
    userID = id;

    const url = `${window.DJANGO_API_BASE_URL}/api/enable_2fa/${userID}/`;
    const response = await makeRequest(true, url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    document.getElementById(
      "qrcodeImage"
    ).src = `${window.DJANGO_API_BASE_URL}/${response.qrcode_path}`;
    document.getElementById("statusMessage").innerText = response.message;
  } catch (error) {
    console.error("Error enabling 2FA:", error.message);
  }
}

async function disable2FA() {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/disable_2fa/${userID}/`;
    const response = await makeRequest(true, url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    document.getElementById("statusMessage").innerText = response.message;
  } catch (error) {
    console.error("Error disabling 2FA:", error.message);
  }
}

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
  window.location.href = "/home-logged";
});
