import React, { Component } from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import SpaceInfo from "./space-info";
import { setFormData, togglePropertyModal } from "redux/actions";
import BuyPropertyForm from "./BuyPropertyForm";
import AuctionPropertyForm from "./AuctionPropertyForm";

class SpaceDetailed extends Component {
  state = {
    mortaged: false,
    housesBought: 0,
    housesSold: 0
  };

  handleClose = () => {
    this.props.togglePropertyModal(false);
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

  render() {
    const { handleClose } = this;
    const { housesBought, housesSold, mortaged } = this.state;
    const {
      selectedPropertyIndex,
      showPropertyModal,
      properties,
      candidates,
      phase,
      playerAction,
      buyOutEndpoint,
      auctionEndpoint
    } = this.props;
    const { onHousesBrought, onMortgaged, onHousesSold, saveChanges } = this;
    const space = properties[selectedPropertyIndex];
    const highlighted =
      candidates.indexOf(selectedPropertyIndex) !== -1 ? true : false;

    return (
      showPropertyModal && (
        <Modal show={showPropertyModal} onHide={handleClose}>
          <Modal.Header style={{ background: space.monopoly }} closeButton>
            <Modal.Title>{space.name}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Container>
              {/* Space info */}
              <SpaceInfo space={space} />
              {/* Buy Property Form */}
              {phase === "buy_property" && (
                <BuyPropertyForm
                  buyOutEndpoint={buyOutEndpoint}
                  handleClose={handleClose}
                />
              )}
              {/* Auciton Property Form */}
              {phase === "auction_property" && (
                <AuctionPropertyForm
                  auctionEndpoint={auctionEndpoint}
                  handleClose={handleClose}
                />
              )}
              {/* Form Section */}
              {highlighted && playerAction === "buy-constructions" && (
                <Form.Group controlId="formBuyConstructions">
                  <Form.Label>Buy Constructions</Form.Label>
                  <Form.Control
                    min={space.houses}
                    max={4}
                    onChange={onHousesBrought}
                    type="number"
                    value={housesBought || 0}
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
                    max={space.houses}
                    value={housesSold || 0}
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
            </Container>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              Close
            </Button>
            <Button
              variant="primary"
              onClick={() => saveChanges(selectedPropertyIndex)}
            >
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      )
    );
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setFormData: (propertyId, formData) =>
      dispatch(setFormData(propertyId, formData)),
    togglePropertyModal: (showPropertyModal, selectedPropertyIndex) =>
      dispatch(togglePropertyModal(showPropertyModal, selectedPropertyIndex))
  };
};

const mapStateToProps = state => {
  return {
    selectedPropertyIndex: state.selectedPropertyIndex,
    showPropertyModal: state.showPropertyModal,
    phase: state.phase,
    playerAction: state.playerAction,
    properties: state.properties,
    buyOutEndpoint: state.endpoints.BUY_OUT,
    auctionEndpoint: state.endpoints.AUCTION_OUT,
    candidates: state.candidates || []
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SpaceDetailed);
