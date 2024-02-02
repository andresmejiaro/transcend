from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Tournament, Match, Round
from api.userauth.models import CustomUser as User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from api.jwt_utils import get_user_id_from_jwt_token
import json
import math
import random
from api.userauth.models import CustomUser
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

# Create your views here.

# Tournament CRUD views


def tournament_create(request):
    if request.method == 'POST':
        try:

            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    _, token = authorization_header.split()
                    user_id = get_user_id_from_jwt_token(token)
                    user = CustomUser.objects.get(id=user_id)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=401)

            tournament_admin = user

            data = json.loads(request.body)
            name = data.get('name')
            type = data.get('type', '1v1')
            end_date = data.get('end_date', None)
            round = data.get('round', 0)


            if not name:
                return JsonResponse({"status": "error", "message": "The 'name' field is required"}, status=422)

            players_ids = data.get('players', [user_id])
            valid_players = validate_users_existence(players_ids)
            if not valid_players[0]:
                return valid_players[1]

            observers_ids = data.get('observers', [])
            valid_observers = validate_users_existence(observers_ids)
            if not valid_observers[0]:
                return valid_observers[1]

            tournament = Tournament(
                name=name, type=type, end_date=end_date, round=round, tournament_admin=tournament_admin)
            tournament.save()
            tournament.players.set(valid_players[1])
            tournament.observers.set(valid_observers[1])

            response = JsonResponse(
                {'status': 'ok', 'tournament_id': tournament.id, 'message': 'Tournament created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            # Add this line for broader CORS support
            response['Access-Control-Allow-Origin'] = '*'

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
                # 'None' if 'winner' is 'None
                'winner': tournament_instance.winner.id if tournament_instance.winner else None,
                'players': [player.id for player in tournament_instance.players.all()],
                'observers': [observer.id for observer in tournament_instance.observers.all()],
                'tournament_admin': tournament_instance.tournament_admin_id
            }
            return JsonResponse({'status': 'ok', 'data': tournament_detail})
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            action = data.get('action', None)

            if action == 'delete_tournament':
                tournament_instance.delete()
                return JsonResponse({'status': 'ok', 'message': 'Tournament deleted successfully'})
            elif action == 'remove_player':
                player_to_remove_id = data.get('player_to_remove', None)

                if player_to_remove_id is not None:
                    player_to_remove = User.objects.get(id=player_to_remove_id)
                    tournament_instance.players.remove(player_to_remove)
                    tournament_instance.save()
                    return JsonResponse({'status': 'ok', 'message': 'Player removed from the tournament successfully'})
                else:
                    return JsonResponse({'status': 'error', 'message': 'Player ID to remove is missing from the request'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid action in the request'}, status=400)

        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Player to remove does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    elif request.method == 'PUT':
        # Update tournament
        try:
            data = json.loads(request.body)
            new_name = data.get('name', None)
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

            # Update Players
            existing_players_ids = [
                player.id for player in tournament_instance.players.all()]
            updated_players_ids = list(
                set(existing_players_ids + new_players_ids))
            tournament_instance.players.set(updated_players_ids)

            # Update Observers
            existing_observers_ids = [
                observer.id for observer in tournament_instance.observers.all()]
            updated_observers_ids = list(
                set(existing_observers_ids + new_observers_ids))
            tournament_instance.observers.set(updated_observers_ids)

            tournament_instance.save()
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
            response = JsonResponse(
                {'status': 'ok', 'message': 'Match created successfully', 'match_id': match.id})
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

            response = JsonResponse(
                {'status': 'ok', 'message': 'Round created successfully'})
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
                round_instance.tournament = Tournament.objects.get(
                    id=new_tournament_id)
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

            user = User(username=username, email=email,
                        first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save()
            response = JsonResponse(
                {'status': 'ok', 'message': 'User created successfully'})
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

def user_all_matches(request):
    if request.method == 'GET':
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    _, token = authorization_header.split()
                    user_id = get_user_id_from_jwt_token(token)
                    print(user_id)
                    user = User.objects.get(id=user_id)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=401)
                
            # user = User.objects.get(id=pk)
                
            matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
                
            match_list = []
            for match in matches:
                if match.winner:
                    match_list.append({
                        'id': match.id,
                        'player1': {
                            "id": match.player1.id,
                            "username": match.player1.username,
                        },
                        'player2': {
                            "id": match.player2.id,
                            "username": match.player2.username,
                        },
                        'player1_score': match.player1_score,
                        'player2_score': match.player2_score,
                        'winner': match.winner.username if match.winner else None,
                        'date_played': match.date_played,
                        'active': match.active
                    })
            match_list.reverse()
            return JsonResponse({'status': 'ok', 'data': match_list})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)


def user_all_matches_username(request, username):
    if request.method == 'GET':
        try:
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                try:
                    _, token = authorization_header.split()
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=401)
                
            user = get_object_or_404(CustomUser, username=username)
                
            matches = Match.objects.filter(player1=user) | Match.objects.filter(player2=user)
                
            match_list = []
            for match in matches:
                if match.winner:
                    match_list.append({
                        'id': match.id,
                        'player1': {
                            "id": match.player1.id,
                            "username": match.player1.username,
                        },
                        'player2': {
                            "id": match.player2.id,
                            "username": match.player2.username,
                        },
                        'player1_score': match.player1_score,
                        'player2_score': match.player2_score,
                        'winner': match.winner.username if match.winner else None,
                        'date_played': match.date_played,
                        'active': match.active
                    })
            match_list.reverse()
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
            tournaments = Tournament.objects.filter(
                players=user) | Tournament.objects.filter(observers=user)
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
def get_match_info(request, *args, **kwargs):
    if request.method == 'GET':
        try:
            match_object = Match.objects.get(id=kwargs['match_id'])
            player1_info = {
                "id": match_object.player1.id,
                "username": match_object.player1.username,
                "score": match_object.player1_score
            }
            player2_info = {
                "id": match_object.player2.id,
                "username": match_object.player2.username,
                "score": match_object.player2_score,
            }
            winner_info = None
            if match_object.winner:
                winner_info = {
                    "id": match_object.winner.id,
                    "username": match_object.winner.username
                }

            res = {
                "match_id": match_object.id,
                "player1": player1_info,
                "player2": player2_info,
                "winner": winner_info,
                "date_played": match_object.date_played
            }
            return JsonResponse(res)
        except Match.DoesNotExist:
            return JsonResponse({
                "message": "Match not found"
            }, status=404)
    return JsonResponse({
        "message": "Method not allowed"
    }, status=405)

def list_joinable_tournaments(request, *args, **kwargs):
    if request.method == 'GET':
        try:
            tournaments = Tournament.objects.filter(joinable=True, public=True)
            tournament_list = [
                {
                    'id': tournament.id,
                    'name': tournament.name,
                    'players': list(tournament.players.values_list('id', flat=True)),
                }
                for tournament in tournaments
            ]
            return JsonResponse({'status': 'ok', 'data': tournament_list}, status=200)
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)

def get_tournament_by_name(request, *args, **kwargs):
    if request.method == 'GET':
        try:
            tournament = Tournament.objects.get(name=kwargs['name'])
            # If tournament is not joinable, return error
            if not tournament.joinable:
                return JsonResponse({'status': 'error', 'message': 'Tournament is not joinable or full'}, status=400)
            tournament_info = {
                'id': tournament.id,
                'name': tournament.name,
                'players': list(tournament.players.values_list('id', flat=True)),
            }
            return JsonResponse({'status': 'ok', 'data': tournament_info}, status=200)
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred'}, status=500)
