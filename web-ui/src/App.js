import React, { Component } from "react";
import { connect } from "react-redux";
import "bootstrap/dist/css/bootstrap.css";
import Board from "./Board";
import Autobahn from "autobahn";
import Button from "react-bootstrap/Button";
import * as constants from "./constants";
import {
  substituteEndpoint,
  getBuyingCandidates,
  getSellingCandidates,
  getMortgageCandidates
} from "utils";
import {
  receieveMessage,
  setMyId,
  setEndpoints,
  setCandidates
} from "./redux/actions";
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

    const connection = new Autobahn.Connection({
      url,
      realm
    });

    connection.onopen = session => {
      window.session = session;
    };

    connection.open();
  }

  startGame = async () => {
    let response = null;

    if (!window.session) return null;

    const session = window.session;

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

  /* Receivers  */
  receiveRequest = (phase, state) => {
    const { receieveMessage } = this.props;
    state = JSON.parse(state[0]);
    receieveMessage(state, phase);
  };

  subscribeToEvents = response => {
    //default responses
    window.session.subscribe(response["RESPOND_TRADE_IN"], state => {
      window.session.publish(response["RESPOND_TRADE_OUT"], [false]);
    });
    window.session.subscribe(response["TRADE_IN"], state => {
      window.session.publish(response["TRADE_OUT"], [false]);
    });
    window.session.subscribe(response["AUCTION_IN"], state => {
      window.session.publish(response["AUCTION_OUT"], [0]);
    });
    window.session.subscribe(response["JAIL_IN"], state => {
      window.session.publish(response["JAIL_OUT"], ["P"]);
    });
    window.session.subscribe(
      response["START_TURN_IN"],
      this.receiveRequest.bind(this, "start_turn")
    );

    //   TRADE = 1
    // DICE_ROLL = 2
    // BUYING = 3
    // AUCTION = 4
    // PAYMENT = 5
    // JAIL = 6
    // CHANCE_CARD = 7
    // COMMUNITY_CHEST_CARD = 8

    //generic receive state
    window.session.subscribe(response["BROADCAST_IN"], state => {
      const { receieveMessage } = this.props;
      state = JSON.parse(state[0]);
      let phase = state.current_phase_number;
      if (phase === 2) {
        phase = "dice_roll";
      }
      if (phase === 4) {
        phase = "auction";
      }
      if (phase === 6) {
        phase = "jail_decision";
      }

      receieveMessage(state, phase);
      window.session.publish(response["BROADCAST_OUT"], []);
    });

    //buy property
    window.session.subscribe(response["BUY_IN"], state => {
      const { receieveMessage } = this.props;
      state = JSON.parse(state[0]);
      const propertyToBuy = state.phase_payload;
      //this is the property I landed on
      //trigger a modal on this property
      // send a redux acion maybe?
      console.log(propertyToBuy);
      receieveMessage(state, "buy_property");
    });

    //do you want to do bsm
    window.session.subscribe(response["BSM_IN"], state => {
      state = JSON.parse(state[0]);
      const buyingCandidates = getBuyingCandidates(state);
      const sellingCandidates = getSellingCandidates(state);
      const mortageCandidates = getMortgageCandidates(state);

      if (
        buyingCandidates.length === 0 &&
        sellingCandidates.length === 0 &&
        mortageCandidates.length === 0
      ) {
        window.session.publish(response["BSM_OUT"], []);
      } else {
        const { receieveMessage } = this.props;
        receieveMessage(state, "bsm");
      }
    });

    //end game
    window.session.subscribe(
      response["END_GAME_IN"],
      this.receiveRequest.bind(this, "end_game")
    );

    //start game
    window.session.subscribe(response["START_GAME_IN"], state => {
      this.receiveRequest.bind(this, "start_game");
      window.session.publish(response["START_GAME_OUT"], []);
    });
  };

  render() {
    const { startGame } = this;
    return (
      <div className="App">
        <Board />
        <Button
          onClick={startGame}
          style={{ marginTop: "40px" }}
          size="lg"
          variant="success"
        >
          Start Game
        </Button>
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  receieveMessage: (rawState, phase) =>
    dispatch(receieveMessage(rawState, phase)),
  setMyId: id => dispatch(setMyId(id)),
  setEndpoints: endpoints => dispatch(setEndpoints(endpoints)),
  setCandidates: candidates => dispatch(setCandidates(candidates))
});

export default connect(
  null,
  mapDispatchToProps
)(App);
