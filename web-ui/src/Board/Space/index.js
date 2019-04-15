import React, { Component } from "react";
import { connect } from "react-redux";
import Modal from "react-bootstrap/Modal";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";

class Space extends Component {
  state = {
    show: false
  };

  handleClose = () => {
    this.setState({ show: false });
  };

  handleShow = () => {
    this.setState({ show: true });
  };

  render() {
    const { index, properties, candidates } = this.props;
    const space = properties[index];
    const { monopoly, class: category, name, price } = space;
    const { handleClose, handleShow } = this;

    return (
      <div
        className={`space ${category}  ${
          candidates.indexOf(space.id) !== -1 ? "highlight" : ""
        }
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
            </Container>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
              Close
            </Button>
            <Button variant="primary" onClick={handleClose}>
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
    candidates: state.candidates || []
  };
};

export default connect(mapStateToProps)(Space);
