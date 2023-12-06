from django.test import Client, TestCase

from .models import Team, Players, User, Bowls, Game

# Create your tests here.
class CricketTestCase(TestCase):

    def setUp(self):
        # Create users
        u = User.objects.create_user('neeraj@neeraj.com', 'neeraj')
        t1 = Team.objects.create(name='team1', user=u)
        t2 = Team.objects.create(name='team2', user=u)
        t3 = Team.objects.create(name='team3', user=u)

        game1 = Game.objects.create()

        game1.teams.add(t1)
        game1.teams.add(t2)
        game1.teams.add(t3)

    def test_index(self):

        # Set up client to make requests
        c = Client()
        u = User.objects.get(pk = 1)
        c.force_login(u)

        # Send get request to index page and store response
        response = c.get('/')

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)

    def test_team(self):
        c = Client()
        u = User.objects.get(pk=1)
        c.force_login(u)

        # Send get request to index page and store response
        response = c.get('/teams')

        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)

        # Make sure a list on numbers from 1 to 15 is returned
        self.assertEqual(response.context["range"], range(1,16))
        
        # Send a post request to teams page
        with open('cricket/static/cricket/logo.svg') as fp:
            response = c.post('/teams', {"name": "warriors", 
                                         "logo": fp,
                                         "first": ["Sachin", "MS", "Virat", "Rohit", "Dinesh", "Ajinkya", "Rahul", "Ravindra", "Ravichandran", "Yuzvendra", "Amit", "Bhuvaneshwar", "Muhammad", "Muhammad", "Umesh"],
                                         "last": ["Tendulkar", "Dhoni", "Kohli", "Sharma", "Karthik", "Rahane", "Dravid", "Jadeja", "Ashwin", "Chahal", "Mishra", "Kumar", "Siraj", "Shami", "Yadav"],
                                         "type": ["BA", "WK", "BA", "BA", "WK", "BA", "BA", "AR", "AR", "BO", "BO", "BO", "BO", "BO", "BO"]
                                    })
            
        # Make sure the status code is 302
        self.assertEqual(response.status_code, 302)
        
        # Make sure that 15 players were registered into the database and the players belong to the team from the input     
        players = Players.objects.all()
        team = players[0].team

        self.assertEqual(team.name, "warriors")
        self.assertEqual(players.count(), 15)

    # Test invalid game
    def test_invalid_team_number(self):
        game = Game.objects.get()

        self.assertFalse(game.is_valid_game())