import React from "react";
import Button from "react-bootstrap/Button";

const PlayerActions = ({
  onBuyProperty,
  onBuyConstructions,
  onSellConsructions,
  onMortgageProperty,
  onTrade,
  onJailDecision,
  onAuctionBid,
  onStartTurn
}) => {
  return (
    <div className="player-actions">
      <h2 className="label">Player Actions</h2>
      <Button onClick={onBuyProperty} variant="primary">
        Buy Property?
      </Button>
      <Button onClick={onBuyConstructions} variant="secondary">
        Buy Houses/Hotel
      </Button>
      <Button onClick={onSellConsructions} variant="success">
        Sell Houses/Hotel
      </Button>
      <Button onClick={onMortgageProperty} variant="warning">
        Mortgage/Unmortgage
      </Button>
      <Button onClick={onTrade} variant="danger">
        Trade
      </Button>
      <Button onClick={onJailDecision} variant="info">
        Get out of Jail?
      </Button>
      <Button onClick={onAuctionBid} variant="dark">
        Bid for Auction
      </Button>
      <Button onClick={onStartTurn} variant="primary">
        Start Turn
      </Button>
    </div>
  );
};

export default PlayerActions;

{
  /* <button
onClick={sendTradeResponse}
className="trade"
disabled={actionButton === "trade" ? "" : "disabled"}
>
Trade
</button>
<button
onClick={sendAuctionResponse}
className="auction"
disabled={actionButton === "auction" ? "" : "disabled"}
>
Auction
</button>
<button
onClick={sendBSMResponse}
className="bsm"
disabled={actionButton === "bsm" ? "" : "disabled"}
>
BSM
</button>
<button
className="jail-decision"
disabled={actionButton === "jail-decision" ? "" : "disabled"}
onClick={sendJailDecisionResponse}
>
Jail Decision
</button> */
}
