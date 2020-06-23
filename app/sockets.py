from app import socketio
from flask import session, request, flash, redirect, url_for
from flask_socketio import emit, send, join_room, leave_room
from game.game import rooms, Room

# Sends a message in the current room
@socketio.on("message")
def handle_message(data):
    message = data['message']
    room = data['room']
    username = session.get("username")
    send("<strong>"+ username +":</strong> " + message, room=room)

# When a new player joins
@socketio.on("join")
def on_join():
    room_id = session.get("room")
    rooms[room_id].playerCount += 1
    # Either adds or updates the player info in global rooms var
    rooms[room_id].addPlayer(request.sid, session.get("username"))
    # Connects socket to the room
    join_room(room_id)
    if session.get("username") in rooms[room_id].disconnectedPlayers:
        on_rejoin(room_id)
    else:
        # First player is made a host
        if len(rooms[room_id].players) == 1:
            rooms[room_id].host = session.get('username')
            emit("host", {'started': rooms[room_id].started }, room=rooms[room_id].players[rooms[room_id].host])
        # Updates the player list
        emit("updatePlayerList", {'players': rooms[room_id].players, 'host': rooms[room_id].host}, room=room_id)
        emit("host", {'started': rooms[room_id].started},room=rooms[room_id].players[rooms[room_id].host])
        # Sends message
        send(session.get('username') + ' has entered the room.', room=room_id)


def on_rejoin(room_id):
    room = rooms[room_id]
    join_room(room_id)
    emit("updatePlayerList", {'players': rooms[room_id].players, 'host': rooms[room_id].host}, room=room_id)
    emit("host", {'started': rooms[room_id].started},room=rooms[room_id].players[rooms[room_id].host])
    send(session.get('username') + ' has rejoined the room.', room=room_id)
    if room.started:
        emit("gameStarted", room=request.sid)
        if len(room.wordlist) != room.wordsPerPlayer * len(room.players):
            if len(room.wordDict[session.get("username")]) < room.wordsPerPlayer:
                emit("getWords", {'wordsPerPlayer': room.wordsPerPlayer, 'index': len(room.wordDict[ session.get('username')])}, room=request.sid)
            else:
                emit("waitingForPlayers", {'players': [x for x in rooms[room_id].wordDict.keys() if len(rooms[room_id].wordDict[x]) < rooms[room_id].wordsPerPlayer]},room=request.sid)
        else:
            # Create teams
            emit("startPlay", {'round': rooms[room_id].round, 'redTeam': rooms[room_id].redTeam, 'blueTeam': rooms[room_id].blueTeam, 'players': rooms[room_id].players}, room=request.sid)
        
            # Start the turn of the next player
            emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=request.sid)
            if room.currentPlayer ==  session.get('username'):
                emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=request.sid)
        
    

@socketio.on("disconnect")
def on_leave():
    room_id = session.get("room")
    player = request.sid
    # Removes room_id from client side
    # Removes player info from server side
    # Disconnects socket from the room
    
    if session.get("username") in rooms[room_id].kickedPlayers:
        send(session.get('username') + ' has been kicked from the room.', room=room_id)
    else: 
        if rooms[room_id].started:
            rooms[room_id].disconnectedPlayers.append(session.get('username'))
        send(session.get('username') + ' has left the room.', room=room_id)
    
    leave_room(room_id, player)
    # Updates the player list
    del rooms[room_id].players[session.get('username')]
    emit("updatePlayerList", {'players': rooms[room_id].players, 'host': rooms[room_id].host}, room=room_id)
    if rooms[room_id].playerCount == 1:
        del rooms[room_id]
    else:
        rooms[room_id].playerCount -= 1


@socketio.on("removePlayer")
def on_remove(data):
    room_id = session.get("room")
    player = data['player']
    # Checks if the player sending message is a host
    if session.get('username') == rooms[room_id].host:
        # Adds username to kickedPlayers list
        rooms[room_id].kickedPlayers.append(player)
        # Emit to kicked player he has been kicked
        emit("kickedPlayer", room=rooms[room_id].players[player])
        

@socketio.on("startGame")
def start_game():
    room_id = session.get('room')
    rooms[room_id].started = True
    # Emits Game start for client side to initialize game board
    emit("gameStarted", room=room_id)
    # Get words from the individual players
    emit("getWords", {'wordsPerPlayer': rooms[room_id].wordsPerPlayer, 'index': 0}, room=room_id)

@socketio.on("addWord")
def add_word(data):
    word = data['word']
    room_id = session.get("room")
    username = session.get("username")
    rooms[room_id].addWord(word, username)
    if len(rooms[room_id].wordlist) >= len(rooms[room_id].players) * rooms[room_id].wordsPerPlayer: #if wordlist is max - 3 words per player
        rooms[room_id].prepareGame()
        # Create teams
        emit("startPlay", {'round': rooms[room_id].round, 'redTeam': rooms[room_id].redTeam, 'blueTeam': rooms[room_id].blueTeam, 'players': rooms[room_id].players}, room=room_id)
        emit("nextRound", {'round': rooms[room_id].round}, room=room_id)
        # Start the turn of the next player
        emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=room_id)
        emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])
    else:
        emit("waitingForPlayers", {'players': [x for x in rooms[room_id].wordDict.keys() if len(rooms[room_id].wordDict[x]) < rooms[room_id].wordsPerPlayer]},room=request.sid)


@socketio.on("endTurn")
def end_turn(data):
    correctWords = data['correctWords']
    room_id = session.get("room")
    rooms[room_id].endTurn(correctWords)
    if len(rooms[room_id].currentWordList) != 0:
        rooms[room_id].getNextPlayer()
        emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=room_id)
        emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])
    elif len(rooms[room_id].currentWordList) == 0:
        if rooms[room_id].round == 3:
            if rooms[room_id].blueScore > rooms[room_id].redScore:
                winner = 1
            elif rooms[room_id].blueScore < rooms[room_id].redScore: 
                winner = 2
            else: 
                winner = 3
            emit("gameEnded", {'winner': winner}, room=room_id)
            rooms[room_id].endGame()
            # Temporary way to stop the game
            del rooms[room_id]
            return
        else:
            rooms[room_id].startNextRound()
            emit("nextRound", {'round': rooms[room_id].round}, room=room_id)
        if data['timeLeft'] < 5: #Only continues the player's turn if there is significant time left
            rooms[room_id].getNextPlayer()
            emit("yourTurn", {'turnTimer': rooms[room_id].turnTimer, 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])
        else: 
            emit("yourTurn", {'turnTimer': data['timeLeft'], 'currentWordList': rooms[room_id].currentWordList }, room=rooms[room_id].players[rooms[room_id].currentPlayer])
        emit("playerTurn", {'players': rooms[room_id].players, 'currentPlayer': rooms[room_id].currentPlayer, 'redScore': rooms[room_id].redScore, 'blueScore': rooms[room_id].blueScore}, room=room_id)
        
    