from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Tournament, Match, Round
from api.userauth.models import CustomUser as User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
import json
import math
import random

# Create your views here.

# Tournament CRUD views
def tournament_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            type = data.get('type', '1v1')
            end_date = data.get('end_date', None)
            round = data.get('round', 0)

            if not name:
                return JsonResponse({"status": "error", "message": "The 'name' field is required"}, status=422)

            players_ids = data.get('players', [])
            valid_players = validate_users_existence(players_ids)
            if not valid_players[0]:
                return valid_players[1]

            observers_ids = data.get('observers', [])
            valid_observers = validate_users_existence(observers_ids)
            if not valid_observers[0]:
                return valid_observers[1]

            tournament = Tournament(name=name, type=type, end_date=end_date, round=round)
            tournament.save()
            tournament.players.set(valid_players[1])
            tournament.observers.set(valid_observers[1])

            response = JsonResponse({'status': 'ok', 'tournament_id': tournament.id, 'message': 'Tournament created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            response['Access-Control-Allow-Origin'] = '*'  # Add this line for broader CORS support

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def validate_users_existence(user_ids):
    valid_users = []
    for user_id in user_ids:
        if not User.objects.filter(id=user_id).exists():
            return (False, JsonResponse({"status": "error", "message": f"Invalid user ID: {user_id}"}, status=400))
        valid_users.append(User.objects.get(id=user_id))
    return (True, valid_users)

def tournament_list(request):
    if request.method == 'GET':
        try:
            tournaments = Tournament.objects.all()
            tournament_list = []
            for tournament in tournaments:
                tournament_list.append({
                    'id': tournament.id,
                    'name': tournament.name,
                    'start_date': tournament.start_date,
                    'end_date': tournament.end_date,
                    'round': tournament.round,
                    'winner': tournament.winner.id if tournament.winner else None,
                    'players': [player.id for player in tournament.players.all()],
                    'observers': [observer.id for observer in tournament.observers.all()],            
                })
            return JsonResponse({'status': 'ok', 'data': tournament_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def tournament_operations(request, pk):
    tournament_instance = get_object_or_404(Tournament, pk=pk)

    if request.method == 'GET':
        # Retrieve tournament details
        try:
            tournament_detail = {
                'id': tournament_instance.id,
                'name': tournament_instance.name,
                'type': tournament_instance.type,
                'start_date': tournament_instance.start_date,
                'end_date': tournament_instance.end_date,
                'round': tournament_instance.round,
                'winner': tournament_instance.winner.id if tournament_instance.winner else None, # 'None' if 'winner' is 'None
                'players': [player.id for player in tournament_instance.players.all()],
                'observers': [observer.id for observer in tournament_instance.observers.all()],
            }
            return JsonResponse({'status': 'ok', 'data': tournament_detail})
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'DELETE':
        # Delete tournament
        try:
            tournament_instance.delete()
            return JsonResponse({'status': 'ok', 'message': 'Tournament deleted successfully'})
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'PUT':
        # Update tournament
        try:
            data = json.loads(request.body)
            new_name = data.get('name')
            new_type = data.get('type', None)
            new_start_date = data.get('start_date', None)
            new_end_date = data.get('end_date', None)
            new_players_ids = data.get('players', [])
            new_observers_ids = data.get('observers', [])

            if new_name:
                tournament_instance.name = new_name
            if new_type:
                tournament_instance.type = new_type
            if new_start_date:
                tournament_instance.start_date = new_start_date
            if new_end_date:
                tournament_instance.end_date = new_end_date

            new_players = []
            if new_players_ids:
                for player_id in new_players_ids:
                    if not User.objects.filter(id=player_id).exists():
                        return JsonResponse({"status": "error", "message": "Invalid player ID"}, status=400)
                    new_players.append(User.objects.get(id=player_id))

            new_observers = []
            if new_observers_ids:
                for observer_id in new_observers_ids:
                    if not User.objects.filter(id=observer_id).exists():
                        return JsonResponse({"status": "error", "message": "Invalid observer ID"}, status=400)
                    new_observers.append(User.objects.get(id=observer_id))

            tournament_instance.save()
            tournament_instance.players.set(new_players_ids)
            tournament_instance.observers.set(new_observers_ids)
            return JsonResponse({'status': 'ok', 'message': 'Tournament updated successfully'})
        
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': f'Unsupported HTTP method: {request.method}'}, status=400)

def tournament_rounds(request, pk):
    if request.method == 'GET':
        try:
            tournament = Tournament.objects.get(id=pk)
            rounds = Round.objects.filter(tournament=tournament)
            round_list = []
            for round in rounds:
                round_list.append({
                    'id': round.id,
                    'tournament': round.tournament.id,
                    'round_number': round.round_number,
                    'matches': [match.id for match in round.matches.all()]
                })
            return JsonResponse({'status': 'ok', 'data': round_list})
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:

            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)
# -----------------------------

# Match CRUD views
@csrf_exempt
def match_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player1_id = data.get('player1')
            player2_id = data.get('player2', None)
            player1_score = data.get('player1_score', 0)
            player2_score = data.get('player2_score', 0)
            winner_id = data.get('winner', None)
            active = data.get('active', True)

            # Convert player1_id and player2_id to User instances
            try:
                player1 = User.objects.get(id=player1_id)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid player 1 ID'}, status=400)
            
            try:
                player2 = User.objects.get(id=player2_id)
            except User.DoesNotExist:
                player2 = None
            
            # if not (player1 and player2):
            #     return JsonResponse({"status": "error", "message": "Invalid players"}, status=400)
            winner_user = None
            if winner_id is not None:
                try:
                    winner_user = User.objects.get(id=winner_id)
                    if winner_user not in [player1, player2]:
                        return JsonResponse({"status": "error", "message": "Winner must be one of the players"}, status=400)
                except User.DoesNotExist:
                    return JsonResponse({"status": "error", "message": "Winner does not exist"}, status=400)
            if not (player1_score >= 0 and player2_score >= 0):
                return JsonResponse({"status": "error", "message": "Score must be positive"}, status=400)
            if active not in [True, False]:
                return JsonResponse({"status": "error", "message": "Active must be a boolean"}, status=400)
            
            match = Match(
                player1=player1,
                player2=player2,
                player1_score=player1_score,
                player2_score=player2_score, 
                winner=winner_user,
                date_played=timezone.now(), 
                active=active
                )
            match.save()
            response = JsonResponse({'status': 'ok', 'message': 'Match created successfully', 'match_id': match.id})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid player ID'}, status=400)
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def match_list(request):
    if request.method == 'GET':
        try:
            matches = Match.objects.all()
            match_list = []

            for match in matches:
                match_data = {
                    'id': match.id,
                    'player1': match.player1.id if match.player1 else None,
                    'player2': match.player2.id if match.player2 else None,
                    'player1_score': match.player1_score,
                    'player2_score': match.player2_score,
                    'winner': match.winner.id if match.winner else None,
                    'date_played': match.date_played,
                    'active': match.active
                }
                match_list.append(match_data)

            return JsonResponse({'status': 'ok', 'data': match_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def match_available(request):
    if request.method == 'GET':
        try:
            matches = Match.objects.all()

            for match in matches:
                if match.player2 is None:
                    return JsonResponse({'status': 'ok', 'id': match.id})
                
            return JsonResponse({'status': 'ok', 'data': None})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

@csrf_exempt
def match_operations(request, pk):
    match_instance = get_object_or_404(Match, pk=pk)

    if request.method == 'GET':
        # Retrieve match details
        try:
            match_detail = {
                'id': match_instance.id,
                'player1': match_instance.player1.id,
                'player2': match_instance.player2.id if match_instance.player2 else None,
                'player1_score': match_instance.player1_score,
                'player2_score': match_instance.player2_score,
                'winner': match_instance.winner.id if match_instance.winner else None,
                'date_played': match_instance.date_played,
                'active': match_instance.active
            }
            return JsonResponse({'status': 'ok', 'data': match_detail})
        except Match.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'DELETE':
        # Delete match
        try:
            match_instance.delete()
            return JsonResponse({'status': 'ok', 'message': 'Match deleted successfully'})
        except Match.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            player1_id = data.get('player1')
            player2_id = data.get('player2')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')
            winner_id = data.get('winner')
            date_played = data.get('date_played', None)
            active = data.get('active')

            # Assuming match_instance is already defined based on your logic
            match_instance = Match.objects.get(pk=pk)

            if 'player1' in data:
                match_instance.player1 = User.objects.get(id=player1_id)
            if 'player2' in data:
                match_instance.player2 = User.objects.get(id=player2_id)
            if 'player1_score' in data:
                match_instance.player1_score = player1_score
            if 'player2_score' in data:
                match_instance.player2_score = player2_score
            if 'winner' in data:
                if winner_id is not None:
                    winner_user = User.objects.get(id=winner_id)
                    if winner_user not in [match_instance.player1, match_instance.player2]:
                        return JsonResponse({"status": "error", "message": "Winner must be one of the players"}, status=400)
                    match_instance.winner = winner_user
                else:
                    match_instance.winner = None
            if 'date_played' in data:
                match_instance.date_played = date_played
            if 'active' in data:
                if active not in [True, False]:
                    return JsonResponse({"status": "error", "message": "Active must be a boolean"}, status=400)
                match_instance.active = active

            match_instance.save()
            return JsonResponse({'status': 'ok', 'message': 'Match updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid player ID'}, status=400)
        except Match.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# -----------------------------

# Round CRUD views
def round_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tournament_id = data.get('tournament')
            round_number = data.get('round_number')
            matches_ids = data.get('matches', [])

            if not Tournament.objects.filter(id=tournament_id).exists():
                return JsonResponse({"status": "error", "message": "Invalid tournament ID"}, status=400)
            if not round_number:
                return JsonResponse({"status": "error", "message": "Round number is missing"}, status=400)
            if not matches_ids:
                return JsonResponse({"status": "error", "message": "Matches are missing"}, status=400)

            tournament = Tournament.objects.get(id=tournament_id)
            matches = []
            for match_id in matches_ids:
                if not Match.objects.filter(id=match_id).exists():
                    return JsonResponse({"status": "error", "message": "Invalid match ID"}, status=400)
                matches.append(Match.objects.get(id=match_id))

            round = Round(tournament=tournament, round_number=round_number)
            round.save()
            round.matches.set(matches)

            response = JsonResponse({'status': 'ok', 'message': 'Round created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def round_list(request):
    if request.method == 'GET':
        try:
            rounds = Round.objects.all()
            round_list = []
            for round in rounds:
                round_list.append({
                    'id': round.id,
                    'tournament': round.tournament.id,
                    'round_number': round.round_number,
                    'matches': [match.id for match in round.matches.all()]                
                })
            return JsonResponse({'status': 'ok', 'data': round_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def round_operations(request, pk):
    round_instance = get_object_or_404(Round, pk=pk)

    if request.method == 'GET':
        # Retrieve round details
        try:
            round_detail = {
                'id': round_instance.id,
                'tournament': round_instance.tournament.id,
                'round_number': round_instance.round_number,
                'matches': [match.id for match in round_instance.matches.all()]
            }
            return JsonResponse({'status': 'ok', 'data': round_detail})
        except Round.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Round does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'DELETE':
        # Delete round
        try:
            round_instance.delete()
            return JsonResponse({'status': 'ok', 'message': 'Round deleted successfully'})
        except Round.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Round does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'PUT':
        # Update round
        try:
            data = json.loads(request.body)
            new_tournament_id = data.get('tournament')
            new_round_number = data.get('round_number')
            new_matches_ids = data.get('matches', [])

            if new_tournament_id:
                if not Tournament.objects.filter(id=new_tournament_id).exists():
                    return JsonResponse({"status": "error", "message": "Invalid tournament ID"}, status=400)
                round_instance.tournament = Tournament.objects.get(id=new_tournament_id)
            if new_round_number:
                round_instance.round_number = new_round_number
            if new_matches_ids:
                new_matches = []
                for match_id in new_matches_ids:
                    if not Match.objects.filter(id=match_id).exists():
                        return JsonResponse({"status": "error", "message": "Invalid match ID"}, status=400)
                    new_matches.append(Match.objects.get(id=match_id))
                round_instance.matches.set(new_matches)
            round_instance.save()
            return JsonResponse({'status': 'ok', 'message': 'Round updated successfully'})
        except Round.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Round does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': f'Unsupported HTTP method: {request.method}'}, status=400)
# -----------------------------

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
# -----------------------------

# Tournament Matchmaking
def create_matches(sorted_players):
    matches = []
    num_players = len(sorted_players)

    # Adjust the range to handle odd number of players
    for i in range(0, num_players - 1, 2):
        player1 = sorted_players[i]
        player2 = sorted_players[i + 1]

        player1_score = 0
        player2_score = 0
        winner = None

        match = Match(
            player1=player1,
            player2=player2,
            player1_score=player1_score,
            player2_score=player2_score,
            winner=winner,
            date_played=timezone.now(),
            active=True
        )
        
        match.save()
        matches.append(match)

    return matches

def create_round(tournament, matches):
    new_round = Round(tournament=tournament, round_number=tournament.round + 1)
    new_round.save()
    new_round.matches.set(matches)

def calculate_rounds(num_players):
    return math.ceil(math.log2(num_players))

def calculate_player_score(player, tournament=None):
    if not tournament:
        return 0

    latest_round = tournament.rounds.last()  # Get the latest round

    if latest_round:
        matches = latest_round.matches.filter(Q(player1=player) | Q(player2=player))
        player_score = sum(1 for match in matches if match.winner == player)
    else:
        player_score = 0

    return player_score


# Actual matchmaking view
def game_matchmaking(request, pk):
    if request.method == 'GET':
        try:
            tournament = Tournament.objects.get(id=pk)

            if tournament is None:
                return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)

            players = tournament.players.all()

            # Determine if there is a player sitting out
            if players.count() % 2 != 0:
                sit_out_player = random.choice(players)
            else:
                sit_out_player = None

            num_rounds = calculate_rounds(players.count())
            if tournament.round >= num_rounds:
                winner = max(players, key=lambda player: calculate_player_score(player, tournament=tournament))
                tournament.winner = winner
                tournament.end_date = timezone.now()
                tournament.save()
                return JsonResponse({'status': 'ok', 'message': f'Tournament winner is {winner.username}'})

            sorted_players = players.order_by('id')
            
            if sit_out_player:
                sorted_players = [player for player in sorted_players if player != sit_out_player]
            print(sit_out_player)
            print(sorted_players)

            matches = []
            if tournament.round == 1:
                matches = create_matches(sorted_players)
            else:
                player_scores = {player.id: calculate_player_score(player, tournament=tournament) for player in players}
                sorted_players = sorted(sorted_players, key=lambda player: player_scores[player.id])
                matches = create_matches(sorted_players)

            create_round(tournament, matches)

            tournament.round += 1
            tournament.save()

            # Prepare the response with match details
            match_list = [{'match_id': match.id, 'total_rounds': num_rounds, 'player1_id': match.player1.id, 'player2_id': match.player2.id} for match in matches]

            return JsonResponse({
                'status': 'ok', 'message': 'Matchmaking successful',
                'sit_out_player': sit_out_player.id if sit_out_player else None,
                'matches': match_list,
                'total_rounds': num_rounds,
                })

        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=377)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=366)

    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=355)
# -----------------------------