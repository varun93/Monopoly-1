import React, { useState } from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import SpaceInfo from "./SpaceInfo";
import { setFormData, togglePropertyModal } from "redux/actions";
import BuyPropertyForm from "./BuyPropertyForm";
import AuctionPropertyForm from "./AuctionPropertyForm";

const SpaceDetailed = ({
  selectedPropertyIndex,
  showPropertyModal,
  properties,
  candidates,
  phase,
  playerAction,
  buyOutEndpoint,
  auctionEndpoint,
  togglePropertyModal,
  setFormData
}) => {
  const handleClose = (hide = true) => {
    if (hide) togglePropertyModal(false);
  };

  const space = properties[selectedPropertyIndex];
  const [housesBought, setHousesBought] = useState(0);
  const [housesSold, setHousesSold] = useState(0);
  const [mortaged, setMortgaged] = useState(false);
  const buyMortgage =
    ["buy_property", "auction_property"].indexOf(phase) !== -1;
  const closeButton = {
    closeButton: !buyMortgage
  };

  const highlighted =
    candidates.indexOf(selectedPropertyIndex) !== -1 ? true : false;

  return (
    showPropertyModal && (
      <Modal show={showPropertyModal} onHide={() => handleClose(!buyMortgage)}>
        <Modal.Header style={{ background: space.monopoly }} {...closeButton}>
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
                  onChange={event => setHousesBought(event.target.value)}
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
                  onChange={event => setHousesSold(event.target.value)}
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
                  onChange={event => setMortgaged(event.target.checked)}
                  checked={mortaged}
                  type="checkbox"
                  label="Mortgage Property"
                />
              </Form.Group>
            )}
            {/* no set form data required just publish! */}
            {highlighted &&
              [
                "mortage-unmortgage",
                "sell-contructions",
                "buy-constructions"
              ].indexOf(playerAction) !== -1 && (
                <Button
                  variant="primary"
                  onClick={() => {
                    setFormData(selectedPropertyIndex, {
                      housesBought,
                      housesSold,
                      mortaged
                    });
                    handleClose();
                  }}
                  block
                >
                  Save Changes
                </Button>
              )}
          </Container>
        </Modal.Body>
      </Modal>
    )
  );
};

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
