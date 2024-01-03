import requests
import json
from ..models import CustomUser


def get_user_info(access_token: str) -> dict:
    url = "https://api.intra.42.fr/v2/me"
    response = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})

    if response.status_code != 200:
        return {}

    loaded = response.json()

    return {
        "login": loaded.get("login"),
        "email": loaded.get("email"),
        "fullname": loaded.get("usual_full_name"),
        "image": loaded["image"]["link"]
    }


def get_or_create_user(user_info: dict) -> CustomUser:
    user, created = CustomUser.objects.get_or_create(
        username=user_info.get("login"),
        email=user_info.get("email"),
        fullname=user_info.get("fullname")
    )

    return user
