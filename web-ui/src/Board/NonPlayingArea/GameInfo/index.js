import React from "react";

const GameInfo = ({ playerInfo }) => {
  playerInfo = playerInfo || {
    cash: 1500,
    position: 7,
    debt: 0,
    properties: [3, 6, 8],
    bankrupt: false
  };
  return (
    <div className="current-player-info">
      <h2 className="label">Current Player Info</h2>
      <div>Cash : {playerInfo.cash}</div>
      <div>Debt : {playerInfo.debt}</div>
    </div>
  );
};

export default GameInfo;
