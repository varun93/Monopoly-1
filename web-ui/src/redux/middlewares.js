import * as actionTypes from "./actionTypes";
import { setCandidates, resetForm } from "./actions";
import {
  getBuyingCandidates,
  getSellingCandidates,
  getMortgageCandidates
} from "utils";

// window.session.publish(endpoints.BSM_OUT, payload);

const middleware = store => next => async action => {
  const dispatch = store.dispatch;
  const state = store.getState();
  let candidates = [];
  const payload = [];
  let keyToExtract = "",
    endpoint = "";
  const { endpoints } = state;

  //this happens on click of a button
  if (action.type === actionTypes.SET_PLAYER_ACTION) {
    const { playerAction } = action;
    const buyingCandidates = getBuyingCandidates(state);
    const sellingCandidates = getSellingCandidates(state);
    const mortageCandidates = getMortgageCandidates(state);

    if (
      buyingCandidates.length === 0 &&
      sellingCandidates.length === 0 &&
      mortageCandidates.length === 0
    ) {
      return;
    }

    if (playerAction === "buy-constructions") {
      candidates = buyingCandidates;
    } else if (playerAction === "sell-constructions") {
      candidates = sellingCandidates;
    } else if (playerAction === "mortage-unmortgage") {
      candidates = mortageCandidates;
    }

    dispatch(setCandidates(candidates));
  }

  // finally send to adjudicator
  if (action.type === actionTypes.PUBLISH_ACTION) {
    const { formData, playerAction } = state;

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
      keyToExtract = "mortgage";
      payload[0] = "M";
      endpoint = endpoints.BSM_OUT;
    }
    payload[1] = Object.keys(formData).map(key => {
      return [key, formData[key][keyToExtract]];
    });

    console.log([payload, endpoint]);

    window.session.publish(endpoint, payload);
    //toggle the modal
    dispatch(resetForm());
    return;
  }

  next(action);
};

export default middleware;
