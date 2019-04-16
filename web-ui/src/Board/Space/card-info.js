import React from "react";

const CardInfo = ({ space, handleShow }) => {
  const { monopoly, price, name } = space;

  return (
    <div onClick={handleShow} className="monopoly-box">
      {monopoly && <div className={`color-bar ${monopoly}`} />}
      {name && <div className="name">{name}</div>}
      {price && <div className="price">Price ${price}</div>}
    </div>
  );
};

export default CardInfo;
