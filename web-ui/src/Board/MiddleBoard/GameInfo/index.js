import React from "react";
import Col from "react-bootstrap/Col";

const GameInfo = ({ playersCash }) => {
  return (
    <div className="current-player-info">
      <h2 className="label">Current Player Info</h2>
      <div>Cash : {1}</div>
      {/* <div>Debt : {playerInfo.debt}</div> */}
    </div>
  );
};

export default GameInfo;
