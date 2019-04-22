import React from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Container from "react-bootstrap/Container";
import { toggleJailDecisionModal } from "redux/actions";

const JailDecision = ({ showJailDecisionModal, toggleJailDecisionModal }) => {
  return (
    showJailDecisionModal && (
      <Modal
        show={showJailDecisionModal}
        onHide={() => showJailDecisionModal(false)}
      >
        <Modal.Header closeButton>
          <Modal.Title>Get out of Jail</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>
            <Button variant="success">Roll a Double</Button>
            <Button variant="warning">Pay $100</Button>
            <Button variant="secondary">Use Get Out of Jail Card</Button>
          </Container>
        </Modal.Body>
      </Modal>
    )
  );
};

const mapDispatchToProps = dispatch => {
  return {
    toggleJailDecisionModal: showJailDecisionModal =>
      dispatch(toggleJailDecisionModal(showJailDecisionModal))
  };
};

const mapStateToProps = state => {
  return {
    showJailDecisionModal: state.showJailDecisionModal
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(JailDecision);
