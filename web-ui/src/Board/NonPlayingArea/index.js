import React from "react";
import GameInfo from "./GameInfo";
import PlayerActions from "./PlayerActions";

const NonPlayingArea = props => {
  return (
    <div className="middle-board">
      <GameInfo />
      <PlayerActions />
    </div>
  );
};

export default NonPlayingArea;
