import * as actionTypes from "./actionTypes";

const mergeProperties = (current, incoming) => {
  const merged = current.map((property, index) => {
    return {
      ...property,
      ...incoming[index]
    };
  });

  return merged;
};

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.RECEIVE_MESSAGE:
      const { rawState, phase } = action;
      return {
        ...state,
        rawState,
        phase,
        properties: mergeProperties(state.properties, rawState.properties),
        players: rawState.player_ids,
        currentPlayer: rawState.current_player_id,
        playersPositions: rawState.player_board_positions,
        playersCash: rawState.player_cash
      };

    case actionTypes.SET_MY_ID:
      const { id: myId } = action;
      return {
        ...state,
        myId: myId
      };

    case actionTypes.SET_ENDPOINTS:
      const { endpoints } = action;
      return {
        ...state,
        endpoints: endpoints
      };

    case actionTypes.SET_PLAYER_ACTION:
      const { playerAction } = action;
      return {
        ...state,
        playerAction
      };

    case actionTypes.SET_CANDIDATES:
      const { candidates } = action;
      return {
        ...state,
        candidates
      };

    case actionTypes.SET_FORM_DATA:
      const { formData, propertyId } = action;
      return {
        ...state,
        formData: {
          ...state.formData,
          [propertyId]: formData
        }
      };

    case actionTypes.RESET_FORM:
      return {
        ...state,
        formData: {},
        playerAction: ""
      };

    default:
      return state;
  }
};

export default reducer;
