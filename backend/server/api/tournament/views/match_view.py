from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from api.userauth.models import CustomUser as User
from api.tournament.models.tournament_model import Tournament
from api.tournament.models.match_model import Match
import json
from django.utils import timezone

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