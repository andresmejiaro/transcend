from django.test import TestCase
from django.contrib.auth.models import User
from .models import Tournament, Match
from datetime import datetime, date

# User Tests
class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="testuser", password="testpassword", email="test@test.com")

    def test_user_created(self):
        user = User.objects.get(username="testuser")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.password, "testpassword")
        print("User created")

    def test_user_updated(self):
        user = User.objects.get(username="testuser")
        user.username = "testuser2"
        user.email = "update@update.com"
        user.password = "updatepassword"
        user.save()

        self.assertEqual(user.username, "testuser2")
        self.assertEqual(user.email, "update@update.com")
        self.assertEqual(user.password, "updatepassword")
        print("User updated")

    def test_user_deleted(self):
        user = User.objects.get(username="testuser")
        user.delete()
        print("User deleted")

# Tournament Tests
class TournamentTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="testuser_tournament", password="testpassword_tournament", email="test@tournament.com")
        Tournament.objects.create(name="testtournament", start_date="2021-01-01", end_date="2021-01-02")
        
    def test_tournament_created(self):
        tournament = Tournament.objects.get(name="testtournament")
        self.assertEqual(tournament.name, "testtournament")
        
        # Convert the string to a datetime.date object
        expected_start_date = datetime.strptime("2021-01-01", "%Y-%m-%d").date()
        self.assertEqual(tournament.start_date, expected_start_date)

        # Similarly, convert the end_date string to a datetime.date object
        expected_end_date = datetime.strptime("2021-01-02", "%Y-%m-%d").date()
        self.assertEqual(tournament.end_date, expected_end_date)
        
        print("Tournament created")

    def test_tournament_updated(self):
        tournament = Tournament.objects.get(name="testtournament")
        tournament.name = "testtournament2"
        tournament.start_date = "2021-01-03"
        tournament.end_date = "2021-01-04"
        tournament.save()

        self.assertEqual(tournament.name, "testtournament2")
        self.assertEqual(tournament.start_date, "2021-01-03")
        self.assertEqual(tournament.end_date, "2021-01-04")
        print("Tournament updated")


    def test_tournament_deleted(self):
        tournament = Tournament.objects.get(name="testtournament")
        tournament.delete()

        with self.assertRaises(Tournament.DoesNotExist):
            Tournament.objects.get(name="testtournament")
        print("Tournament deleted")

# Match Tests
class MatchTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="testuser_match", password="testpassword_match", email="test@test.com")
        Match.objects.create(player1=User.objects.get(username="testuser_match"), player2=User.objects.get(username="testuser_match"), player1_score=0, player2_score=0, active=False)

    def test_match_created(self):
        match = Match.objects.get(player1=User.objects.get(username="testuser_match"))
        self.assertEqual(match.player1, User.objects.get(username="testuser_match"))
        self.assertEqual(match.player2, User.objects.get(username="testuser_match"))
        self.assertEqual(match.player1_score, 0)
        self.assertEqual(match.player2_score, 0)
        self.assertEqual(match.active, False)
        print("Match created")

    def test_match_updated(self):
        match = Match.objects.get(player1=User.objects.get(username="testuser_match"))
        match.player1_score = 1
        match.player2_score = 1
        match.active = True
        match.save()
        print("Match updated")

        self.assertEqual(match.player1_score, 1)
        self.assertEqual(match.player2_score, 1)
        self.assertEqual(match.active, True)

    def test_match_deleted(self):
        match = Match.objects.get(player1=User.objects.get(username="testuser_match"))
        match.delete()

        with self.assertRaises(Match.DoesNotExist):
            Match.objects.get(player1=User.objects.get(username="testuser_match"))
        print("Match deleted")

