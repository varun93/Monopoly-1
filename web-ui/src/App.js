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
    this.session = null;
    // currently hardcoding game id
    this.gameId = 1;
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
      const joinGameUri = substituteEndpoint(
        constants.JOIN_GAME_ENDPOINT,
        null,
        this.gameId
      );

      session.call(joinGameUri).then(response => {
        const { setMyId, setEndpoints } = this.props;
        const myId = response["agent_id"];
        setMyId(myId);
        delete response["agent_id"];
        setEndpoints(response);
        this.subscribeToEvents(response);
      });
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
    this.session.subscribe(response["BROADCAST_IN"], this.receiveBroadcast);

    this.session.subscribe(
      response["BUY_IN"],
      this.receiveRequest.bind(this, "buy_property")
    );

    this.session.subscribe(
      response["RESPOND_TRADE_IN"],
      this.receiveRequest.bind(this, "trade")
    );
    this.session.subscribe(
      response["AUCTION_IN"],
      this.receiveRequest.bind(this, "auction")
    );
    this.session.subscribe(
      response["BSM_IN"],
      this.receiveRequest.bind(this, "bsm")
    );
    this.session.subscribe(
      response["JAIL_IN"],
      this.receiveRequest.bind(this, "jail_decision")
    );
    this.session.subscribe(
      response["END_GAME_IN"],
      this.receiveRequest.bind(this, "end_game")
    );
    this.session.subscribe(
      response["START_GAME_IN"],
      this.receiveRequest.bind(this, "start_game")
    );
    this.session.subscribe(
      response["END_GAME_IN"],
      this.receiveRequest.bind(this, "end_game")
    );
  };

  startGame = () => {
    this.session.publish("com.monopoly.start");
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

// // #URIs
// join_game_uri = 'com.game{}.joingame'.format(self.game_id)

// 4) call a remote procedure
// );

// // # call a remote procedure.
// res = yield self.call(join_game_uri)
// print("The agent was assigned id: {}".format(res['agent_id']))
// self.id = res['agent_id']

// self.endpoints = res

// // #Successfully Registered. Invoke confirm_register
// response = yield self.call(res['CONFIRM_REGISTER'])
