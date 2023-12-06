## Overview
Cs-Cricket is a Django application that serves as a comprehensive scoreboard for cricket matches, seamlessly storing detailed information about each ball bowled in a dedicated database.

## Distinctiveness and Complexity
CS Cricket stands apart from traditional web projects in the CS50 Web course by introducing a dynamic and data-centric approach. Unlike other applications where navigation takes precedence, CS Cricket focuses on real-time game dynamics, with every user interaction directly influencing the underlying database. This project has used in it all the areas of web applications that each of the other projects have focused on with more if not the same level of complexity in them.

The primary complexity in the application involves writing code to navigate various scenarios, such as concluding an inning due to either the fall of all wickets or the completion of overs.
This  app's database is meticulously structured to not only power the current scoreboard functionality but also lay a robust foundation for future statistical features.
In developing CS Cricket, the JavaScript code intricately manages the complexity of dynamic game scenarios, handling everything from player positions to scores and wicket counts by constantly interacting with the backend. The modular structure and use of functions within functions ensure a resilient and adaptable codebase.

## Contents of each File

### Templates
The template folder contains seven html files.
- The layout for all the other html files is written in the layout.html file that contains the navigation bar and the logo.
- The login.html and register.html files make the login and register pages in the application.
- The teams.html file makes the web page that shows all the teams made by the logged in user and also has the feature to create new teams. To make a new team, the file contains a form to be filled that requires to fill details of the team such as the name, choose an image for the logo (will be stored as a media file), and details of the 15 players in the team including their first and last name and the type of player they are.
- The index.html file consists of option to either load game if the user's previous game didn't conclude or to start a new game. For the new game, the user has to choose two teams from the teams that were created by the user.
- The game.html file consists of various blocks, each of which will have some role to play in the game that either is new or is a loaded game. The first block contains the images of the logos of the two teams that the game is between. The next four blocks will only show up in a new game where it requires the user to select details of the game such as the overs, the team to bat first and the 11 players out of 15 in each team that will be playing that specific game. The last block is the main game content that has a scoreboard, details of the players on the pitch and buttons for each possible outcome of a ball bowled.

### Static files
#### script.js
The script.js file is the javascript file used in all the pages. 
- The main function is run afer the document is loaded. This function is divided into three parts where each part is designed to be executed in one of the pages from game.html, index.html and teams.html.
- The code has also made use of localstorage to help with implementing the load game feature.
- The javascript code for teams.html and index.html is simple. The code for game.html however is big and complicated and makes for most of the javascript code in the application.

The script.js file also contains 5 other functions that will be used in the game.html page.
- The gameplay function is set to run after the successful loading of the previous unfinished game, or on starting a new game after the selection of the game structure. The other functions run inside this function since this is the part I refered to as 'dynamic' where each click of a button will lead to many changes in the database.
- In the other 4 functions, the selectBatsman function takes care of displaying a form for selecting the next batsman by first fetching the details of players in the batting team who aren't out yet. It is also involved in sending the detail of the selected batsman on submitting the form. The selectBowler does the same but for selecting the next bowler on completion of each player.
- The playerChange function first checks for the absence of two batsmen or a bowler on pitch and then decides whether to run the selectBatsman or selectBowler functions.
- The updateScore function collects data on the current condtion of the game including scores, wickets fallen, striker, etc.

### Models.py
- The Team model consists of the details of the teams created by the user.
- The Players model consists of details and the game records of the player that can be used for statistical purposes in the future.
- The Game model consists of details of the games played in the user's profile.
- The Bowls model stores the data of each ball bowled and has a foreign key referring to a game.
- The Playing model is also related to a game through a foreign key and contains the details of players who played the game including their scores or balls bowled.
- The TeamsPlaying model is also related to a game and contains the details of the condition of a team at a point or at the end of the game.
- On deletion of a field in the game model, the corresponding Bowls, Playing and Teamsplaying fields related to it also get deleted.

### Views.py
- The index view simply renders the index page by providing it the data of every team by the user.
- The login_view, logout_view and register take care of the authentication of the user.
- The teams view renders the teams.html page and also saves the details of the new team created by the user into the database.
- The game view send back the information on whether there is an unfinished game and on receiving a post request creates a new game field in the database.
- The gamecontent view renders the game.html page and on receiving a post request saves the details of the game type.
- The state view gives back a json response containing the current situation of the game and on post request changes the database based on the kind of request it is.
- The next_batsman and next_bowler view, update database to change the current_bowler, strike and non_strike rows and also sends back details of players from batting team that weren't out and players from the bowling team.
- The empty_spots view sends back details on whether there are 2 batsmen or a bowler on the pitch.
- The winner view renders the winner.html page after the end of a game.


### How to Run
1. Go to the directory which contains "manage.py" file
2. Then type this command: python manage.py runserver
3. In your Web browser use a URL: http://127.0.0.1:8000/

### Additional information
This applcation can successfully run an entire game but cannot play an entire tournament currently even though all the foundations that would be required to do it are present in the application. Even though there are options, I have reduced the number of overs to just 2 to make it easier to show functioning of the app.
