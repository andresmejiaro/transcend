from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def test_view(request):
	return JsonResponse({'Tournament': 'Not Today!'})

def test_match(request):
	match = {
		'player1': 'Player1',
		'player2': 'Player2',
		'winner': 'Player1',
		'loser': 'Player2',
		'round': 1
	}
	return JsonResponse(match)