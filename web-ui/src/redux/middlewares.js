import * as actionTypes from "./actionTypes";
import { setCandidates, resetForm } from "./actions";

const amIOwner = (property, myId) => {
  return property.owned === true && property.ownerId === myId;
};

const completedMonopoly = (properties, property, myId) => {
  for (let index = 0; index < property.monopoly_group_element.length; index++) {
    if (!amIOwner(properties[index], myId)) return false;
    if (properties[index].houses > 0) return false;
  }
  return true;
};

const getBuyingCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "Street") return false;
      if (!amIOwner(property, myId)) return false;
      if (!completedMonopoly(properties, property, myId)) return false;
      return true;
    })
    .map(property => property.id);

  return [4, 9, 12];
};

const getSellingCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "Street") return false;
      if (!amIOwner(property, myId)) return false;
      if (!completedMonopoly(properties, property, myId)) return false;
      return true;
    })
    .map(property => property.id);
  return [11, 14, 19];
};

const getMortgageCandidates = state => {
  const { properties, myId } = state;

  const candidates = properties
    .filter(property => {
      if (property.class !== "Street") return false;
      if (property.mortgaged) return false;
      if (!amIOwner(property, myId)) return false;
      if (!completedMonopoly(properties, property, myId)) {
        if (property.houses > 0 || property.hotel) return false;
      }
      return true;
    })
    .map(property => property.id);

  return [20, 25, 29];
};

const middleware = store => next => async action => {
  const dispatch = store.dispatch;
  const state = store.getState();
  let candidates = [];
  if (action.type === actionTypes.SET_PLAYER_ACTION) {
    const { playerAction } = action;
    if (playerAction === "buy-constructions") {
      candidates = getBuyingCandidates(state);
    } else if (playerAction === "sell-constructions") {
      candidates = getSellingCandidates(state);
    } else if (playerAction === "mortage-unmortgage") {
      candidates = getMortgageCandidates(state);
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
    }

    console.log([payload, endpoint]);

    // window.session.publish(endpoint, payload)
    // make sure you clear the previous form
    // reset form
    dispatch(resetForm());
    return;
  }

  next(action);
};

export default middleware;
