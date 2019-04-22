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

export const resetForm = () => {
  return { type: actionTypes.RESET_FORM };
};

export const publishAction = () => {
  return { type: actionTypes.PUBLISH_ACTION };
};

export const togglePropertyModal = (
  showPropertyModal,
  selectedPropertyIndex
) => {
  return {
    type: actionTypes.TOGGLE_PROPERTY_MODAL,
    showPropertyModal,
    selectedPropertyIndex
  };
};

export const toggleJailDecisionModal = showJailDecisionModal => {
  return {
    type: actionTypes.TOGGLE_JAIL_DECISION_MODAL,
    showJailDecisionModal
  };
};

export const toggleRentModal = (showRentModal, rent) => {
  return {
    type: actionTypes.TOGGLE_RENT_MODAL,
    showRentModal,
    rent
  };
};
