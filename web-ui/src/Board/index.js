import React, { Component } from "react";
import Space from "./Space";
import "./style.css";
import MiddleBoard from "./MiddleBoard";

// https://stackoverflow.com/questions/3895478/does-javascript-have-a-method-like-range-to-generate-a-range-within-the-supp
const range = (size, startAt = 0) => {
  return [...Array(size).keys()].map(i => i + startAt);
};

//this should connect to re
export default class Board extends Component {
  render() {
    return (
      <div className="monopoly-table">
        {/* Start of Board */}
        <div className="board">
          <MiddleBoard />

          {/* Actual Grids go here */}
          <Space key={0} index={0} />

          {/* Bottom Section */}
          <div className="board-row horizontal-board-row bottom-board-row">
            {range(9).map(index => (
              <Space key={10 - (index + 1)} index={10 - (index + 1)} />
            ))}
          </div>

          <Space key={10} index={10} />

          {/* Left Section */}
          <div className="board-row vertical-board-row left-board-row">
            {range(9).map(index => (
              <Space key={20 - (index + 1)} index={20 - (index + 1)} />
            ))}
          </div>

          <Space key={20} index={20} />

          {/* Top Section */}
          <div className="board-row horizontal-board-row top-board-row">
            {range(9).map((prop, index) => (
              <Space key={index + 21} index={index + 21} />
            ))}
          </div>

          <Space key={30} index={30} />

          {/* Right Section */}
          <div className="board-row vertical-board-row right-board-row">
            {range(9).map((prop, index) => (
              <Space key={index + 31} index={index + 31} />
            ))}
          </div>
          {/* End of Game Playing Grids */}
        </div>
      </div>
    );
  }
}
