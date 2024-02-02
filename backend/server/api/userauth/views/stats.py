from django.http import JsonResponse

from ..models import CustomUser
from api.tournament.models import Match
from api.tournament.models import Tournament
from api.jwt_utils import get_user_id_from_jwt_token
from django.db.models import Q
from django.shortcuts import get_object_or_404


def get_kpi(request):
    if request.method != 'GET':
        return JsonResponse({
            "status": "Method not allowed"
        }, status=405)

    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        try:
            _, token = authorization_header.split()
            user_id = get_user_id_from_jwt_token(token)
            print(user_id)
            user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=401)

    matches = Match.objects.filter(Q(player1=user) | Q(player2=user))
    matches = [x for x in matches if x.winner]
    # wins = matches.filter(winner=user)
    wins = [x for x in matches if x.winner == user]
    winrate = round(len(wins) / len(matches), 2) if len(matches) != 0 else 0
    tournament_wins = Tournament.objects.filter(winner=user)

    res = {
        "games_played": len(matches),
        "wins": len(wins),
        "winrate": winrate * 100,
        "tournaments_won": len(tournament_wins),
    }

    return JsonResponse(res)


def get_kpi_username(request, username):
    if request.method != 'GET':
        return JsonResponse({
            "status": "Method not allowed"
        }, status=405)

    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        try:
            _, token = authorization_header.split()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=401)
    
    user = get_object_or_404(CustomUser, username=username)

    matches = Match.objects.filter(Q(player1=user) | Q(player2=user))
    matches = [x for x in matches if x.winner]
    # wins = matches.filter(winner=user)
    wins = [x for x in matches if x.winner == user]
    winrate = round(len(wins) / len(matches), 2) if len(matches) != 0 else 0
    tournament_wins = Tournament.objects.filter(winner=user)

    res = {
        "games_played": len(matches),
        "wins": len(wins),
        "winrate": winrate * 100,
        "tournaments_won": len(tournament_wins),
    }

    return JsonResponse({'status': 'ok', 'data': res})