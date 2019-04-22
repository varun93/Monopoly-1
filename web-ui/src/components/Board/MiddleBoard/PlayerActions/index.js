import React from "react";
import Button from "react-bootstrap/Button";

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
