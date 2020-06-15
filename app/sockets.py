from app import socketio
from flask import session, request, flash, redirect, url_for
from flask_socketio import emit, send, join_room, leave_room
from game.game import rooms, Room

# Sends a message in the current room
@socketio.on("message")
def handle_message(data):
    message = data['message']
    room = data['room']
    username = session['username']
    send("<strong>"+ username +":</strong> " + message, room=room)

# When a new player joins
@socketio.on("join")
def on_join(data):
    room_id = data['room']
    if session['username'] in rooms[room_id].players:
        rooms[room_id].addPlayer(request.sid, session['username'])
        on_rejoin(room_id)
    else:
        rooms[room_id].addPlayer(request.sid, session['username'])
        # First player is made a host
        if len(rooms[room_id].players) == 1:
            rooms[room_id].host = session['username']
        # Connects the socket to the room
        join_room(room_id)
        # Updates the player list
        emit("updatePlayerList", {'players': rooms[room_id].players, 'host': rooms[room_id].host}, room=room_id)
        emit("host", room=rooms[room_id].players[rooms[room_id].host])
        # Sends message
        send(session['username'] + ' has entered the room.', room=room_id)

def on_rejoin(room_id):
    room = rooms[room_id]
    join_room(room_id)
    emit("updatePlayerList", {'players': rooms[room_id].players, 'host': rooms[room_id].host}, room=room_id)
    emit("host", room=rooms[room_id].players[rooms[room_id].host])
    send(session['username'] + ' has rejoined the room.', room=room_id)
    if room.started:
        emit("gameStarted", room=request.sid)
        if len(room.wordDict[session['username']]) != room.wordsPerPlayer:
            print(len(room.wordDict[session['username']]))
            emit("getWords", {'wordsPerPlayer': rooms[room_id].wordsPerPlayer, 'index': len(room.wordDict[session['username']])}, room=request.sid)
        else:
            # Create teams
            emit("startPlay", {'round': rooms[room_id].round, 'redTeam': rooms[room_id].redTeam, 'blueTeam': rooms[room_id].blueTeam, 'players': rooms[room_id].players}, room=request.sid)
        
            # Start the turn of the next player
            emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=request.sid)
            if room.currentPlayer == session['username']:
                emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])

    

@socketio.on("leave")
def on_leave(data):
    room_id = data['room']
    player = request.sid
    # Removes room_id from client side
    del session['room']
    # Removes player info from server side
    del rooms[room_id].players[session['username']]
    # Disconnects socket from the room
    
    if session['username'] in rooms[room_id].kickedPlayers:
        send(session['username'] + ' has been kicked from the room.', room=room_id)
    else: 
        send(session['username'] + ' has left the room.', room=room_id)
    leave_room(room_id, player)
    # Updates the player list
    emit("updatePlayerList", {'players': rooms[room_id].players, 'host': rooms[room_id].host}, room=room_id)
    emit("host", room=rooms[room_id].players[rooms[room_id].host])

@socketio.on("removePlayer")
def on_remove(data):
    room_id = data['room']
    player = data['player']
    # Checks if the player sending message is a host
    if session['username'] == rooms[room_id].host:
        # Adds username to kickedPlayers list
        rooms[room_id].kickedPlayers.append(player)
        # Emit to kicked player he has been kicked
        emit("kickedPlayer", room=rooms[room_id].players[player])
        

@socketio.on("startGame")
def start_game(data):
    room_id = data['room']
    rooms[room_id].started = True
    # Emits Game start for client side to initialize game board
    emit("gameStarted", room=room_id)
    # Get words from the individual players
    emit("getWords", {'wordsPerPlayer': rooms[room_id].wordsPerPlayer, 'index': 0}, room=room_id)

@socketio.on("addWord")
def add_word(data):
    word = data['word']
    room_id = data['room']
    username = session['username']
    rooms[room_id].addWord(word, username)
    if len(rooms[room_id].wordlist) >= len(rooms[room_id].players) * rooms[room_id].wordsPerPlayer: #if wordlist is max - 3 words per player
        rooms[room_id].prepareGame()
        # Create teams
        emit("startPlay", {'round': rooms[room_id].round, 'redTeam': rooms[room_id].redTeam, 'blueTeam': rooms[room_id].blueTeam, 'players': rooms[room_id].players}, room=room_id)
        emit("nextRound", {'round': rooms[room_id].round}, room=room_id)
        # Start the turn of the next player
        emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=room_id)
        emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])

@socketio.on("endTurn")
def end_turn(data):
    print("ENDED")
    correctWords = data['correctWords']
    room_id = data['room']
    rooms[room_id].endTurn(correctWords)
    rooms[room_id].getNextPlayer()
    if len(rooms[room_id].currentWordList) == 0:
        if rooms[room_id].round == 3:
            rooms[room_id].endGame()
            emit("gameEnded", room=room_id)
            return
        else:
            rooms[room_id].startNextRound()
            emit("nextRound", {'round': rooms[room_id].round}, room=room_id)
    emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=room_id)
    emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])
    