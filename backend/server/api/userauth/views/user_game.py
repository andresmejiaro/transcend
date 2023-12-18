from django.http import JsonResponse
from api.tournament.models.tournament_model import Tournament
from api.tournament.models.match_model import Match
from api.userauth.models import CustomUser as User

def user_all_matches(request, pk):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=pk)
            matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
            match_list = []
            for match in matches:
                match_list.append({
                    'id': match.id,
                    'player1': match.player1.id,
                    'player2': match.player2.id,
                    'player1_score': match.player1_score,
                    'player2_score': match.player2_score,
                    'winner': match.winner.id if match.winner else None,
                    'date_played': match.date_played,
                    'active': match.active
                    })
            return JsonResponse({'status': 'ok', 'data': match_list})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def user_all_tournaments(request, pk):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=pk)
            tournaments = Tournament.objects.filter(players=user) | Tournament.objects.filter(observers=user)
            tournament_list = []
            for tournament in tournaments:
                tournament_list.append({
                    'id': tournament.id,
                    'name': tournament.name,
                    'start_date': tournament.start_date,
                    'end_date': tournament.end_date,
                    'round': tournament.round,
                    'players': [player.id for player in tournament.players.all()],
                    'observers': [observer.id for observer in tournament.observers.all()],            
                })
            return JsonResponse({'status': 'ok', 'data': tournament_list})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def user_stats(request, pk):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=pk)
            tournaments = Tournament.objects.filter(players=user)
            tournament_list = []

            matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
            match_list = []

            total_match_wins = 0
            total_tournament_wins = 0

            for tournament in tournaments:
                tournament_list.append({
                    'id': tournament.id,
                    'name': tournament.name,
                    'start_date': tournament.start_date,
                    'round': tournament.round,
                    'players': [player.id for player in tournament.players.all()],        
                })
                if tournament.winner == user:
                    total_tournament_wins += 1

            for match in matches:
                match_list.append({
                    'id': match.id,
                    'player1': match.player1.id,
                    'player2': match.player2.id,
                    'player1_score': match.player1_score,
                    'player2_score': match.player2_score,
                    'winner': match.winner.id if match.winner else None,
                    'date_played': match.date_played,
                    })
                if match.winner == user:
                    total_match_wins += 1
                
            formated_reponse = {
                'id': user.id,
                'username': user.username,
                'ELO': user.ELO,
                'total_match_wins': total_match_wins,
                'total_tournament_wins': total_tournament_wins,
                'tournaments': tournament_list,
                'matches': match_list
            }
                
            return JsonResponse({'status': 'ok', 'data': formated_reponse})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)
# -----------------------------