const getMatchInfo = async (matchId) => {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/match/${matchId}/`;
    const options = {
      method: "GET",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
    };

    const data = await makeRequest(true, url, options);
    console.log(data);
    if (data.status == "ok") {
      return data;
    }

    return null;
  } catch (error) {
    console.error("Error:", error.message);
  }
};

// Function to update the match in the database
const updateMatchInDb = async (matchId, player2Id) => {
  try {
    const url = `${window.DJANGO_API_BASE_URL}/api/match/${matchId}/`;
    const options = {
      method: "PUT",
      mode: "cors",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        player2: player2Id,
      }),
    };

    const data = await makeRequest(true, url, options);
    console.log(data);
    if (data.status == "ok") {
      return data;
    }

    return null;
  } catch (error) {
    console.error("Error:", error.message);
  }
};
