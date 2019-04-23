import React, { Component } from "react";
import { connect } from "react-redux";
import Autobahn from "autobahn";
import Board from "components/Board";
import JailDecision from "components/JailDecision";
import ToastMessage from "components/ToastMessage";
import Button from "react-bootstrap/Button";
import {
  substituteEndpoint,
  getBuyingCandidates,
  getSellingCandidates,
  getMortgageCandidates,
  calculateRent
} from "utils";
import {
  receieveMessage,
  setMyId,
  setEndpoints,
  setCandidates,
  togglePropertyModal,
  toggleJailDecisionModal,
  toggleToastMessageModal
} from "redux/actions";
import * as constants from "./constants";
import "./App.css";
import "bootstrap/dist/css/bootstrap.css";
import { setTimeout } from "timers";
import { mergeProperties } from "./utils";

class App extends Component {
  constructor(props, context) {
    super(props, context);
    window.session = null;
    // currently hardcoding game id
    this.gameId = 1;
  }

  //deprecated
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
      const { receieveMessage, toggleToastMessageModal, myId } = this.props;
      state = JSON.parse(state);
      let phase = constants.PhaseNameMapping[state.current_phase_number];
      const currentPlayer = state.current_player_id;
      const phasePayload = state.phase_payload;
      let message = "",
        title = "",
        currentPlayerName = "",
        opponentPlayerName = "";

      if (myId === currentPlayer) {
        currentPlayerName = "Human";
        opponentPlayerName = "Robot";
      } else {
        currentPlayerName = "Robot";
        opponentPlayerName = "Human";
      }

      if (phase === "chance_card") {
        title = "Chance Card";
        message = `${currentPlayerName} won a Chance Card - ${
          constants.chanceCards[phasePayload].content
        }`;
      }

      if (phase === "community_chest_card") {
        title = "Community Chest Card";
        message = `${currentPlayerName} won a Community Chest Card - ${
          constants.communityChestCards[phasePayload].content
        }`;
      }

      if (phase === "payment") {
        title = "Rent";
        const rent = calculateRent(state.player_debts, currentPlayer);
        message = `Player ${currentPlayerName} landed on ${opponentPlayerName}'s property. 
        ${currentPlayerName} pays ${opponentPlayerName} - ${rent}`;
      }

      if (message && message.length) {
        //automatically close the modal after 5 seconds
        setTimeout(() => {
          receieveMessage(state, phase);
          toggleToastMessageModal(false);
          window.session.publish(response["BROADCAST_OUT"], []);
        }, 5000);
        toggleToastMessageModal(true, title, message);
      } else {
        receieveMessage(state, phase);
        window.session.publish(response["BROADCAST_OUT"], []);
      }
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

    //Cconduct a BSM
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
        <ToastMessage />
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
    dispatch(toggleJailDecisionModal(showJailDecisionModal)),
  toggleToastMessageModal: (showToastMessage, toastTitle, toastMessage) =>
    dispatch(
      toggleToastMessageModal(showToastMessage, toastTitle, toastMessage)
    )
});

const mapStateToProps = state => {
  return {
    myId: state.myId
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(App);
