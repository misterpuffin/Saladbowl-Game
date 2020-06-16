from app import app, socketio

if __name__ == '__main__':
    socketio.run(app)



# TODO
'''
1. create room function
2. function to rejoin game
3. scoring (kinda done)
4. nicer layout

5. server should not send redundant info to client

'''
