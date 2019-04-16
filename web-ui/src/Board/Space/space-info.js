import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const SpaceInfo = ({ space }) => {
  let { rent } = space;
  rent = rent || [];
  return (
    <div>
      <Row className="show-grid">
        <Col xs={6} md={12}>
          Ownwer : 1
        </Col>
      </Row>
      <Row className="show-grid">
        <Col xs={6} md={6}>
          Houses Count : 3
        </Col>
        <Col xs={6} md={6}>
          Hotels : Present
        </Col>
      </Row>
      <Row className="show-grid">
        <Col xs={6} md={6}>
          Price : {space.price}
        </Col>
      </Row>
      <Row className="show-grid">
        {rent.map((item, index) => {
          return (
            <Col key={index} xs={6} md={6}>
              Rent {index < 4 ? `House ${index + 1}` : "Rent Hotel"} : {item}
            </Col>
          );
        })}
      </Row>
    </div>
  );
};

export default SpaceInfo;
