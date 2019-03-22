import React from "react";
import Button from 'react-bootstrap/Button'

const GameInfo = () => {
  let playerInfo = {
    cash: 1500,
    position: 7,
    debt: 0,
    properties: [3,6,8],
    bankrupt: false
  };
  return (
    <div className="middle-board">
      <div className="current-player-info">
        <h2 className="label">Current Player Info</h2>
        <div>Cash : {playerInfo.cash}</div>
        <div>Debt : {playerInfo.debt}</div>
      </div>
      <div className="player-actions">
        <h2 className="label">Player Actions</h2>
        <Button variant="primary">Buy Property?</Button>
        <Button variant="secondary">Buy Houses/Hotel</Button>
        <Button variant="success">Sell Houses/Hotel</Button>
        <Button variant="warning">Mortgage/Unmortgage</Button>
        <Button variant="danger">Trade</Button>
        <Button variant="info">Get out of Jail?</Button>
        <Button variant="dark">Bid for Auction</Button>
      </div>
    </div>
  );
};

export default GameInfo;
