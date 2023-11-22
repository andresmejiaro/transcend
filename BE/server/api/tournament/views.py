from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Tournament, Match
from api.userauth.models import CustomUser as User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

# Create your views here.

# Tournament CRUD views
def tournament_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            start_date = data.get('start_date', None)
            end_date = data.get('end_date', None)
            match_ids = data.get('matches', [])

            if not name:
                return JsonResponse({"status": "error", "message": "Name is missing"}, status=400)

            matches = []
            for match_id in match_ids:
                matches.append(Match.objects.get(pk=match_id))
                if not matches[-1]:
                    return JsonResponse({"status": "error", "message": "Invalid match ID"}, status=400)

            tournament = Tournament(name=name, start_date=start_date, end_date=end_date)
            tournament.save()
            tournament.matches.set(matches)
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
            tournaments = Tournament.objects.all()
            tournament_list = []
            for tournament in tournaments:
                tournament_list.append({
                    'id': tournament.id,
                    'name': tournament.name,
                    'start_date': tournament.start_date,
                    'end_date': tournament.end_date,
                    'matches': [match.id for match in tournament.matches.all()]
                })
            return JsonResponse({'status': 'ok', 'data': tournament_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def tournament_delete(request, pk):
    if request.method == 'DELETE':
        tournament = get_object_or_404(Tournament, pk=pk)
        try:
            tournament.delete()
            return JsonResponse({'status': 'ok', 'message': 'Tournament deleted successfully'})
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only DELETE requests are allowed'}, status=400)

def tournament_update(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            new_name = data.get('name')
            new_start_date = data.get('start_date', None)
            new_end_date = data.get('end_date', None)
            new_match_ids = data.get('matches', [])

            matches = []
            for match_id in new_match_ids:
                matches.append(Match.objects.get(pk=match_id))
                if not matches[-1]:
                    return JsonResponse({"status": "error", "message": "Invalid match ID"}, status=400)

            if new_name:
                tournament.name = new_name
            if new_start_date:
                tournament.start_date = new_start_date
            if new_end_date:
                tournament.end_date = new_end_date
            tournament.matches.set(matches)
            tournament.save()
            return JsonResponse({'status': 'ok', 'message': 'Tournament updated successfully'})
        
        except Tournament.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Tournament does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=400)

# Match CRUD views
def match_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player1_id = data.get('player1')
            player2_id = data.get('player2')
            player1_score = data.get('player1_score', 0)
            player2_score = data.get('player2_score', 0)
            active = data.get('active')

            # Convert player1_id and player2_id to User instances
            player1 = User.objects.get(id=player1_id)
            player2 = User.objects.get(id=player2_id)

            if not (player1 and player2):
                return JsonResponse({"status": "error", "message": "Invalid players"}, status=400)

            if not (player1_score >= 0 and player2_score >= 0):
                return JsonResponse({"status": "error", "message": "Score must be positive"}, status=400)
            if active not in [True, False]:
                return JsonResponse({"status": "error", "message": "Active must be a boolean"}, status=400)
            
            match = Match(player1=player1, player2=player2, player1_score=player1_score, player2_score=player2_score, active=active)
            match.save()
            response = JsonResponse({'status': 'ok', 'message': 'Match created successfully'})
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
            Matchs = Match.objects.all()
            match_list = []
            for match in Matchs:
                match_list.append({
                    'id': match.id,
                    'player1': match.player1.id,
                    'player2': match.player2.id,
                    'player1_score': match.player1_score,
                    'player2_score': match.player2_score,
                    'active': match.active
                    })
            return JsonResponse({'status': 'ok', 'data': match_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=400)

def match_delete(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == 'DELETE':
        try:
            match.delete()
            return JsonResponse({'status': 'ok', 'message': 'Match deleted successfully'})
        except Match.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only DELETE requests are allowed'}, status=400)

def match_update(request, pk):
    match = get_object_or_404(Match, pk=pk)
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            player1_id = data.get('player1')  # Change the variable name to avoid confusion
            player2_id = data.get('player2')
            player1_score = data.get('player1_score')
            player2_score = data.get('player2_score')
            active = data.get('active')

        
            if not User.objects.filter(id=player1_id).exists():
                return JsonResponse({"status": "error", "message": "Player1 does not exist"}, status=400)
            if not User.objects.filter(id=player2_id).exists():
                return JsonResponse({"status": "error", "message": "Player2 does not exist"}, status=400)
            if not (player1_score >= 0 and player2_score >= 0):
                return JsonResponse({"status": "error", "message": "Score must be positive"}, status=400)
            if active not in [True, False]:
                return JsonResponse({"status": "error", "message": "Active must be a boolean"}, status=400)

            player1 = User.objects.get(id=player1_id)
            player2 = User.objects.get(id=player2_id)

            match.player1 = player1
            match.player2 = player2
            match.player1_score = player1_score
            match.player2_score = player2_score
            match.active = active
            match.save()
            return JsonResponse({'status': 'ok', 'message': 'Match updated successfully'})
        except Match.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Match does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid player ID'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
    return JsonResponse({'status': 'error', 'message': 'Only PUT requests are allowed'}, status=400)

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

def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'DELETE':
        try:
            user.delete()
            return JsonResponse({'status': 'ok', 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only DELETE requests are allowed'}, status=400)

def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "PUT":
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

    return JsonResponse({'status': 'error', 'message': 'Only PUT requests are allowed'}, status=400)