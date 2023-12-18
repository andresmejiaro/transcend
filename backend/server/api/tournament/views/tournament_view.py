from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from api.userauth.models import CustomUser as User
from api.tournament.models.tournament_model import Tournament
from api.tournament.models.round_model import Round
import json

# Tournament CRUD views
def tournament_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            type = data.get('type', '1v1')
            end_date = data.get('end_date', None)
            round = data.get('round', 0)
            tournament_admin_id = data.get('tournament_admin')

            tournament_admin = get_object_or_404(User, pk=tournament_admin_id)

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



            tournament = Tournament(name=name, type=type, end_date=end_date, round=round, tournament_admin=tournament_admin)
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
            existing_players_ids = [player.id for player in tournament_instance.players.all()]
            updated_players_ids = list(set(existing_players_ids + new_players_ids))
            tournament_instance.players.set(updated_players_ids)

            # Update Observers
            existing_observers_ids = [observer.id for observer in tournament_instance.observers.all()]
            updated_observers_ids = list(set(existing_observers_ids + new_observers_ids))
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