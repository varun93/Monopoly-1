import React from "react";
import { connect } from "react-redux";
import { setPlayerAction, publishAction } from "redux/actions";
import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";

const MiddleBoard = props => {
  const { setPlayerAction, publishAction } = props;
  return (
    <div className="middle-board">
      <GameInfo />
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

export default connect(
  null,
  mapDispatchToProps
)(MiddleBoard);
