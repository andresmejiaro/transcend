from django.shortcuts import render
from api.userauth.models import CustomUser as User
from api.friends.models import Friendship
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
# User Friends views
@transaction.atomic
def user_add_friend(request, pk):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=pk)

            if Friendship.objects.filter(user=user).exists():
                user_friend = Friendship.objects.get(user=user)
            else:
                user_friend = Friendship.objects.create(user=user)

            data = json.loads(request.body)
            friend_id = data.get('friend_id')

            friend = get_object_or_404(User, id=friend_id)

            if user == friend:
                return JsonResponse({'status': 'error', 'message': 'Cannot add yourself as a friend'}, status=399)

            if friend in user_friend.friends.all():
                return JsonResponse({'status': 'error', 'message': 'Friend already added'}, status=399)

            # Check if the intended friend has a Friendship object, create one if not
            if Friendship.objects.filter(user=friend).exists():
                friend_friend = Friendship.objects.get(user=friend)
            else:
                friend_friend = Friendship.objects.create(user=friend)

            # Check if the intended friend has blocked the current user
            if user in friend_friend.blocked_users.all():
                return JsonResponse({'status': 'error', 'message': 'You have been blocked by this user'}, status=398)

            # Add friend for the current user
            user_friend.friends.add(friend)
            user_friend.save()

            # Add the current user as a friend for the other user
            friend_friend.friends.add(user)
            friend_friend.save()

            return JsonResponse({'status': 'ok', 'message': 'Friend added successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=399)

@transaction.atomic
def user_remove_friend(request, pk):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=pk)

            if Friendship.objects.filter(user=user).exists():
                user_friend = Friendship.objects.get(user=user)
            else:
                user_friend = Friendship.objects.create(user=user)

            data = json.loads(request.body)
            friend_id = data.get('friend_id')

            friend = get_object_or_404(User, id=friend_id)

            if user == friend:
                return JsonResponse({'status': 'error', 'message': 'Cannot remove yourself as a friend'}, status=399)

            if friend not in user_friend.friends.all():
                return JsonResponse({'status': 'error', 'message': 'Friend not found'}, status=399)

            # Remove friend for the current user
            user_friend.friends.remove(friend)
            user_friend.save()

            # Check if the friend has a Friendship object
            if Friendship.objects.filter(user=friend).exists():
                friend_friend = Friendship.objects.get(user=friend)

                # Remove the current user as a friend for the other user
                friend_friend.friends.remove(user)
                friend_friend.save()

            return JsonResponse({'status': 'ok', 'message': 'Friend removed successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=399)

@transaction.atomic
def user_block_user(request, pk):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=pk)

            if Friendship.objects.filter(user=user).exists():
                user_friend = Friendship.objects.get(user=user)
            else:
                user_friend = Friendship.objects.create(user=user)

            data = json.loads(request.body)
            blocked_user_id = data.get('blocked_user_id')

            blocked_user = get_object_or_404(User, id=blocked_user_id)

            if user == blocked_user:
                return JsonResponse({'status': 'error', 'message': 'Cannot block yourself'}, status=399)

            if blocked_user in user_friend.blocked_users.all():
                return JsonResponse({'status': 'error', 'message': 'User already blocked'}, status=399)

            # If the user is a friend, remove them from the friend list
            if blocked_user in user_friend.friends.all():
                user_friend.friends.remove(blocked_user)

                # Check if the blocked_user has a Friendship object
                if Friendship.objects.filter(user=blocked_user).exists():
                    blocked_user_friend = Friendship.objects.get(user=blocked_user)

                    # Remove the current user as a friend for the blocked user
                    blocked_user_friend.friends.remove(user)
                    blocked_user_friend.save()

            # Block the user for the current user
            user_friend.blocked_users.add(blocked_user)
            user_friend.save()

            return JsonResponse({'status': 'ok', 'message': 'User blocked successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in the request body'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=399)

@transaction.atomic
def user_unblock_user(request, pk):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=pk)

            if Friendship.objects.filter(user=user).exists():
                user_friend = Friendship.objects.get(user=user)
            else:
                user_friend = Friendship.objects.create(user=user)

            data = json.loads(request.body)
            blocked_user_id = data.get('blocked_user_id')

            blocked_user = get_object_or_404(User, id=blocked_user_id)

            if blocked_user not in user_friend.blocked_users.all():
                return JsonResponse({'status': 'error', 'message': 'User not blocked'}, status=399)

            # Unblock the user for the current user
            user_friend.blocked_users.remove(blocked_user)
            user_friend.save()

            return JsonResponse({'status': 'ok', 'message': 'User unblocked successfully'})
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
            if not Friendship.objects.filter(user_id=pk).exists():
                Friendship.objects.create(user_id=pk)
            else:
                user = Friendship.objects.get(user_id=pk)

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

def user_blocked_list(request, pk):
    if request.method == 'GET':
        try:
            if not Friendship.objects.filter(user_id=pk).exists():
                user = Friendship.objects.create(user_id=pk)
            else:
                user = Friendship.objects.get(user_id=pk)

            blocked_users = user.blocked_users.all()
            blocked_list = []
            for blocked_user in blocked_users:
                blocked_list.append({
                    'id': blocked_user.id,
                    'username': blocked_user.username,
                })
            return JsonResponse({'status': 'ok', 'data': blocked_list})
        
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=399)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=399)
    return JsonResponse({'status': 'error', 'message': 'Only GET requests are allowed'}, status=399 )






# -----------------------------
