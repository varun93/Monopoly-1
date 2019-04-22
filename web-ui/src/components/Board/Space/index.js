import React from "react";

const Space = ({
  highlighted,
  space,
  togglePropertyModal,
  index,
  playerOnPosition,
  owned
}) => {
  const { monopoly, price, name } = space;

  return (
    <div
      onClick={() => togglePropertyModal(true, index)}
      className={`space ${space.class}  ${highlighted ? "highlight" : ""}`}
    >
      <div className={`${owned.owner} monopoly-box`}>
        {monopoly && <div className={`color-bar ${monopoly}`} />}
        {name && <div className="name">{name}</div>}
        <div className={`center-block ${playerOnPosition.player}`} />
        {price && <div className="price">Price ${price}</div>}
      </div>
    </div>
  );
};

export default Space;
