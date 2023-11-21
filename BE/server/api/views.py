from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def test_view(request):
	return JsonResponse({'message': 'Test passed'})