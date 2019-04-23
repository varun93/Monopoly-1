import React, { Component } from "react";
import { connect } from "react-redux";
import Autobahn from "autobahn";
import Board from "components/Board";
import JailDecision from "components/JailDecision";
import Rent from "components/Rent";
import Button from "react-bootstrap/Button";
import { togglePropertyModal, toggleJailDecisionModal } from "redux/actions";
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
import * as constants from "./constants";
import "./App.css";
import "bootstrap/dist/css/bootstrap.css";

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
    //not implementing trade for the time being; just rejecting all trade responses
    window.session.subscribe(response["RESPOND_TRADE_IN"], state => {
      window.session.publish(response["RESPOND_TRADE_OUT"], [false]);
    });
    window.session.subscribe(response["TRADE_IN"], state => {
      window.session.publish(response["TRADE_OUT"], [false]);
    });

    window.session.subscribe(response["END_TURN_IN"], state => {
      window.session.publish(response["END_TURN_OUT"]);
    });

    window.session.subscribe(
      response["START_TURN_IN"],
      this.receiveRequest.bind(this, "start_turn")
    );

    // TRADE = 1
    // DICE_ROLL = 2
    // BUYING = 3
    // AUCTION = 4
    // PAYMENT = 5
    // JAIL = 6
    // CHANCE_CARD = 7
    // COMMUNITY_CHEST_CARD = 8

    //how do you want to get out jail?
    window.session.subscribe(response["JAIL_IN"], state => {
      const { toggleJailDecisionModal, receieveMessage } = this.props;
      state = JSON.parse(state);
      receieveMessage(state, "jail_decision");
      toggleJailDecisionModal(true);
    });

    //generic receive state
    window.session.subscribe(response["BROADCAST_IN"], state => {
      const { receieveMessage } = this.props;
      state = JSON.parse(state);
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

    //auction property
    window.session.subscribe(response["AUCTION_IN"], state => {
      const { togglePropertyModal, receieveMessage } = this.props;
      state = JSON.parse(state);
      const propertyToAuction = state.phase_payload;
      receieveMessage(state, "auction_property");
      togglePropertyModal(true, propertyToAuction);
    });

    //buy property
    window.session.subscribe(response["BUY_IN"], state => {
      const { receieveMessage, togglePropertyModal } = this.props;
      state = JSON.parse(state);
      const propertyToBuy = parseInt(state.phase_payload);
      receieveMessage(state, "buy_property");
      togglePropertyModal(true, propertyToBuy);
    });

    //do you want to conduct a BSM?
    window.session.subscribe(response["BSM_IN"], state => {
      state = JSON.parse(state);

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
    window.session.subscribe(response["END_GAME_IN"], state => {
      state = JSON.parse(state);
      //display the statistics
      window.session.publish(response["END_GAME_OUT"], []);
    });

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
        <JailDecision />
        <Rent />
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => ({
  receieveMessage: (rawState, phase) =>
    dispatch(receieveMessage(rawState, phase)),
  setMyId: id => dispatch(setMyId(id)),
  setEndpoints: endpoints => dispatch(setEndpoints(endpoints)),
  setCandidates: candidates => dispatch(setCandidates(candidates)),
  togglePropertyModal: (showPropertyModal, selectedPropertyIndex) =>
    dispatch(togglePropertyModal(showPropertyModal, selectedPropertyIndex)),
  toggleJailDecisionModal: showJailDecisionModal =>
    dispatch(toggleJailDecisionModal(showJailDecisionModal))
});

export default connect(
  null,
  mapDispatchToProps
)(App);
