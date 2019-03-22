import React, { Component } from "react";
import * as constants from "./constants";
import Space from "./Space";
import properties from "./properties";
import "./style.css";
import UpdatesPanel from "../UpdatesPanel";
import GameInfo from "./GameInfo";

export default class Board extends Component {

  render() {

    return (
      <div className="monopoly-table">
        <div className="board">
          <GameInfo />

          <Space space={properties[0]}/>
          
          <div className="board-row horizontal-board-row bottom-board-row">
            {properties.slice(1,10).reverse()
              .map(prop => (
                <Space space={prop}/>
              ))}
          </div>
          
          <Space space={properties[10]}/>
          
          <div className="board-row vertical-board-row left-board-row">
            {properties.slice(11,20).reverse()
              .map(prop => (
                <Space space={prop}/>
              ))}
          </div>
          
          <Space space={properties[20]}/>
          
          <div className="board-row horizontal-board-row top-board-row">
            {properties.slice(21,30)
              .map(prop => (
                <Space space={prop}/>
              ))}
          </div>

          <Space space={properties[30]}/>
          
          <div className="board-row vertical-board-row right-board-row">
            {properties.slice(31)
              .map(prop => (
                <Space space={prop}/>
              ))}
          </div>
        </div>
        <div class="updates-panel">
          <UpdatesPanel />
        </div>
      </div>
    );
  }
}
