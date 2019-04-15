import * as actionTypes from "./actionTypes";

export const receieveMessage = (rawState, phase) => {
  return { type: actionTypes.RECEIVE_MESSAGE, rawState, phase };
};

export const setMyId = id => {
  return { type: actionTypes.SET_MY_ID, id };
};

export const setEndpoints = endpoints => {
  return { type: actionTypes.SET_ENDPOINTS, endpoints };
};

export const setPlayerAction = playerAction => {
  return { type: actionTypes.SET_PLAYER_ACTION, playerAction };
};

export const setCandidates = candidates => {
  return { type: actionTypes.SET_CANDIDATES, candidates };
};

export const setFormData = (propertyId, formData) => {
  return { type: actionTypes.SET_FORM_DATA, propertyId, formData };
};
