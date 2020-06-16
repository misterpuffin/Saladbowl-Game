import json
import random


class Room():
    def __init__(self, room_id, wordsPerPlayer, turnTimer):
        self.room_id = room_id
        self.players = {}
        self.playerCount = 0
        self.playersList = []
        self.host = None
        self.wordlist = []
        self.wordDict = {}
        self.kickedPlayers = []
        self.disconnectedPlayers = []

        #Game configs
        self.turnTimer = turnTimer
        self.wordsPerPlayer = wordsPerPlayer

        #teams
        self.redTeam = []
        self.blueTeam = []
        self.playerOrder = [] 
        self.redScore = 0
        self.blueScore = 0

        #game status 
        self.started = False
        self.round = 0

        #turn info
        self.currentPlayer = None
        self.currentWordList = None

        
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    # function to add players
    def addPlayer(self, player_id, username):
        self.players[username] = player_id
        if username not in self.wordDict:
            self.wordDict[username] = []
    
    #function to add words into the game
    def addWord(self, word, username):
        self.wordlist.append(word)
        self.wordDict[username].append(word)

    def prepareGame(self):
        #Create Teams
        playerList = random.sample(self.players.keys(), len(self.players))
        self.blueTeam = playerList[0: len(playerList) // 2]
        self.redTeam = playerList[len(playerList) // 2:]

        #Some code to alternate between the 2 teams
        self.playerOrder = self.redTeam + self.blueTeam
        self.playerOrder[::2] = self.redTeam
        self.playerOrder[1::2] = self.blueTeam 

        self.startNextRound()
        self.getNextPlayer()


    def startNextRound(self):
        self.round += 1
        #Shuffle wordlist
        self.currentWordList = random.sample(self.wordlist, len(self.wordlist))

    def getNextPlayer(self):
        if self.currentPlayer == None:
            self.currentPlayer = self.playerOrder[0]
        else:
            index = self.playerOrder.index(self.currentPlayer)
            index += 1
            if index >= len(self.playerOrder):
                self.currentPlayer = self.playerOrder[0]
            else:
                self.currentPlayer = self.playerOrder[index]
        
    def endTurn(self, correct):
        if self.currentPlayer in self.redTeam:
            self.redScore += len(correct)
        elif self.currentPlayer in self.blueTeam:
            self.blueScore += len(correct)
        for index in sorted(correct, reverse=True):
            del self.currentWordList[index]
        random.shuffle(self.currentWordList)

    def endGame(self):
        self.wordlist = []

        #teams
        self.redTeam = []
        self.blueTeam = []
        self.playerOrder = [] 
        self.redScore = 0
        self.blueScore = 0

        #game status 
        self.started = False
        self.round = 0

        #turn info
        self.currentPlayer = None
        self.currentWordList = None




rooms = {}
