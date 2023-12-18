from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from api.tournament.models.tournament_model import Tournament
from api.tournament.models.match_model import Match
from api.userauth.models import CustomUser as User
import json


# User CRUD views
def user_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            first_name = data.get('first_name')
            last_name = data.get('last_name')

            if not (username and password and email and first_name and last_name):
                return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username already exists"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email already exists"}, status=400)

            user = User(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save()
            response = JsonResponse({'status': 'ok', 'message': 'User created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def user_list(request):
    if request.method == 'GET':
        try:
            users = User.objects.all()
            user_list = []
            for user in users:
                user_list.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'password': user.password,
                    'staff_status': user.is_staff,
                    'user_status': user.is_active,
                })
            return JsonResponse({'status': 'ok', 'data': user_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def user_operations(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'GET':
        # Retrieve user details
        user_detail = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'password': user.password,
            'staff_status': user.is_staff,
            'user_status': user.is_active,
            'avatar': user.avatar.url if user.avatar else ''
        }
        return JsonResponse({'status': 'ok', 'data': user_detail})

    elif request.method == 'DELETE':
        # Delete user
        try:
            user.delete()
            return JsonResponse({'status': 'ok', 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'PUT':
        # Update user
        try:
            data = json.loads(request.body)
            new_username = data.get('username')
            new_password = data.get('password')
            new_email = data.get('email')
            new_first_name = data.get('first_name')
            new_last_name = data.get('last_name')

            if not (new_username and new_password and new_email and new_first_name and new_last_name):
                return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

            user.username = new_username
            user.set_password(new_password)
            user.email = new_email
            user.first_name = new_first_name
            user.last_name = new_last_name
            user.save()
            return JsonResponse({'status': 'ok', 'message': 'User updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': f'Unsupported HTTP method: {request.method}'}, status=400)

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