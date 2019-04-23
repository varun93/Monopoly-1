import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const SpaceInfo = ({ space }) => {
  let { rent, houses, owned, ownerId, hotel } = space;
  rent = rent || [];
  return (
    <div>
      <Row className="show-grid">
        <Col xs={6} md={12}>
          Owner : {owned ? ownerId : "Unowned"}
        </Col>
      </Row>
      <Row className="show-grid">
        <Col xs={6} md={6}>
          Houses Count : {houses}
        </Col>
        <Col xs={6} md={6}>
          Hotels : {hotel ? "Present" : "Not Present"}
        </Col>
      </Row>
      <Row className="show-grid">
        <Col xs={6} md={6}>
          Price : {space.price}
        </Col>
      </Row>
      <Row className="show-grid">
        {rent.length &&
          rent.map((item, index) => {
            return (
              <Col key={index} xs={6} md={6}>
                Rent
                {index === 0
                  ? " : "
                  : index < 5
                  ? `House ${index + 1} : `
                  : "Rent Hotel : "}
                ${item}
              </Col>
            );
          })}
      </Row>
    </div>
  );
};

export default SpaceInfo;
