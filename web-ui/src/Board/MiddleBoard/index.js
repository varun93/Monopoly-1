import React from "react";
import { connect } from "react-redux";
import { setPlayerAction, publishAction } from "redux/actions";
import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";
import MessageBox from "./MessageBox";

const MiddleBoard = props => {
  const {
    setPlayerAction,
    publishAction,
    phase,
    phasePayload,
    properties
  } = props;
  return (
    <div className="middle-board">
      <GameInfo />
      <MessageBox
        phase={phase}
        phasePayload={phasePayload}
        properties={properties}
      />
      <PlayerActions
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
    phase: state.phase,
    properties: state.properties,
    phasePayload: state.rawState.phase_payload
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MiddleBoard);
