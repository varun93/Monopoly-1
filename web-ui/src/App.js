import React, { Component } from "react";
import 'bootstrap/dist/css/bootstrap.css';
import Board from "./Board";
import "./App.css";

class App extends Component {
  constructor() {
    super(); 

    // hardoced for now
    this.game_id = 1 ;
    this.agent_id = 1;
    this.gameStarted = false;

    this.buttonSwitches = {
      startTurn: false,
      buyProperty: false,
      auctionProperty: false,
      BSMDecision: false,
      tradeDecision: false,
      jailDecision: false
    };

    this.logMessages = [];

    // starting Autobahn connection
    //hardcoded for now
    //this.connection = new autobahn.Connection({url: 'ws://127.0.0.1:9000/', realm: 'crossbardemo'});
    //this.connection.onopen = openHandler;
  }

  didGameEnd = () => {};

  startAgent(){
    //this.connection.open();
    this.gameStarted = true;
   }

  joinGameCallback(res){
    this.session.register(res['bsm'], this.getBSMTDecision);
    this.session.register(res['respondtrade'], this.respondTrade);
    this.session.register(res['buy'], this.buyProperty);
    this.session.register(res['auction'], this.auctionProperty);
    this.session.register(res['jail'], this.jailDecision);
    this.session.register(res['receivestate'], this.receiveState);
    this.session.register(res['trade'], this.getTradeDecision);

    // subsribe for end game results
    this.session.subscribe(res["endgame"],this.endGame);

    // Successfully Registered. Invoke confirm_register
    this.session.call(res['confirm_register']).then(this.confirmRegisterCallback);
  }

  //could we use the return value here for something?
  confirmRegisterCallback(res){
    console.log("Result of calling confirm_register: ");
    console.log(res);
  }

  openHandler(session, details){
    console.log("Human Player with id: "+this.agent_id+" connected");
    this.session = session
    let join_game_uri = 'com.game{}.joingame'.replace('{}',this.game_id)
    session.call(join_game_uri).then(this.joinGameCallback);
  }

  endGame(result){
    console.log("Game has ended");
    console.log(result);
  }

  getBSMTDecision(state){
    console.log("Inside getBSMTDecision");
    console.log(state);

    return null;
    //TODO
  }

  respondTrade(state){
    console.log("Inside respondTrade");
    console.log(state);
    return false;
  }

  buyProperty(state){
    console.log("Inside buyProperty");
    console.log(state);

    this.buttonSwitches.buyProperty = true;
  }

  auctionProperty(state){
    console.log("Inside auctionProperty");
    console.log(state);

    this.buttonSwitches.auctionProperty = true;

    return 0;
  }

  jailDecision(state){
    console.log("Inside jailDecision");
    console.log(state);

    this.buttonSwitches.jailDecision = true;
  }

  receiveState(state){
    //very important. update UI
    //we need to record all actions since the last time the human player had a turn.
    //we also need to log actions the human player takes in the current turn.
    //at the start of the human player's turn, he/she should first receive a dice roll receivestate call.
    //we will use this to give a prompt to the user to start their turn.
    console.log("Inside receiveState");
    let jsonState = JSON.parse(state);
    let phase = jsonState.current_phase_number;
    let payload = jsonState.phase_payload;
    if (phase == Phase.DICE_ROLL && payload) {
      this.logMessages.push("Dice roll was a "+payload[0]+" and a "+payload[1]+".");
    }
    else if (phase == Phase.JAIL){
      if (payload == undefined) {
        this.logMessages.push("This player has been sent to Jail.");  
      }
      else if(payload) {
        this.logMessages.push("The player is out of Jail.");
      }
      else {
        this.logMessages.push("The player remains in Jail."); 
      }
    }
    console.log(state);
  }

  getTradeDecision(state){
    console.log("Inside getTradeDecision");
    console.log(state);
  }

  render() {
    return (
      <div className="App">
        <button type="button" className="center-block start-game btn btn-primary">
          Start Game
        </button>
        <Board />
      </div>
    );
  }
}

export default App;
