import React from "react";
import CardInfo from "./card-info";

const Space = ({ highlighted, space, index, togglePropertyModal, ...rest }) => {
  return (
    <div
      onClick={() => togglePropertyModal(true, index)}
      className={`space ${space.class}  ${highlighted ? "highlight" : ""}`}
    >
      <CardInfo space={space} index={index} {...rest} />
    </div>
  );
};

export default Space;
