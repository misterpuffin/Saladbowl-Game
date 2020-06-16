from app import app
from flask import render_template, request, redirect, url_for, session, flash
from game.game import rooms, Room
from urllib.parse import quote, unquote



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        room_id = request.form.get('room')
        room_id = quote(room_id, safe='')

        # Checks if the room is already created
        if room_id not in rooms:
            flash("The room you are trying to join does not exist!")
            return redirect(url_for("index"))

        # Checks if player already exists in the room
        elif username in rooms[room_id].players or username in rooms[room_id].kickedPlayers:
            flash("The username is already taken")
            return redirect(url_for("index"))

        # Checks if the game has already started
        elif rooms[room_id].started:
            flash("The room you are trying to join had already started their game")    
            return redirect(url_for("index"))

        # Checks if the user is kicked from the room
        elif session.get("username") is not None:
            if session.get("username") in rooms[room_id].kickedPlayers:
                flash("You have been kicked from this room")

                return redirect(url_for("index"))
            else:
                session['username'] = username
                session['room'] = room_id
                rooms[room_id].playersList.append(session['username'])

        # Successful connection to the room
        else:
            session['username'] = username
            session['room'] = room_id
            print(session)
            rooms[room_id].playersList.append(session['username'])
        return redirect(url_for("room", room_id = unquote(room_id)))

    # GET route
    return render_template("index.html")

@app.route("/<room_id>")
def room(room_id):
    # Checks if user has already joined from the index page
    room_id = quote(room_id)
    if session.get('room') is None or room_id not in rooms:
        return redirect(url_for("index"))

    # Checks if user is in the wrong room
    if session.get("room") != room_id:
        if session.get("room") in rooms and session.get("username") in rooms[room_id].playersList:
            return redirect(url_for("room", room_id = unquote(session['room'])))

    # Checks if user has been kicked
    if session.get("username") in rooms[room_id].kickedPlayers:
        flash("You have been kicked from this room")
        return redirect(url_for("index"))

    # Checks if username is in the room
    if session.get("username") not in rooms[room_id].playersList:
        return redirect(url_for("index"))

    # Successfully joined
    return render_template("room.html", room = rooms[room_id])

@app.route("/create", methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Creates the user and room profile
        room_id = request.form.get('room')
        room_id = quote(room_id, safe='')
        wordsPerPlayer = int(request.form.get('wordsPerPlayer'))
        turnTimer = int(request.form.get("turnTimer"))

        # Only if room does not already exist
        if room_id not in rooms:
            session['username'] = request.form.get("username")
            session['room'] = room_id
            rooms[room_id] = Room(room_id, wordsPerPlayer, turnTimer)
            rooms[room_id].playersList.append(session.get("username"))

        # Room already exists
        else: 
            flash("The room ID is already taken!")
            return redirect(url_for("index"))
        return redirect(url_for("room", room_id = unquote(room_id)))
    return redirect(url_for("index"))
        