import React, { Component } from "react";
import 'bootstrap/dist/css/bootstrap.css';
import Board from "./Board";
import TurnChooser from "./TurnChooser";
import "./App.css";

class App extends Component {
  constructor() {
    super(); 

    // hardoced for now
    this.game_id = 1 ;
    this.agent_id = 1;
    this.gameStarted = false;

    // starting Autobahn connection
    //hardcoded for now
    //this.connection = new autobahn.Connection({url: 'ws://127.0.0.1:9000/', realm: 'crossbardemo'});
    //this.connection.onopen = openHander;
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
    this.session.call(res['confirm_register']).then(
       function(res){
          console.log("Result of calling confirm_register: ");
          console.log(res);
       }
    );
  }

  openHander(session, details){
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
    //TODO
  }

  respondTrade(state){
    console.log("Inside respondTrade");
    console.log(state);
  }

  buyProperty(state){
    console.log("Inside buyProperty");
    console.log(state);
  }

  auctionProperty(state){
    console.log("Inside auctionProperty");
    console.log(state);
  }

  jailDecision(state){
    console.log("Inside jailDecision");
    console.log(state);
  }

  receiveState(state){
    //very important. update UI
    console.log("Inside receiveState");
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
