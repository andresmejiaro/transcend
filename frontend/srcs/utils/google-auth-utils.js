const load2FA = async () => {
  try {
    const id = await getUserId();

    if (id !== null) {
      const url = `${window.DJANGO_API_BASE_URL}/api/display_qr_code/${id}/`;
      const response = await makeRequest(true, url, {
        method: "GET",
        mode: "cors",
        credentials: "include",
      });
      console.log(response);
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
  const id = await getUserId();

  if (id == null) return;

  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/verify_totp_code/`;
    const response = await makeRequest(true, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: JSON.stringify({
        user_id: id,
        totp_code: totpCode,
      }),
    });

	const status = response.status;
    const statusTotp = document.getElementById("statusMessage");
    if (status == "error")
      statusTotp.style.color = "red";
    else
      statusTotp.style.color = "green";
    statusTotp.innerText = response.message;

  } catch (error) {
    console.error("Error verifying TOTP:", error.message);
  }
}

async function enable2FA() {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/enable_2fa/`;
    const response = await makeRequest(true, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    document.getElementById(
      "qrcodeImage"
    ).src = `${window.DJANGO_API_BASE_URL}/${response.qrcode_path}`;
    document.getElementById("statusMessage").innerText = response.message;
    return response;
  } catch (error) {
    console.error("Error enabling 2FA:", error.message);
  }
}

async function disable2FA() {
  try {
	console.log("DISABLE")
    const id = await getUserId();
    const userID = id;
    if (id == null) {
      console.error("User ID is null");
      return;
    }
    const url = `${window.DJANGO_API_BASE_URL}/api/disable_2fa/${userID}/`;
    const response = await makeRequest(true, url, {
      method: "POST",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
	console.log(response)

    document.getElementById("statusMessage").innerText = response.message;
  } catch (error) {
    console.error("Error disabling 2FA:", error.message);
  }
}
