async function getUserInfo(accessToken) {
    const apiUrl = 'https://api.intra.42.fr/v2/me';

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const userData = await response.json();
        console.log('User Information:', userData);
        document.getElementById("user").innerHTML=userData.displayname
    } catch (error) {
        console.error('Error fetching user information:', error.message);
    }
}


async function handleCallback() {
    console.log("HELLO");
    // Extract the authorization code from the URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const authorizationCode = urlParams.get('code');

    if (authorizationCode) {
        // Replace with your actual client ID, client secret, and redirect URI
        const clientId = 'u-s4t2ud-ca3a07a81bac42c6b896a950e6bcce0a4072c14b72a8aea1e48f732b55dd58e2';
        const clientSecret = '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'; // Replace with your actual client secret
        const redirectUri = 'http://localhost:3000/callback';

        const tokenUrl = 'https://api.intra.42.fr/oauth/token';

        const response = await fetch(tokenUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `grant_type=authorization_code&client_id=${clientId}&client_secret=${clientSecret}&code=${authorizationCode}&redirect_uri=${encodeURIComponent(redirectUri)}`,
        });

        const tokenData = await response.json();

        console.log('Access Token:', tokenData.access_token);
        getUserInfo(tokenData.access_token)
    }
}

handleCallback();
