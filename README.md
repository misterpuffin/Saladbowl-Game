# Saladbowl-Game
A flask-socketio implementation of the game "Salad Bowl"

Website: http://saladbowl-game.herokuapp.com

How to play: https://kidstir.com/salad-bowl-game/

Stages:
  - Upon Game Start, all users will be prompted to input N words. (N is specified in game options by host)
  - Teams and words are shuffled.
  - Each player takes turns with the specified amount of time to describe/act the word out for teammates to guess. (Teams are identified by the color of player on the board)
  - Players have the option to skip words
  - Play continues after the words in the "salad bowl" run out, whereby a new round starts
  - At the end of the game score is tracked and winning team is shown
  
 Future Extensions:
  - Front-end framework/library for nicer looks
  - Modularity of the code can be improved
  - In-game option to draw (instead of charades) - this allows the game to be played using only the website
  - Game options to rejoin the same room after a game. (EASY)
  - Allow for "free-for-all" game option (keep track of individual player's score)
  - Bug fixing for when players leave the game, rejoin if disconnected.
  
  
 Screenshots:
 
