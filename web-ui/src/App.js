import React, { Component } from "react";
import { connect } from "react-redux";
import "bootstrap/dist/css/bootstrap.css";
import Board from "./Board";
import Autobahn from "autobahn";
import * as constants from "./constants";
import { substituteEndpoint } from "./utils";
import { receieveMessage, setMyId, setEndpoints } from "./redux/actions";
import "./App.css";

class App extends Component {
  constructor(props, context) {
    super(props, context);
    window.session = null;
    // currently hardcoding game id
    this.gameId = 1;
  }

  componentWillMount() {
    const url = constants.ROUTER_ENDPOINT;
    const realm = constants.APPLICATION_REALM;
    let response = null;

    const connection = new Autobahn.Connection({
      url,
      realm
    });

    connection.onopen = async session => {
      window.session = session;
      const joinGameUri = substituteEndpoint(
        constants.JOIN_GAME_ENDPOINT,
        null,
        this.gameId
      );

      response = await session.call(joinGameUri);
      const { setMyId, setEndpoints } = this.props;
      const myId = response["agent_id"];
      setMyId(myId);
      delete response["agent_id"];
      setEndpoints(response);
      this.subscribeToEvents(response);
      response = await session.call(response["CONFIRM_REGISTER"]);
    };

    connection.open();
  }

  /* Receivers  */
  receiveRequest = (phase, state) => {
    console.log(phase);
    const { receieveMessage } = this.props;
    receieveMessage(state, phase);
  };

  receiveBroadcast = state => {
    console.log(state);
  };

  subscribeToEvents = response => {
    window.session.subscribe(response["BROADCAST_IN"], this.receiveBroadcast);

    window.session.subscribe(
      response["BUY_IN"],
      this.receiveRequest.bind(this, "buy_property")
    );

    window.session.subscribe(
      response["RESPOND_TRADE_IN"],
      this.receiveRequest.bind(this, "trade")
    );
    window.session.subscribe(
      response["AUCTION_IN"],
      this.receiveRequest.bind(this, "auction")
    );
    window.session.subscribe(
      response["BSM_IN"],
      this.receiveRequest.bind(this, "bsm")
    );
    window.session.subscribe(
      response["JAIL_IN"],
      this.receiveRequest.bind(this, "jail_decision")
    );
    window.session.subscribe(
      response["END_GAME_IN"],
      this.receiveRequest.bind(this, "end_game")
    );
    window.session.subscribe(
      response["START_GAME_IN"],
      this.receiveRequest.bind(this, "start_game")
    );
    window.session.subscribe(
      response["END_GAME_IN"],
      this.receiveRequest.bind(this, "end_game")
    );
  };

  startGame = () => {
    window.session.publish("com.monopoly.start");
  };

  render() {
    return (
      <div className="App">
        <Board />
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  receieveMessage: (rawState, phase) =>
    dispatch(receieveMessage(rawState, phase)),
  setMyId: id => dispatch(setMyId(id)),
  setEndpoints: endpoints => dispatch(setEndpoints(endpoints))
});

export default connect(
  null,
  mapDispatchToProps
)(App);
