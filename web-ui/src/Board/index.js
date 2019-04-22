import React, { Component } from "react";
import { connect } from "react-redux";
import Space from "./Space";
import SpaceDetailed from "./SpaceDetailed";
import { range } from "utils";
import "./style.css";
import MiddleBoard from "./MiddleBoard";
import { togglePropertyModal } from "redux/actions";

class Board extends Component {
  getSpaceProps = index => {
    const {
      properties,
      candidates,
      players,
      playersPositions,
      togglePropertyModal
    } = this.props;
    const space = properties[index];
    const key = index;
    const highlighted = candidates.indexOf(index) !== -1 ? true : false;

    return {
      index,
      space,
      key,
      highlighted,
      players,
      playersPositions,
      togglePropertyModal
    };
  };

  render() {
    const { getSpaceProps } = this;

    return (
      <div className="monopoly-table">
        {/* Start of Board */}
        <div className="board">
          <MiddleBoard />

          {/* Actual Grids go here */}
          <Space {...getSpaceProps(0)} />

          {/* Bottom Section */}
          <div className="board-row horizontal-board-row bottom-board-row">
            {range(9).map(index => (
              <Space {...getSpaceProps(10 - (index + 1))} />
            ))}
          </div>

          <Space {...getSpaceProps(10)} />

          {/* Left Section */}
          <div className="board-row vertical-board-row left-board-row">
            {range(9).map(index => (
              <Space {...getSpaceProps(20 - (index + 1))} />
            ))}
          </div>

          <Space {...getSpaceProps(20)} />

          {/* Top Section */}
          <div className="board-row horizontal-board-row top-board-row">
            {range(9).map((prop, index) => (
              <Space {...getSpaceProps(21 + index)} />
            ))}
          </div>

          <Space {...getSpaceProps(30)} />

          {/* Right Section */}
          <div className="board-row vertical-board-row right-board-row">
            {range(9).map((prop, index) => (
              <Space {...getSpaceProps(31 + index)} />
            ))}
          </div>
          {/* End of Game Playing Grids */}
        </div>
        <SpaceDetailed />
      </div>
    );
  }
}

const mapDispatchToProps = dispatch => {
  return {
    togglePropertyModal: (showPropertyModal, selectedPropertyIndex) =>
      dispatch(togglePropertyModal(showPropertyModal, selectedPropertyIndex))
  };
};

const mapStateToProps = state => {
  return {
    players: state.players || [],
    properties: state.properties,
    candidates: state.candidates || [],
    playersPositions: state.playersPositions
  };
};

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Board);
