import React from "react";
import { connect } from "react-redux";
import { setPlayerAction } from "redux/actions";
import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";

const MiddleBoard = props => {
  const { setPlayerAction } = props;
  return (
    <div className="middle-board">
      <GameInfo />
      <PlayerActions setPlayerAction={setPlayerAction} />
    </div>
  );
};

const mapDispatchToProps = dispatch => {
  return {
    setPlayerAction: playerAction => dispatch(setPlayerAction(playerAction))
  };
};

export default connect(
  null,
  mapDispatchToProps
)(MiddleBoard);
