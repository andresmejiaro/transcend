from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from api.tournament.models.tournament_model import Tournament
from api.tournament.models.match_model import Match
from api.tournament.models.round_model import Round
import json

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