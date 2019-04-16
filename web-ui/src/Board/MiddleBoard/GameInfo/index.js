import React from "react";

const GameInfo = ({ playersCash, myId }) => {
  console.log(playersCash, myId);
  return (
    <div className="current-player-info">
      <h2 className="label">Current Player Info</h2>
      <div>Cash :{playersCash[myId]}</div>
    </div>
  );
};

export default GameInfo;
