import React, { Component } from "react";
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import Table from 'react-bootstrap/Table';
import "./styles.css";


export default class UpdatesPanel extends Component {

  render() {

    return (
		<Tabs fill defaultActiveKey="activity" id="updates-panel">
			<Tab eventKey="activity" title="Activity">
				<div class="activity-panel">
					<p style={{textDecoration: "underline", fontSize: "16px"}}>Turn 10:</p>
					<p style={{textDecoration: "underline", fontSize: "14px"}}>Player 2:</p>
					<p>The player rolled a 4 and a 2.</p>
					<p>The player landed on Vermont Avenue.</p>
					<p>The player unmortgages St. Charles Place spending $25.</p>
					<p>The player decides to buy it spending $120.</p>
					<p style={{textDecoration: "underline", fontSize: "14px"}}>Player 3:</p>
					<p>The player rolled a 4 and a 2.</p>
					<p>The player landed on Vermont Avenue.</p>
					<p>The player unmortgages St. Charles Place spending $25.</p>
					<p>The player decides to buy it spending $120.</p>
				</div>
			</Tab>
			<Tab eventKey="other-players" title="Other Players">
				<div class="other-players-panel">
					<div class="player-card">
						<p style={{textDecoration: "underline", fontSize: "14px"}}>Player 2:</p>
						<Table striped bordered hover>
						  <tbody>
						    <tr>
						      <th>Cash</th>
						      <td>$1500</td>
						    </tr>
						    <tr>
						      <th>Position</th>
						      <td>Med. Avenue (2)</td>
						    </tr>
						    <tr>
						      <th>Is the player active?</th>
						      <td>Yes</td>
						    </tr>
						    <tr>
						      <th>Is the player in Jail?</th>
						      <td>No</td>
						    </tr>
						    <tr>
								<th>Properties</th>
								<td>
									<Table striped bordered hover>
									<tbody>
										<tr>
											<th>Med. Avenue</th>
											<td>Owned</td>
										</tr>
										<tr>
											<th>Penn Avenue</th>
											<td>4 Houses</td>
										</tr>
										<tr>
											<th>Mayfair</th>
											<td>Mortgaged</td>
										</tr>
									</tbody>
								</Table>
								</td>
							</tr>
						  </tbody>
						</Table>
					</div>
				</div>
			</Tab>
		</Tabs>
    );
  }
}