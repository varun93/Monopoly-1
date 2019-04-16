import React from "react";

// 	TRADE = 1
// 	DICE_ROLL = 2
// 	BUYING = 3
// 	AUCTION = 4
// 	JAIL = 6
// 	CHANCE_CARD = 7
// 	COMMUNITY_CHEST_CARD = 8

const MessageBox = ({ phase, properties, phasePayload }) => {
  return (
    <div className="message-box">
      <h2 className="label"> Message Box </h2>
      {phase === "dice_roll" && (
        <div>
          Dice rolled was ${phasePayload[0]} and ${phasePayload[1]}
        </div>
      )}
      {phase === "bsm" && <div>Do you want to buy sell or auction? </div>}
      {phase === "buy_property" && (
        <div>
          Do you want to buy property{" "}
          <span style={{ fontWeight: "bold", fontSize: 16 }}>
            {" "}
            {properties[phasePayload].name}{" "}
          </span>{" "}
        </div>
      )}
      {phase === "jail_decision" && (
        <div>How do you want to get out of jail? </div>
      )}
    </div>
  );
};

export default MessageBox;
