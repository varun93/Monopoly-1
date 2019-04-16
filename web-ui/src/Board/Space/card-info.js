import React from "react";

const playersMapping = {
  1: { name: "player-one" },
  2: { name: "player-two" }
};

const getPlayerOnPosition = (playersPositons, index) => {
  for (let playerId in playersPositons) {
    if (index === playersPositons[playerId]) {
      return playersMapping[playerId];
    }
  }
  return "";
};

const CardInfo = ({ space, index, playersPositons, handleShow }) => {
  const { monopoly, price, name } = space;
  const playerOnPosition = getPlayerOnPosition(playersPositons, index);
  return (
    <div onClick={handleShow} className="monopoly-box">
      {monopoly && <div className={`color-bar ${monopoly}`} />}
      {name && <div className="name">{name}</div>}
      <div className={`center-block ${playerOnPosition}`} />
      {price && <div className="price">Price ${price}</div>}
    </div>
  );
};

export default CardInfo;
