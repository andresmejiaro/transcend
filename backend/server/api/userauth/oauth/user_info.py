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


def get_or_create_user_oauth(user_info: dict) -> CustomUser:
    login = user_info.get('login')

    try:
        user = CustomUser.objects.get(login=login)
        return user

    except CustomUser.DoesNotExist:
        username = login
        fullname = user_info.get('fullname')
        email = user_info.get('email')
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(
                username=username,
                login=username,
                fullname=fullname,
                email=email
            )
            user.set_unusable_password()
            user.save()
            return user

        suffix = 2
        while CustomUser.objects.filter(username=f'{username}{suffix}').exists():
            suffix += 1

        user = CustomUser.objects.create_user(
            username=f'{username}{suffix}',
            login=login,
            fullname=fullname,
            email=email
        )
        user.set_unusable_password()
        user.save()
        return user
