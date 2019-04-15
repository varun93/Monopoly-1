import React, { Component } from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";

class Space extends Component {
  state = {
    show: false,
    housesBought: 0,
    housesSold: 0,
    mortaged: false,
    propertyBrought: false
  };

  handleClose = () => {
    this.setState({ show: false });
  };

  handleShow = () => {
    this.setState({ show: true });
  };

  saveChanges = () => {
    const { housesBought, housesSold, mortaged, propertyBrought } = this.state;
    console.log(housesBought, housesSold, mortaged, propertyBrought);
    //now dispatch an action against a property id
    this.setState({ show: false });
  };

  onHousesBrought = event => {
    this.setState({ housesBought: event.target.value });
  };

  onHousesSold = event => {
    this.setState({ housesSold: event.target.value });
  };

  onMortgaged = event => {
    this.setState({ mortaged: event.target.checked });
  };

  onPropertyBrought = event => {
    this.setState({ propertyBrought: event.target.checked });
  };

  render() {
    const { index, properties, candidates, playerAction } = this.props;
    const space = properties[index];
    const { monopoly, class: category, name, price } = space;
    const {
      handleClose,
      handleShow,
      saveChanges,
      onHousesBrought,
      onHousesSold,
      onMortgaged,
      onPropertyBrought
    } = this;
    const { housesBought, housesSold, propertyBrought, mortaged } = this.state;
    const highlighted = candidates.indexOf(space.id) !== -1 ? true : false;

    return (
      <div
        className={`space ${category}  ${highlighted ? "highlight" : ""}
      `}
      >
        <div onClick={handleShow} className="monopoly-box">
          {monopoly && <div className={`color-bar ${monopoly}`} />}
          {name && <div className="name">{name}</div>}
          {price && <div className="price">Price ${price}</div>}
        </div>
        <Modal show={this.state.show} onHide={handleClose}>
          <Modal.Header style={{ background: monopoly }} closeButton>
            <Modal.Title>{name}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Container>
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
                  Price : {price}
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
              {highlighted && playerAction === "buy-constructions" && (
                <Form.Group controlId="formBuyConstructions">
                  <Form.Label>Buy Constructions</Form.Label>
                  <Form.Control
                    onChange={onHousesBrought}
                    type="number"
                    value={housesBought || ""}
                    placeholder="Constructions to Buy"
                  />
                </Form.Group>
              )}

              {highlighted && playerAction === "sell-constructions" && (
                <Form.Group controlId="formSellConstructions">
                  <Form.Label>Sell Constructions</Form.Label>
                  <Form.Control
                    onChange={onHousesSold}
                    type="number"
                    value={housesSold || ""}
                    placeholder="Constructions to Sell"
                  />
                </Form.Group>
              )}

              {highlighted && playerAction === "mortage-unmortgage" && (
                <Form.Group controlId="formMortgageProperty">
                  <Form.Check
                    onChange={onMortgaged}
                    checked={mortaged}
                    type="checkbox"
                    label="Mortgage Property"
                  />
                </Form.Group>
              )}
              {highlighted && playerAction === "buy-property" && (
                <Form.Group controlId="formBuyProperty">
                  <Form.Check
                    onChange={onPropertyBrought}
                    checked={propertyBrought}
                    type="checkbox"
                    label="Buy Property"
                  />
                </Form.Group>
              )}
            </Container>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              Close
            </Button>
            <Button variant="primary" onClick={saveChanges}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    properties: state.properties,
    candidates: state.candidates || [],
    playerAction: state.playerAction
  };
};

export default connect(mapStateToProps)(Space);
