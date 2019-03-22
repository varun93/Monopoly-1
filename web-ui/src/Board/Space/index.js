import React from "react";

const Space = ({
  space
}) => {
  const { monopoly, class: category, name, price } = space;
  return (
    <div className={`space ${category}`}>
      <div className="monopoly-box">
        {monopoly && <div className={`color-bar ${monopoly}`} />}
        {name && <div className="name">{name}</div>}
        {price && <div className="price">Price ${price}</div>}
      </div>
    </div>
  );
};

export default Space;
