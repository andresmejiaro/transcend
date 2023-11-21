from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Tournaments, Matches
from django.http import JsonResponse
import json

# @csrf_exempt
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

# @csrf_exempt
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

# @csrf_exempt
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