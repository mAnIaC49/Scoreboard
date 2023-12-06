from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse
from django.http import HttpResponseBadRequest, JsonResponse
import json
from django.core.serializers import serialize


from .models import User, Players, Team, Game, Bowls, Playing, TeamsPlaying

# Define the total overs per innings
OVERS = 2

@login_required
def index(request):
    return render(request, 'cricket/index.html', {
        "teams": Team.objects.filter(user=request.user)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "cricket/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "cricket/login.html")

def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "cricket/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "cricket/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "cricket/register.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@login_required
def teams(request):
    if request.method == 'POST':
        type = request.POST.getlist('type')
        first = request.POST.getlist('first')
        last = request.POST.getlist('last')
        players = []

        # Validate the input of the form
        for i in range(15):
            if type[i] not in ['BA', 'BO', 'AR', 'WK']:
                players.clear()
                return HttpResponseBadRequest('Invalid Request')
            else:
                Dict = {}
                Dict["first"] = first[i]
                Dict["last"] = last[i]
                Dict["type"] = type[i]

                players.append(Dict)

        # Insert the team into the database
        team = Team.objects.create(name=request.POST["name"], logo=request.FILES["logo"], user=request.user)

        # Insert the players into the database
        for player in players:                
            Players.objects.create(first=player["first"], last=player["last"], type=player["type"], team=team)

        return HttpResponseRedirect(reverse("teams"))
    else:
        return render(request, "cricket/teams.html", {
            "teams": Team.objects.filter(user=request.user),
            "range": range(1,16)
        })

@login_required    
def game(request):
    if request.method == 'POST':
        # If there is an unfinished game then clear it's data
        games = Game.objects.filter(user=request.user, end_status=False)
        for game in games:
            if game.end_status == False:
                game.delete()

        # Get the form inputs
        team1 = Team.objects.get(name=request.POST["team1"], user=request.user)
        team2 = Team.objects.get(name=request.POST["team2"], user=request.user)

        # Put the game into the database
        game = Game.objects.create(user=request.user)

        # Add the teams to the database
        game.teams.add(team1)
        game.teams.add(team2)

        team1 = TeamsPlaying.objects.create(game=game, team=team1)
        team2 = TeamsPlaying.objects.create(game=game, team=team2)

        return HttpResponseRedirect(reverse("gamecontent"))
    
    else:
        # On receiving a get request by this view, it sends back whether there is an unfinished game
        games = Game.objects.filter(user=request.user, end_status=False)

        for game in games:
            if game.end_status == False:
                return JsonResponse({"data": False}, status=200)
            
        
        return JsonResponse({"data": True}, status=200)


@login_required
@csrf_exempt
def gamecontent(request):
    if request.method == 'POST':
        # On receiving a post request, it first checks whether it's sending the game type or the first team to bat or player info and then updates that information
        data = json.loads(request.body)
        content = data.get("data")

        if content == 'gametype':
            data = data.get("gametype")
            game = Game.objects.get(user=request.user, end_status=False)
            game.game_type=data
            game.save()

        elif content == 'first_bat':
            data = data.get("team")
            game = Game.objects.get(user=request.user, end_status=False)
            bat = Team.objects.get(user=request.user, name=data)
            team = TeamsPlaying.objects.get(game=game, team=bat)
            team.batting_status=True
            team.save()

        elif content == 'players':
            data = data.get("players")
            game = Game.objects.get(user=request.user, end_status=False)

            for id in data:
                player = Players.objects.get(pk=id)
                player = Playing.objects.create(game=game, player=player, first=player.first, last=player.last, team=player.team)
        
        return JsonResponse(status=200, data={})
        
    else:
        # If a get request is made, render game page with the details of the currently running game in the user's account
        game = Game.objects.get(user=request.user, end_status=False)

        teams = game.teams.all()
        players1 = Players.objects.filter(team=teams[0])
        players2 = Players.objects.filter(team=teams[1])
        
        return render(request, 'cricket/game.html', {
            "team1": teams[0],
            "team2": teams[1],
            "players1": players1,
            "players2": players2,
            "game": game
        })


@login_required
@csrf_exempt           
def state(request):
    if request.method == 'POST':
        # The post request requires to contain the details of the bowl and it will the database will be manipulated based on it
        data = json.loads(request.body)
        data = data.get("data")

        game = Game.objects.get(user=request.user, end_status=False)
        bowler = Playing.objects.get(game=game, current_bowling=True)
        strike = Playing.objects.get(game=game, on_strike=True)
        non_strike = Playing.objects.get(game=game, bat_status=True, on_strike=False)
        bowler = Playing.objects.get(game=game, current_bowling=True)
        batting = TeamsPlaying.objects.get(game=game, batting_status=True)
        bowling = TeamsPlaying.objects.get(game=game, batting_status=False)

        # The scores, strike and the number of bowls are manipulated based on the rules of cricket.
        if data == 'wide':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='.', bowl_type='wide', inning=game.inning, over=game.over)
            bowler.runs_given = bowler.runs_given + 1
            batting.score = batting.score + 1
        
            bowl.save()
            bowler.save()
            batting.save()

            return JsonResponse({}, status=200)

        elif data == 'six':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='6', bowl_type='valid', inning=game.inning, over=game.over)
            batting.score = batting.score + 6
            strike.runs = strike.runs + 6
            bowler.bowls = bowler.bowls + 1
            bowler.runs_given = bowler.runs_given + 6

            strike.save()
            bowl.save()
            bowler.save()
            batting.save()

        elif data == 'four':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='4', bowl_type='valid', inning=game.inning, over=game.over)
            batting.score = batting.score + 4
            strike.runs = strike.runs + 4
            bowler.bowls = bowler.bowls + 1
            bowler.runs_given = bowler.runs_given + 4

            strike.save()
            bowl.save()
            bowler.save()
            batting.save()

        elif data == 'one':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='1', bowl_type='valid', inning=game.inning, over=game.over)
            batting.score = batting.score + 1
            strike.runs = strike.runs + 1
            strike.on_strike = False
            non_strike.on_strike = True
            bowler.bowls = bowler.bowls + 1
            bowler.runs_given = bowler.runs_given + 1

            strike.save()
            non_strike.save()
            bowl.save()
            bowler.save()
            batting.save()

        elif data == 'two':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='2', bowl_type='valid', inning=game.inning, over=game.over)
            batting.score = batting.score + 2
            strike.runs = strike.runs + 2
            bowler.bowls = bowler.bowls + 1
            bowler.runs_given = bowler.runs_given + 2

            strike.save()
            bowl.save()
            bowler.save()
            batting.save()

        elif data == 'three':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='3', bowl_type='valid', inning=game.inning, over=game.over)
            batting.score = batting.score + 3
            strike.runs = strike.runs + 3
            strike.on_strike = False
            non_strike.on_strike = True
            bowler.bowls = bowler.bowls + 1
            bowler.runs_given = bowler.runs_given + 3

            strike.save()
            non_strike.save()
            bowl.save()
            bowler.save()
            batting.save()

        elif data == 'dot':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='.', bowl_type='valid', inning=game.inning, over=game.over)
            bowler.bowls = bowler.bowls + 1

            bowler.save()

        elif data == 'nb-six':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='6', bowl_type='noball', inning=game.inning, over=game.over)
            batting.score = batting.score + 7
            strike.runs = strike.runs + 6
            bowler.runs_given = bowler.runs_given + 7

            strike.save()
            bowl.save()
            bowler.save()
            batting.save()
            return JsonResponse({}, status=200)

        elif data == 'nb-four':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='4', bowl_type='noball', inning=game.inning, over=game.over)
            batting.score = batting.score + 5
            strike.runs = strike.runs + 4
            bowler.runs_given = bowler.runs_given + 5

            strike.save()
            bowl.save()
            bowler.save()
            batting.save()

            return JsonResponse({}, status=200)

        elif data == 'nb-one':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='1', bowl_type='noball', inning=game.inning, over=game.over)
            batting.score = batting.score + 2
            strike.runs = strike.runs + 1
            strike.on_strike = False
            non_strike.on_strike = True
            bowler.runs_given = bowler.runs_given + 2

            strike.save()
            non_strike.save()
            bowl.save()
            bowler.save()
            batting.save()

            return JsonResponse({}, status=200)

        elif data == 'nb-two':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='2', bowl_type='noball', inning=game.inning, over=game.over)
            batting.score = batting.score + 3
            strike.runs = strike.runs + 2
            bowler.runs_given = bowler.runs_given + 3

            strike.save()
            bowl.save()
            bowler.save()
            batting.save()

            return JsonResponse({}, status=200)

        elif data == 'nb-three':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='3', bowl_type='noball', inning=game.inning, over=game.over)
            batting.score = batting.score + 4
            strike.runs = strike.runs + 3
            strike.on_strike = False
            non_strike.on_strike = True
            bowler.runs_given = bowler.runs_given + 4

            strike.save()
            non_strike.save()
            bowl.save()
            bowler.save()
            batting.save()

            return JsonResponse({}, status=200)

        elif data == 'nb-dot':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='.', bowl_type='noball', inning=game.inning, over=game.over)
            batting.score = batting.score + 1
            bowler.runs_given = bowler.runs_given + 1

            bowler.save()
            batting.save()
            bowl.save()

            return JsonResponse({}, status=200)

        elif data == 'out':
            bowl = Bowls.objects.create(game=game, batsman=strike, bowler=bowler, bat_type='out', bowl_type='valid', inning=game.inning, over=game.over)
            batting.wickets_down = batting.wickets_down + 1
            strike.out = True
            strike.bat_status = False
            strike.on_strike = False

            bowl.save()
            batting.save()
            strike.save()

        # In case the over is finished after this bowl, the bowler loses the current_bowling status.
        valid = Bowls.objects.filter(game=batting.game, inning=batting.game.inning, over=batting.game.over, bowl_type='valid', bowler__team = bowler.team).count() % 6        
        if valid == 0:
            bowler.current_bowling = False
            game.over = game.over + 1

            game.save()
            bowler.save()
        
        # If the inning is finished, it changes to the second inning or declares the winner.
        wickets_down = batting.wickets_down
        if game.over == OVERS or wickets_down == 10 or (game.inning == 2 and batting.score > bowling.score):
            if game.inning == 1:
                next_bat = TeamsPlaying.objects.get(game=game, batting_status=False)
                batting.batting_status = False
                next_bat.batting_status = True

                strike.bat_status = False
                non_strike.bat_status = False
                strike.on_strike = False
                non_strike.on_strike = False
                bowler.current_bowling = False

                
                game.inning = 2
                game.over = 0

                next_bat.save()
                batting.save()
                strike.save()
                non_strike.save()
                bowler.save()
                game.save()
            else:
                # End the game.
                game.end_status = True
                return JsonResponse({"finish": True}, status=200)
        return JsonResponse({}, status=200)
    else:
        # Send back the current state of the game to update the content onn the scoreboard
        bat = TeamsPlaying.objects.get(batting_status = True)
        bowl = TeamsPlaying.objects.get(batting_status = False)

        batting = bat.team.name    
        bowling = bowl.team.name

        bat_score = bat.score
        bat_wicket = bat.wickets_down
        bowl_score = bowl.score
        over = bat.game.over
        balls = Bowls.objects.filter(game=bat.game, inning=bat.game.inning, over=over, bowl_type='valid').count() % 6

        bowler = Playing.objects.get(game=bat.game, current_bowling=True)
        bowler = bowler.first

        strike = Playing.objects.get(game=bat.game, on_strike=True)
        strike = strike.first

        non_strike = Playing.objects.get(game=bat.game, bat_status=True, on_strike=False)
        non_strike = non_strike.first


        return JsonResponse({"batting": batting, "bowling": bowling, "bat_score": bat_score, "bat_wicket": bat_wicket, "bowl_score": bowl_score,
                            "over": over, "balls":balls, "bowler": bowler, "strike": strike, "non_strike": non_strike},status=200)


@login_required
@csrf_exempt
def next_batsman(request):
    if request.method == 'POST':
        # Update the database with details of the next batsman
        data = json.loads(request.body)
        batsman = data.get("batsman")
        batsman = Playing.objects.get(pk=batsman)
        batsman.bat_status = True
        # Default is to set the player on strike.
        batsman.on_strike = True
        batsman.save()

        # If this batsman is chosen as the second opener, let player be the non striker
        strike = Playing.objects.filter(game=batsman.game, bat_status=True, on_strike=True).count()
        if strike == 2:
            batsman.on_strike = False
            batsman.save()

        return JsonResponse({}, status=200)

    else:
        # Send back a list of players in the batting team that aren't out yet.
        game = Game.objects.get(user=request.user, end_status=False)

        bat_team = TeamsPlaying.objects.get(game=game, batting_status=True)

        bat_players = Playing.objects.filter(game=game, team=bat_team.team, out=False, bat_status=False)

        batters = serialize('json', bat_players)


        return JsonResponse({"batters": batters}, status=200)


@login_required
@csrf_exempt
def next_bowler(request):
    if request.method == 'POST':
        # Update the database with details of the next bowler
        data = json.loads(request.body)
        bowler = data.get("bowler")
        bowler = Playing.objects.get(pk=bowler)
        bowler.current_bowling = True
        bowler.save()

        return JsonResponse({}, status=200)

    else:
        # Send back a list of players in the bowling team
        game = Game.objects.get(user=request.user, end_status=False)

        bowl_team = TeamsPlaying.objects.get(game=game, batting_status=False)

        bowl_players = Playing.objects.filter(game=game, team=bowl_team.team)

        bowlers = serialize('json', bowl_players)

        return JsonResponse({"bowlers": bowlers}, status=200)


@login_required
def empty_spots(request):
    # Send back whether there aare two players and a bowler currently on the pitch
    game = Game.objects.get(user=request.user, end_status=False)

    batting = Playing.objects.filter(game=game, bat_status=True).count()
    if batting == 2:
        batting = False
    else:
        batting = True
    
    bowling = Playing.objects.filter(game=game, current_bowling=True).count()
    if bowling == 1:
        bowling = False
    else:
        bowling = True

    return JsonResponse({"batting": batting, "bowling": bowling}, status=200)

@login_required    
def winner(request):
    # Send back winner of the match based on the team with the highest score.
    game = Game.objects.get(user=request.user, end_status=False)
    teams = TeamsPlaying.objects.filter(game=game)

    if teams[0].score > teams[1].score:
        winner = teams[0]
    else:
        winner = teams[1]

    return render(request, 'cricket/winner.html', {
        "winner": winner,
        "team1": teams[0],
        "team2": teams[1]
    })
            