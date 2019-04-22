import React from "react";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Container from "react-bootstrap/Container";

const PlayerActions = ({
  phase,
  buyOutEndpoint,
  startTurnEndpoint,
  setPlayerAction,
  publishAction
}) => {
  const click = playerAction => {
    setPlayerAction(playerAction);
  };

  return (
    <div className="player-actions">
      <h2 className="label">Player Actions</h2>
      {phase === "buy_property" && (
        <Container>
          <Form.Label as="legend" column>
            Buy Property?
          </Form.Label>
          <Form.Check
            onChange={event => {
              window.session.publish(buyOutEndpoint, [true]);
            }}
            type="radio"
            label="Yes"
            name="formHorizontalRadios"
            id="formHorizontalRadios1"
          />
          <Form.Check
            onChange={event => {
              window.session.publish(buyOutEndpoint, [false]);
            }}
            type="radio"
            label="No"
            name="formHorizontalRadios"
            id="formHorizontalRadios2"
          />
        </Container>
      )}

      {phase === "bsm" && (
        <div>
          <Button
            onClick={click.bind(null, "buy-constructions")}
            variant="secondary"
          >
            Buy Constructions
          </Button>
          <Button
            onClick={click.bind(null, "sell-constructions")}
            variant="success"
          >
            Sell Constructions
          </Button>
          <Button
            onClick={click.bind(null, "mortage-unmortgage")}
            variant="warning"
          >
            Mortgage/Unmortgage
          </Button>
          <Button onClick={() => publishAction()} variant="danger" size="lg">
            Commit Action
          </Button>
        </div>
      )}

      {phase === "start_turn" && (
        <Button
          onClick={() => {
            window.session.publish(startTurnEndpoint);
          }}
          variant="secondary"
        >
          Start Turn
        </Button>
      )}
    </div>
  );
};

export default PlayerActions;
