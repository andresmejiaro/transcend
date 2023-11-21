from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Tournaments, Matches
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

# Create your views here.

# Tournament CRUD views
def touprnament_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')

            if not (name):
                return JsonResponse({"status": "error", "message": "Name is missing"}, status=400)

            if Tournaments.objects.filter(name=name).exists():
                return JsonResponse({"status": "error", "message": "Tournament name already exists"}, status=400)

            tournament = Tournaments(name=name)
            tournament.save()
            response = JsonResponse({'status': 'ok', 'message': 'Tournament created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'

            return response

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def tournament_list(request):
    if request.method == 'GET':
        try:
            tournaments = Tournaments.objects.all()
            tournament_list = []
            for tournament in tournaments:
                tournament_list.append({'id': tournament.id, 'name': tournament.name})
            return JsonResponse({'status': 'ok', 'data': tournament_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def tournament_delete(request, tournament_id):
    if request.method == 'DELETE':
        try:
            tournament = Tournaments.objects.get(id=tournament_id)
            tournament.delete()
            return JsonResponse({'status': 'ok', 'message': 'Tournament deleted successfully'})
        except Tournaments.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only DELETE requests are allowed'}, status=400)

def tournament_update(request, tournament_id):
    tournament = get_object_or_404(Tournaments, pk=tournament_id)
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            new_name = data.get('name')

            if not new_name:
                return JsonResponse({"status": "error", "message": "Name is missing"}, status=400)

            tournament.name = new_name
            tournament.save()
            return JsonResponse({'status': 'ok', 'message': 'Tournament updated successfully'})
        except Tournaments.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

# Match CRUD views
# ... (previous code)

def match_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tournament_id = data.get('tournament_id')
            player1_id = data.get('player1')  # Change the variable name to avoid confusion
            player2_id = data.get('player2')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')
            active = data.get('active')

            if not (tournament_id and player1_id and player2_id and player1_score and player2_score and active):
                return JsonResponse({"status": "error", "message": "Some data is missing"}, status=400)
            if not Tournaments.objects.filter(id=tournament_id).exists():
                return JsonResponse({"status": "error", "message": "Tournament does not exist"}, status=400)

            # Convert player1_id and player2_id to User instances
            player1 = User.objects.get(id=player1_id)
            player2 = User.objects.get(id=player2_id)

            if not (player1 and player2):
                return JsonResponse({"status": "error", "message": "Invalid players"}, status=400)

            if not (player1_score >= 0 and player2_score >= 0):
                return JsonResponse({"status": "error", "message": "Score must be positive"}, status=400)
            if active not in [True, False]:
                return JsonResponse({"status": "error", "message": "Active must be a boolean"}, status=400)
            
            tournament = Tournaments.objects.get(id=tournament_id)
            match = Matches(tournament=tournament, player1=player1, player2=player2, player1_score=player1_score, player2_score=player2_score, active=active)
            match.save()
            response = JsonResponse({'status': 'ok', 'message': 'Match created successfully'})
            response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid player ID'}, status=400)
        except Tournaments.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

def match_list(request):
    if request.method == 'GET':
        try:
            matches = Matches.objects.all()
            match_list = []
            for match in matches:
                match_list.append({'id': match.id, 'tournament_id': match.tournament.id, 'player1': match.player1.id, 'player2': match.player2.id, 'player1_score': match.player1_score, 'player2_score': match.player2_score, 'active': match.active})
            return JsonResponse({'status': 'ok', 'data': match_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def match_delete(request, match_id):
    if request.method == 'DELETE':
        try:
            match = Matches.objects.get(id=match_id)
            match.delete()
            return JsonResponse({'status': 'ok', 'message': 'Match deleted successfully'})
        except Matches.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only DELETE requests are allowed'}, status=400)

def match_update(request, match_id):
    match = get_object_or_404(Matches, pk=match_id)
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            tournament_id = data.get('tournament_id')
            player1_id = data.get('player1')  # Change the variable name to avoid confusion
            player2_id = data.get('player2')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')
            active = data.get('active')

            if not (tournament_id and player1_id and player2_id and player1_score and player2_score and active):
                return JsonResponse({"status": "error", "message": "Some data is missing"}, status=400)
            if not Tournaments.objects.filter(id=tournament_id).exists():
                return JsonResponse({"status": "error", "message": "Tournament does not exist"}, status=400)
            if not User.objects.filter(id=player1_id).exists():
                return JsonResponse({"status": "error", "message": "Player1 does not exist"}, status=400)
            if not User.objects.filter(id=player2_id).exists():
                return JsonResponse({"status": "error", "message": "Player2 does not exist"}, status=400)
            if not (player1_score >= 0 and player2_score >= 0):
                return JsonResponse({"status": "error", "message": "Score must be positive"}, status=400)
            if active not in [True, False]:
                return JsonResponse({"status": "error", "message": "Active must be a boolean"}, status=400)

            tournament = Tournaments.objects.get(id=tournament_id)
            player1 = User.objects.get(id=player1_id)
            player2 = User.objects.get(id=player2_id)

            match.tournament = tournament
            match.player1 = player1
            match.player2 = player2
            match.player1_score = player1_score
            match.player2_score = player2_score
            match.active = active
            match.save()
            return JsonResponse({'status': 'ok', 'message': 'Match updated successfully'})
        except Matches.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid player ID'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
    return JsonResponse({'status': 'error', 'message': 'Only PUT requests are allowed'}, status=400)
