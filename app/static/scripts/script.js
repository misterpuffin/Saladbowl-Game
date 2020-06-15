var socket = io();

//function to get room_id from the url
function getRoom(url) {
  return url.split("/").pop();
}

const room_id = getRoom(window.location.href);

socket.on("connect", function () {
  console.log("New connection");
});

//joins the room
if (room_id.length != 0) {
  socket.emit("join", { room: room_id });
}

//***** MESSAGES SENT *****

//sends message
$("#send").click(function () {
  socket.emit("message", { message: $("#message").val(), room: room_id });
  $("#message").val("");
});

$("#message").keyup(function () {
  if (event.keyCode === 13) {
    $("#send").click();
  }
});

//starts game
$("#startGame").click(function () {
  socket.emit("startGame", { room: room_id });
  $(this).remove();
});

//*****MESSAGES RECEIVED******

//adds message to list
socket.on("message", function (data) {
  $("#messageList").append("<li>" + data + "</li>");
});

//updates the player list when a player joins
socket.on("updatePlayerList", function (data) {
  $("#playerList").empty();
  let player_count = 0;
  for (var player in data.players) {
    if (player === data.host) {
      $("#playerList").append("<li>" + player + "<strong>(host)</strong></li>");
    } else {
      $("#playerList").append(
        "<li>" +
          player +
          "<button class='btn btn-sm btn-danger hostFunction removePlayer hidden ml-1' value='" +
          player +
          "'>x</button></li>"
      );
    }
    player_count++;
  }
  if (player_count < 4) {
    $("#startGame").addClass("disabled");
    $("#startGame").prop("disabled", true);
  } else if (player_count >= 4) {
    $("#startGame").removeClass("disabled");
    $("#startGame").prop("disabled", false);
  }
});

// when player is kicked
socket.on("kickedPlayer", function () {
  socket.emit("leave", { room: room_id });
  location.reload();
});

socket.on("gameStarted", function () {
  $("#startGame").addClass("hidden");
});

socket.on("host", function () {
  $(".hostFunction").removeClass("hidden");
  console.log("removed");
  $(".removePlayer").click(function () {
    socket.emit("removePlayer", { player: $(this).val(), room: room_id });
  });
});

socket.on("getWords", function (data) {
  let wordsPerPlayer = data.wordsPerPlayer;
  let index = data.index;
  $("#getWords").toggleClass("hidden");
  let i = 1 + index;
  $("#getWords>h4").text("Word " + i);
  $("#addWord").click(function () {
    socket.emit("addWord", {
      word: $("#getWords input").val(),
      room: room_id,
    });
    i++;
    if (i <= wordsPerPlayer) {
      $("#getWords>h4").text("Word " + i);
      $("#getWords input").val("");
    } else {
      $("#getWords").toggleClass("hidden");
    }
  });
  $("#getWords input").keyup(function () {
    if (event.keyCode === 13) {
      $("#addWord").click();
    }
  });
});

socket.on("startPlay", function (data) {
  console.log("game started");
  $("#gameBoard").removeClass("hidden");
  $(".current-round").text("Round " + data.round);
  let player_count = data.redTeam.length + data.blueTeam.length;
  let angle = (2 * Math.PI) / player_count;
  for (let i = 0; i < player_count; i++) {
    if (i % 2 == 0) {
      let player = data.redTeam[Math.floor(i / 2)];
      let topValue = 50 - Math.cos(i * angle) * 30;
      let leftValue = 50 - Math.sin(i * angle) * 30;
      $(".redTeam").append(
        "<span style='top: " +
          topValue +
          "%; left: " +
          leftValue +
          "%;' class='redPlayer'><img class='player-img' src='/static/images/red_player.png'><br>" +
          player +
          "</span>"
      );
    } else {
      let player = data.blueTeam[Math.floor(i / 2)];
      let topValue = 50 - Math.cos(i * angle) * 30;
      let leftValue = 50 - Math.sin(i * angle) * 30;
      $(".blueTeam").append(
        "<span style='top: " +
          topValue +
          "%; left: " +
          leftValue +
          "%;' class='bluePlayer'><img class='player-img' src='/static/images/blue_player.png'><br>" +
          player +
          "</span>"
      );
    }
  }

  // data.redTeam.forEach(function (player) {
  //   $(".redTeam").append("<li style='color: red;'>" + player + "</li>");
  // });
  // data.blueTeam.forEach(function (player) {
  //   $(".blueTeam").append("<li style='color:blue;'>" + player + "</li>");
  // });
});

socket.on("yourTurn", function (data) {
  var wordIndex = 0;
  console.log("Index: " + wordIndex);
  var correctWords = [];
  var timeLeft = data.turnTimer;
  var timer;
  clearInterval(timer);

  //Prepares the timer
  $("#your-turn").removeClass("hidden");
  $("#your-turn>.ready").removeClass("hidden");
  $("#your-turn>h5").html("Amount of time left: <br>" + timeLeft);
  $("#your-turn>.ready").off("click");
  $("#your-turn>.ready").click(function () {
    $("#current-word").removeClass("hidden");
    $("#your-turn>.ready").addClass("hidden");
    timer = setInterval(function () {
      timeLeft--;
      $("#your-turn>h5").html("Amount of time left: <br>" + timeLeft);
      if (timeLeft === 0) {
        $("#current-word").addClass("hidden");
        $("#your-turn>h5").html("You ran out of time!");
        clearInterval(timer);

        // wait 5 seconds
        var timeout = setTimeout(function () {
          $("#your-turn").addClass("hidden");
          socket.emit("endTurn", {
            correctWords: correctWords,
            room: room_id,
          });
        }, 5000);
      }
    }, 1000);
  });

  // Code that handles whether a word is right or wrong
  $("#current-word>h3").text(data.currentWordList[wordIndex]);
  $("#current-word>button.wrong").off("click");
  $("#current-word>button.wrong").click(function () {
    wordIndex++;
    if (wordIndex >= data.currentWordList.length) {
      clearInterval(timer);
      $("#current-word").addClass("hidden");
      $("#your-turn>h5").html("You've finished all the words!");

      // wait 5 seconds
      var timeout = setTimeout(function () {
        $("#your-turn").addClass("hidden");
        socket.emit("endTurn", {
          correctWords: correctWords,
          room: room_id,
        });
      }, 5000);
    } else $("#current-word>h3").text(data.currentWordList[wordIndex]);
  });

  $("#current-word>button.correct").off("click");
  $("#current-word>button.correct").click(function () {
    correctWords.push(wordIndex);
    wordIndex++;
    if (wordIndex >= data.currentWordList.length) {
      $("#current-word").addClass("hidden");
      $("#your-turn>h5").html("You've finished all the words!");
      clearInterval(timer);

      // wait 5 seconds
      var timeout = setTimeout(function () {
        $("#your-turn").addClass("hidden");
        socket.emit("endTurn", {
          correctWords: correctWords,
          room: room_id,
        });
      }, 5000);
    } else $("#current-word>h3").text(data.currentWordList[wordIndex]);
  });
});

socket.on("playerTurn", function (data) {
  $(".player-turn").removeClass("hidden");
  $(".player-turn").text("It's " + data.currentPlayer + "'s turn");
  $("#scoreBoard .redScore").text("Red: " + data.redScore);
  $("#scoreBoard .blueScore").text("Blue: " + data.blueScore);
});

socket.on("nextRound", function (data) {
  $(".current-round").text("Round " + data.round);
  $("#instructions").removeClass("hidden");
  $(".round" + data.round).removeClass("hidden");
  $(".done-instructions").off();
  $(".done-instructions").click(function () {
    $("#instructions").addClass("hidden");
    $(".round" + data.round).addClass("hidden");
  });
});

socket.on("gameEnded", function (data) {
  $(".current-round").text("Game Ended!");
});
