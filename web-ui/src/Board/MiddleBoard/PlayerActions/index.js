import React from "react";
import Button from "react-bootstrap/Button";

const PlayerActions = props => {
  const { phase, playerAction } = props;
  const click = playerAction => {
    props.setPlayerAction(playerAction);
  };

  return (
    <div className="player-actions">
      <h2 className="label">Player Actions</h2>
      {phase === "buy_property" && (
        <Button onClick={click.bind(null, "buy-property")} variant="primary">
          Buy Property
        </Button>
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
        </div>
      )}
      <div>
        <Button onClick={click.bind(null, "start-turn")} variant="primary">
          Start Turn
        </Button>
      </div>
      {playerAction && (
        <Button
          onClick={() => props.publishAction()}
          variant="danger"
          size="lg"
        >
          Commit Changes
        </Button>
      )}
    </div>
  );
};

export default PlayerActions;
