import * as actionTypes from "./actionTypes";
import { setCandidates } from "./actions";
const middleware = store => next => async action => {
  const dispatch = store.dispatch;
  const state = store.getState();
  let candidates = [];
  if (action.type === actionTypes.SET_PLAYER_ACTION) {
    const { playerAction } = action;
    if (playerAction === "buy-constructions") {
      candidates = [4, 9, 12];
    } else if (playerAction === "sell-constructions") {
      candidates = [11, 14, 19];
    } else if (playerAction === "mortage-unmortgage") {
      candidates = [20, 25, 29];
    } else if (playerAction === "buy-property") {
      candidates = [21];
    }

    dispatch(setCandidates(candidates));
  }

  if (action.type === actionTypes.PUBLISH_ACTION) {
    const { formData, playerAction, endpoints } = state;
    const payload = [];
    let keyToExtract = "",
      endpoint = "";

    if (formData === null || !Object.keys(formData)) {
      return;
    }

    if (playerAction === "buy-property") {
      keyToExtract = "propertyBought";
      endpoint = endpoints.BUY_OUT;
      payload[0] = true;
    } else {
      if (playerAction === "buy-constructions") {
        keyToExtract = "housesBought";
        payload[0] = "B";
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
    }

    console.log([payload, endpoint]);

    // window.session.publish(endpoint, payload)
    // make sure you clear the previous form
    // reset form
    return;
  }

  next(action);
};

export default middleware;
