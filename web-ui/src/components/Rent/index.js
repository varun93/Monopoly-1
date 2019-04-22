import React from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import { toggleRentModal } from "redux/actions";

const Rent = ({ showRentModal, rent, toggleRentModal }) => {
  return (
    showRentModal && (
      <Modal show={showRentModal} onHide={() => showRentModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Rent</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Container>{/* Body goes here; three buttons */}</Container>
        </Modal.Body>
      </Modal>
    )
  );
};

const mapDispatchToProps = dispatch => {
  return {
    toggleRentModal: (showRentModal, rent) =>
      dispatch(toggleRentModal(showRentModal, rent))
  };
};

const mapStateToProps = state => {
  return {
    showRentModal: state.showRentModal,
    rent: state.rent
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Rent);
