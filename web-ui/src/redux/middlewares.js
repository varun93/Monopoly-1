import * as actionTypes from "./actionTypes";
import { setBSMCandidates, resetForm } from "./actions";
import {
  getBuyingCandidates,
  getSellingCandidates,
  getMortgageCandidates
} from "utils";

const middleware = store => next => async action => {
  const dispatch = store.dispatch;
  let state = store.getState();

  if (action.type === actionTypes.RECEIVE_MESSAGE && action.phase === "bsm") {
    next(action);

    state = store.getState();

    const buyingCandidates = getBuyingCandidates(state);
    const sellingCandidates = getSellingCandidates(state);
    const mortgageCandidates = getMortgageCandidates(state);

    if (
      buyingCandidates.length === 0 &&
      sellingCandidates.length === 0 &&
      mortgageCandidates.length === 0
    ) {
      window.session.publish(state.endpoints.BSM_OUT, []);
    }

    dispatch(
      setBSMCandidates({
        buyingCandidates,
        sellingCandidates,
        mortgageCandidates
      })
    );
  }

  // finally send to adjudicator
  else if (action.type === actionTypes.PUBLISH_ACTION) {
    const { formData, playerAction } = state;
    const { endpoints } = state;
    const payload = [];

    let keyToExtract = "",
      endpoint = "";

    if (formData === null || !Object.keys(formData)) {
      return;
    }

    if (playerAction === "buy-constructions") {
      keyToExtract = "housesBought";
      payload[0] = "BHS";
      endpoint = endpoints.BSM_OUT;
    } else if (playerAction === "sell-constructions") {
      keyToExtract = "housesSold";
      payload[0] = "S";
      endpoint = endpoints.BSM_OUT;
    } else if (playerAction === "mortage-unmortgage") {
      keyToExtract = "mortgaged";
      payload[0] = "M";
      endpoint = endpoints.BSM_OUT;
    }

    payload[1] = Object.keys(formData).map(key => {
      return key;
    });

    window.session.publish(endpoint, [payload]);
    //toggle the modal
    dispatch(resetForm());
    next(action);
  } else {
    next(action);
  }
};

export default middleware;
