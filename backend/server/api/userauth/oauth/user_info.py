import requests
import json
from ..models import CustomUser
from django.core.files.storage import default_storage
import io



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


def get_intra_profile_picture(user_info: dict):
    response = requests.get(user_info["image"])
    if response.status_code != 200:
        return
    save = user_info["image"].split('/')[-1]
    file_name = default_storage.save(f"avatars/{save}", io.BytesIO(response.content))
    return file_name


def get_or_create_user_oauth(user_info: dict) -> CustomUser:
    login = user_info.get('login')

    try:
        user = CustomUser.objects.get(login=login)
        return user

    except CustomUser.DoesNotExist:
        username = login
        fullname = user_info.get('fullname')
        email = user_info.get('email')
        pic = get_intra_profile_picture(user_info)
        if not CustomUser.objects.filter(username=username).exists():
            user = CustomUser.objects.create_user(
                username=username,
                login=username,
                fullname=fullname,
                email=email,
                avatar=pic
            )
            user.set_unusable_password()
            user.save()
            return user

        suffix = 2
        while CustomUser.objects.filter(username=f'{username}{suffix}').exists():
            suffix += 1

        pic = get_intra_profile_picture(user_info)
        user = CustomUser.objects.create_user(
            username=f'{username}{suffix}',
            login=login,
            fullname=fullname,
            email=email,
            avatar=pic
        )
        user.set_unusable_password()
        user.save()
        return user
