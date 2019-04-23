import React from "react";
import { connect } from "react-redux";
import { setPlayerAction, publishAction } from "redux/actions";

import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";

const MiddleBoard = props => {
  const {
    setPlayerAction,
    publishAction,
    phase,
    myId,
    startTurnEndpoint,
    playersCash,
    buyOutEndpoint
  } = props;
  return (
    <div className="middle-board">
      <GameInfo playersCash={playersCash} myId={myId} />
      <PlayerActions
        phase={phase}
        startTurnEndpoint={startTurnEndpoint}
        buyOutEndpoint={buyOutEndpoint}
        publishAction={publishAction}
        setPlayerAction={setPlayerAction}
      />
    </div>
  );
};

const mapDispatchToProps = dispatch => {
  return {
    setPlayerAction: playerAction => dispatch(setPlayerAction(playerAction)),
    publishAction: () => dispatch(publishAction())
  };
};

const mapStateToProps = state => {
  return {
    playersCash: state.rawState.player_cash || {},
    myId: state.myId,
    playerAction: state.playerAction,
    phase: state.phase,
    properties: state.properties,
    phasePayload: state.rawState.phase_payload,
    startTurnEndpoint: state.endpoints.START_TURN_OUT
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MiddleBoard);
