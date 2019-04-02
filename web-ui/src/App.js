import React, { Component } from "react";
import "bootstrap/dist/css/bootstrap.css";
// import Board from "./Board";
import Autobahn from "autobahn";
import * as constants from "./constants";
import { substituteEndpoint } from "./utils";
import Card from "react-bootstrap/Card";
import Button from "react-bootstrap/Button";

// import TurnChooser from "./TurnChooser";
import "./App.css";

// const autobahn = require("autobahn");

class App extends Component {
  constructor(props, context) {
    super(props, context);
    this.session = null;
    // currently hardcoding game id and agent id
    this.gameId = 1;
    this.agentId = 1;
    this.state = {
      actionButton: "",
      winners: []
    };
  }

  componentWillMount() {
    const url = constants.ROUTER_ENDPOINT;
    const realm = constants.APPLICATION_REALM;

    const connection = new Autobahn.Connection({
      url,
      realm
    });

    connection.onopen = session => {
      this.session = session;
      this.subscribeToEvents();
    };

    connection.open();
  }

  /* Receivers  */
  receiveTradeRequest = state => {
    this.setState({ actionButton: constants.TRADE_ACTION });
    console.log(state);
  };

  receiveAuctionRequest = state => {
    this.setState({ actionButton: constants.AUCTION_ACTION });
    console.log(state);
  };

  receiveBSMRequest = state => {
    this.setState({ actionButton: constants.BSM_ACTION });
    console.log(state);
  };

  receiveJailDecisionRequest = state => {
    this.setState({ actionButton: constants.JAIL_DECISION_ACTION });
    console.log(state);
  };

  receiveEndGameResult = state => {
    // this.setState({ actionButton: constants.JAIL_DECISION_ACTION });
    const result = state[0];
    if (typeof result === "object") {
      //aggregate the results
      // this.setState({ winners: [] });
    } else {
      const winners = this.state.winners.concat(
        JSON.stringify(parseInt(result))
      );
      this.setState({ winners });
    }
  };

  /* Send Response; action listners  */

  sendTradeResponse = event => {
    this.session.publish(substituteEndpoint(constants.TRADE_PUBLISHER));
  };

  sendAuctionResponse = event => {
    this.session.publish(substituteEndpoint(constants.AUCTION_PUBLISHER));
  };

  sendBSMResponse = event => {
    this.session.publish(substituteEndpoint(constants.BSM_PUBLISH));
  };

  sendJailDecisionResponse = event => {
    this.session.publish(substituteEndpoint(constants.JAIL_PUBLISHER));
  };

  subscribeToEvents = () => {
    const { gameId, agentId } = this;
    // this.session.subscribe(
    //   substituteEndpoint(constants.TRADE_RECEIVER, agentId, gameId),
    //   this.receiveTradeRequest
    // );
    // this.session.subscribe(
    //   substituteEndpoint(constants.AUCTION_RECEIVER, agentId, gameId),
    //   this.receiveAuctionRequest
    // );
    // this.session.subscribe(
    //   substituteEndpoint(constants.BSM_RECEIVER, agentId, gameId),
    //   this.receiveBSMRequest
    // );
    // this.session.subscribe(
    //   substituteEndpoint(constants.JAIL_RECEIVER, agentId, gameId),
    //   this.receiveJailDecisionRequest
    // );
    this.session.subscribe(
      substituteEndpoint(constants.END_GAME, agentId, gameId),
      this.receiveEndGameResult
    );
  };

  startGame = () => {
    this.session.publish("com.monopoly.start");
  };

  render() {
    // const { actionButton } = this.state;
    const { startGame } = this;
    const { winners } = this.state;
    // const {
    //   sendAuctionResponse,
    //   sendBSMResponse,
    //   sendJailDecisionResponse,
    //   sendTradeResponse
    // } = this;
    return (
      <div className="App">
        <h1>Monopoly Stats </h1>
        {/* <button
          onClick={sendTradeResponse}
          className="trade"
          disabled={actionButton === "trade" ? "" : "disabled"}
        >
          Trade
        </button>
        <button
          onClick={sendAuctionResponse}
          className="auction"
          disabled={actionButton === "auction" ? "" : "disabled"}
        >
          Auction
        </button>
        <button
          onClick={sendBSMResponse}
          className="bsm"
          disabled={actionButton === "bsm" ? "" : "disabled"}
        >
          BSM
        </button>
        <button
          className="jail-decision"
          disabled={actionButton === "jail-decision" ? "" : "disabled"}
          onClick={sendJailDecisionResponse}
        >
          Jail Decision
        </button> */}
        {/* <Board /> */}

        <Button onClick={startGame} variant="primary">
          Start Game
        </Button>

        <Card>
          {winners.map((winner, index) => {
            return (
              <Card body key={index}>
                Winner of game {index + 1} is agent {winner}
              </Card>
            );
          })}
        </Card>
      </div>
    );
  }
}

export default App;
