import React from "react";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const SpaceInfo = ({ space }) => {
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
        <Col xs={6} md={6}>
          Rent : {space.rent}
        </Col>
      </Row>
      <Row className="show-grid">
        <Col xs={6} md={6}>
          Rent Hotel : {space.rent_hotel}
        </Col>
        <Col xs={6} md={6}>
          Rent House 1 : {space.rent_house_1}
        </Col>
        <Col xs={6} md={6}>
          Rent House 2 : {space.rent_house_2}
        </Col>
        <Col xs={6} md={6}>
          Rent House 3 : {space.rent_house_3}
        </Col>
        <Col xs={6} md={6}>
          Rent House 4 : {space.rent_house_4}
        </Col>
      </Row>
    </div>
  );
};

export default SpaceInfo;
