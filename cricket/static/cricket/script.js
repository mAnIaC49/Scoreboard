document.addEventListener("DOMContentLoaded", function() {

    // If on the My teams page
    if (document.getElementById('new-team') !== null)
    {
        // On clicking the new team button, open the div with the form for inouts regarding the new team.
        document.getElementById('new-team').onclick = function() {
            document.getElementById('teams-container').style.display = 'none';
            document.getElementById('new-team-container').style.display = 'block';
        }   
    }


    // If on the index page
    if (document.getElementById('new') !== null)
    {
        // If the new game button is clicked
        document.getElementById('btn-new-game').onclick = function() {
            document.getElementById('new').style.display = 'block';
        }

        document.getElementById('btn-load-game').onclick = function() {
            // Set a flag in local storage so that we can let the game page know that it is loaded and not a new game
            localStorage.setItem("loaded", "true");

            // Click the hidden anchor tag to load the game page
            document.getElementById('secret').click();

        }

        document.querySelector('form').addEventListener('submit', function (event) {

            // Prevent default form submission
            event.preventDefault();

            // Remove the indicator of a previously loaded game
            localStorage.setItem("loaded", "false");

            // Make a GET request
            fetch('/game')
            .then(response => response.json())
            .then(result => {
                let data = result["data"];

                // If there is a game that hasn't ended
                if (!data)
                {
                    // Send a confirmation message
                    let accepted = confirm("There exists an unfinished game. Starting a new game will erase it's data. Are you sure you want to continue ?");

                    // If confirmation accepted
                    if (accepted) {
                        document.querySelector('form').submit();
                    }
                }
                else {

                    document.querySelector('form').submit();
                }
            })
        })
    } 


    // If on the games page
    if (document.getElementById('btn-team1') !== null)
    {
        // Check whether the game is loaded
        let bool = localStorage.getItem("loaded");

        // If the game is loaded, just continue with the gameplay function, else open the block containing the option to choose the type of the game
        if (bool === "true") {
            gameplay();
        }
        else {
            document.getElementById('type-container').style.display = 'block';
        }

        // The user selects t20 or odi and that information is sent to the backend
        document.getElementById('btn-t20').onclick = function() {
            fetch('/gamecontent', {
                method: 'POST',
                body: JSON.stringify({
                    data: "gametype",
                    gametype: 't20'
                })
            })
            .catch(error => {
                console.log('Error:', error)
            });

            document.getElementById('type-container').style.display = 'none';
            document.getElementById('first-container').style.display = 'block';
        }

        document.getElementById('btn-odi').onclick = function() {
            fetch('/gamecontent', {
                method: 'POST',
                body: JSON.stringify({
                    data: "gametype",
                    gametype: 'odi'
                })
            })
            .catch(error => {
                console.log('Error:', error)
            });

            document.getElementById('type-container').style.display = 'none';
            document.getElementById('first-container').style.display = 'block';
        }

        // The user selects the team to bat first and that information  is sent to the database
        document.getElementById('btn-team1').onclick = function() {
            let name = this.innerHTML;

            fetch('/gamecontent', {
                method: 'POST',
                body: JSON.stringify({
                    data: "first_bat",
                    team: name
                })
            })
            .catch(error => {
                console.log('Error:', error)
            });

            document.getElementById('first-container').style.display = 'none';
            document.getElementById('players1').style.display = 'block';
        }

        document.getElementById('btn-team2').onclick = function() {
            let name = this.innerHTML;

            fetch('/gamecontent', {
                method: 'POST',
                body: JSON.stringify({
                    data: "first_bat",
                    team: name
                })
            })
            .catch(error => {
                console.log('Error:', error)
            });

            document.getElementById('first-container').style.display = 'none';
            document.getElementById('players1').style.display = 'block';
        }

        // Let us make sure that the user is only able to select 11 players
        let maxSelections = 11;

        // For players of the first team
        let form1 = document.getElementById('players1').querySelector('form');

        form1.addEventListener('change', function(event) {
            if (event.target.type === 'checkbox' && event.target.name === 'group') {
                let selectedCheckboxes = form1.querySelectorAll('input[name="group"]:checked').length;

                if (selectedCheckboxes > maxSelections)
                {
                    // Uncheck the last clicked radio button if the limit is exceeded
                    event.target.checked = false;
                }
            }

        });


        // For players of the second team
        let form2 = document.getElementById('players2').querySelector('form');

            form2.addEventListener('change', function(event) {
                if (event.target.type === 'checkbox' && event.target.name === 'group') {
                    let selectedCheckboxes = form2.querySelectorAll('input[name="group"]:checked').length;

                    if (selectedCheckboxes > maxSelections)
                    {
                        // Uncheck the last clicked radio button if the limit is exceeded
                        event.target.checked = false;
                    }
                }

            });


        // On submitting the form of the players of the first team.
        form1.onsubmit = function(event) {
            // Prevent the submission of the form.
            event.preventDefault();

            // Let players be the array of ids of the selected players.
            let players = [];

            // Let us store all the checkboxes in the variable checkedCheckboxes.
            let checkedCheckboxes = form1.querySelectorAll('input[type="checkbox"]:checked');

            // Get the id of all the players selected and push it to the players array.
            checkedCheckboxes.forEach(function(checkbox) {
                players.push(checkbox.dataset.id);
            });

            // Submit the lis of selected player ids to the gamecontent view
            fetch('/gamecontent', {
                method: 'POST',
                body: JSON.stringify({
                    data: 'players',
                    players: players
                })
            })
            .then(response => response.json())

            // Close the block and open the block containing selections for the players of the other team.
            form1.parentElement.style.display = 'none';
            document.getElementById('players2').style.display = 'block';

        }

        // On submitting the form of the players of the second team, repeat the same steps.
        form2.onsubmit = function(event) {
            event.preventDefault();
            let checkedCheckboxes = form2.querySelectorAll('input[type="checkbox"]:checked');
            let players = [];

            checkedCheckboxes.forEach(function(checkbox) {
                players.push(checkbox.dataset.id);
            });

            fetch('/gamecontent', {
                method: 'POST',
                body: JSON.stringify({
                    data: 'players',
                    players: players
                })
            })
            .then(response => response.json())

            form2.parentElement.style.display = 'none';
            gameplay();
        }
    }
})

// Set of events to take place in the game
function gameplay() {
    document.getElementById('type-container').style.display = 'none';
    document.getElementById('gameplay').style.display = 'block';

    // Check for the selection of batsmen and bowlers.
    playerChange();


    // The function to be run on each ball.
    document.querySelectorAll('.result').forEach(function(button) {
        button.onclick = () => {
            fetch('/state', {
                method: 'POST',
                body: JSON.stringify({
                    data: button.innerHTML
                })
            })
            .then(response => response.json())
            .then(data => {

                // If the game has ended display the results.
                if (data["finish"])
                {
                    document.getElementById("finish").click();
                }
                playerChange()
            });
        }
    });
}

// Checks for the presence of two batsmen and a bowler in the pitch and incase of absence run selectBatsman and selectBowler function.
function playerChange() {
    // check whether there are two batsmen and a bowler on the pitch.
    fetch("/empty_spots")
    .then(response => response.json())
    .then(result => {
        let batting = result["batting"];
        let bowling = result["bowling"];

        // If there isnt two batsmen currently batting, run the selectBatsman function.
        if(batting) {
        selectBatsman();
        }

        // If there isnt a bowler currently bowling, run the selectBowler function.
        if(bowling) {
        selectBowler();
        }

        // If there are two batsmen and a bowler on the pitch now, just update the scoreboard.
        if(!(batting || bowling))
        {
            updateScore();
        }

    })
    
}

function updateScore() {
    document.getElementById('present').style.display = 'block';

    // Check for the current condition including the scores, batsmen onn crease and bowler bowling and update the scoreboard.
    fetch('/state')
    .then(response => response.json())
    .then(result => {
        let batting = result["batting"];
        let bowling = result["bowling"];
        let bat_score = result["bat_score"];
        let bat_wicket = result["bat_wicket"];
        let bowl_score = result["bowl_score"];
        let over = result["over"];
        let balls = result["balls"];
        let bowler = result["bowler"];
        let strike = result["strike"];
        let non_strike = result["non_strike"];

        document.getElementById("bat").innerHTML = batting;
        document.getElementById("score").innerHTML = bat_score;
        document.getElementById("wicket").innerHTML = bowl_score;
        document.getElementById("over").innerHTML = over;
        document.getElementById("balls").innerHTML = balls;
        document.getElementById("bowler_name").innerHTML = bowler;
        document.getElementById("strike").innerHTML = strike;
        document.getElementById("non_strike").innerHTML = non_strike;
        document.getElementById("number").innerHTML = balls+1;
        document.getElementById("wicket").innerHTML = bat_wicket;
    })
}

function selectBatsman() {
    let block = document.getElementById("select-batsman");

    // Fetch the list of batsmen that aren't out yet
    fetch('/next_batsman')
    .then(response => response.json())
    .then(result => {
            // Let players be the variable containing all the players from the batting team.
            let players = JSON.parse(result.batters);

            // Clear the already existing options from the select element.
            document.getElementById('batsman').innerHTML = '';

            // Create a default option which is selected and disabled.
            let selected = document.createElement('option');
            selected.selected = true;
            selected.disabled = true;
            selected.innerHTML = 'Select Batsman';
            document.getElementById("batsman").appendChild(selected);

            // Create options for each players and append it to the select element.
            players.forEach(item => {            
                let option = document.createElement('option');
                option.value = item.pk;
                option.innerHTML = item.fields["first"] + " " + item.fields["last"];

                document.getElementById("batsman").appendChild(option);
            });

    });

    block.style.display = 'block';

    // On submitting the selected batsman, let the information be sent to the backend.
    block.querySelector('form').onsubmit = function(event) {
        event.preventDefault();

        let value = this.querySelector('select').value;

        block.style.display = 'none';

        fetch("next_batsman", {
            method: 'POST',
            body: JSON.stringify({
                batsman: value
            })
        })
        .then(response => response.json())
        .then(result => {
            // Two openers might be be selected so check whether there is another batsman needed to be selected and run the function again.
            fetch("/empty_spots")
            .then(response => response.json())
            .then(result => {
                let batting = result["batting"];
                
                if (batting) {
                    selectBatsman();
                }
                else {
                    playerChange()
                }

            })
        })
    }

}

function selectBowler() {
    let block = document.getElementById("select-bowler");

    fetch('/next_bowler')
    .then(response => response.json())
    .then(result => {
        // Let players be the variable containing all the players from the bowling team.
        let players = JSON.parse(result.bowlers);

        document.getElementById("bowler").innerHTML = '';

        let selected = document.createElement('option');
        selected.selected = true;
        selected.disabled = true;
        selected.innerHTML = 'Select Bowler'
        document.getElementById("bowler").appendChild(selected);

        players.forEach(item => {            
            let option = document.createElement('option');
            option.value = item.pk;
            option.innerHTML = item.fields["first"] + " " + item.fields["last"];

            document.getElementById("bowler").appendChild(option);
        });
         
    });

    block.style.display = 'block';

    // On submitting the selected bowler, let the information be sent to the backend.
    block.querySelector('form').onsubmit = function(event) {
        event.preventDefault();
        let value = this.querySelector('select').value;

        block.style.display = 'none';

        fetch("next_bowler", {
            method: 'POST',
            body: JSON.stringify({
                bowler: value
            })
        })
        .then(response => response.json())
        .then(result => {
            playerChange()
        })
    }
}