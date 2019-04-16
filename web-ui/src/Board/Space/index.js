import React, { Component } from "react";
import { connect } from "react-redux";
import { setFormData } from "redux/actions";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import SpaceInfo from "./space-info";
import CardInfo from "./card-info";

class Space extends Component {
  state = {
    show: false,
    housesBought: 0,
    housesSold: 0,
    mortaged: false,
    propertyBought: false
  };

  handleClose = () => {
    this.setState({ show: false });
  };

  handleShow = () => {
    this.setState({ show: true });
  };

  saveChanges = propertyId => {
    const { housesBought, housesSold, mortaged, propertyBought } = this.state;
    this.props.setFormData(propertyId, {
      housesBought,
      housesSold,
      mortaged,
      propertyBought
    });
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
    const { monopoly, class: category, name } = space;
    const {
      handleClose,
      handleShow,
      saveChanges,
      onHousesBrought,
      onHousesSold,
      onMortgaged,
      onPropertyBrought
    } = this;
    const { housesBought, housesSold, propertyBought, mortaged } = this.state;
    const highlighted = candidates.indexOf(space.id) !== -1 ? true : false;

    return (
      <div
        className={`space ${category}  ${highlighted ? "highlight" : ""}
      `}
      >
        {" "}
        <CardInfo space={space} handleShow={handleShow} />
        <Modal show={this.state.show} onHide={handleClose}>
          <Modal.Header style={{ background: monopoly }} closeButton>
            <Modal.Title>{name}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Container>
              {/* Space info */}
              <SpaceInfo space={space} />
              {/* Form Section */}
              {highlighted && playerAction === "buy-constructions" && (
                <Form.Group controlId="formBuyConstructions">
                  <Form.Label>Buy Constructions</Form.Label>
                  <Form.Control
                    min={0}
                    max={4}
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
                    min={0}
                    max={4}
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
                    checked={propertyBought}
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
            <Button variant="primary" onClick={() => saveChanges(index)}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setFormData: (propertyId, formData) =>
      dispatch(setFormData(propertyId, formData))
  };
};

const mapStateToProps = state => {
  return {
    properties: state.properties,
    candidates: state.candidates || [],
    playerAction: state.playerAction
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Space);
