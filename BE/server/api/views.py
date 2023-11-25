from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
# Create your views here.
def test_view(request):
	return JsonResponse({'message': 'Test passed'})