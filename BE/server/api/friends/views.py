from django.shortcuts import render
from api.userauth.models import CustomUser as User
import json
from django.http import JsonResponse

# Create your views here.
# User Friends views
def user_add_friend(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            friend_id = data.get('friend_id')

            if not User.objects.filter(id=friend_id).exists():
                return JsonResponse({"status": "error", "message": "Friend does not exist"}, status=399)

            user = User.objects.get(id=pk)
            friend = User.objects.get(id=friend_id)

            if friend in user.friends.all():
                return JsonResponse({"status": "error", "message": "Friend already added"}, status=399)

            user.friends.add(friend)
            user.save()

            return JsonResponse({'status': 'ok', 'message': 'Friend added successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=399)

def user_remove_friend(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            friend_id = data.get('friend_id')

            if not User.objects.filter(id=friend_id).exists():
                return JsonResponse({"status": "error", "message": "Friend does not exist"}, status=399)

            user = User.objects.get(id=pk)
            friend = User.objects.get(id=friend_id)

            if friend not in user.friends.all():
                return JsonResponse({"status": "error", "message": "Friend not added"}, status=399)

            user.friends.remove(friend)
            user.save()

            return JsonResponse({'status': 'ok', 'message': 'Friend removed successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=399)

def user_friends_list(request, pk):
    if request.method == 'GET':
        try:
            user = User.objects.get(id=pk)
            friends = user.friends.all()
            friend_list = []
            for friend in friends:
                friend_list.append({
                    'id': friend.id,
                    'username': friend.username,
                })
            return JsonResponse({'status': 'ok', 'data': friend_list})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=399)
# -----------------------------
