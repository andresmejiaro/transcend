async function handleCallback() {
	const urlParams = new URLSearchParams(window.location.search);
	const authorizationCode = urlParams.get("code");

	if (authorizationCode) {
		try {
			const url = `${window.DJANGO_API_BASE_URL}/api/oauth/login/`;

      const options = {
        method: "POST",
        mode: "cors",
        credentials: "include",
        body: JSON.stringify({
          code: authorizationCode
        })
      };

			const csrfToken = getCSRFCookie();
			if (csrfToken) {
				options.headers = {
					...options.headers,
					"X-CSRFToken": csrfToken,
				};
			}

			const data = await makeRequest(false, url, options);
      if (data) {
        sessionStorage.setItem("jwt", data.token);
        window.location.href = "/play!";
      }
		} catch (error) {
			throw error;
		}
	}
}

handleCallback();
