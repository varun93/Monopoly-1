import * as actionTypes from "./actionTypes";

// {
//     "houses": 0,
//     "hotel": false,
//     "mortgaged": false,
//     "owned": true,
//     "ownerId": "1"
//   }

// "player_board_positions": {
//     "1": 2,
//     "2": 2
//   },
//   "player_cash": {
//     "1": 522,
//     "2": 509
//   },

// NO_ACTION = 0
// TRADE = 1
// DICE_ROLL = 2
// BUYING = 3
// AUCTION = 4
// PAYMENT = 5
// JAIL = 6
// CHANCE_CARD = 7
// COMMUNITY_CHEST_CARD = 8

const initialState = {
  players: [],
  currentPlayer: -1,
  myId: -1,
  currentPhase: -1,
  playerAction: "",
  endpoints: {},
  rawState: {},
  candidates: [],
  properties: {},
  playerCash: {},
  playerBoardPositions: {}
};

const reducer = (state = initialState, action) => {
  switch (action.type) {
    case actionTypes.RECEIVE_MESSAGE:
      const { rawState, phase } = action;
      return {
        ...state,
        rawState,
        phase,
        players: rawState.player_ids,
        currentPlayer: rawState.current_player_id
      };

    case actionTypes.SET_MY_ID:
      const { id: myId } = action;
      return {
        ...state,
        myId
      };

    case actionTypes.SET_ENDPOINTS:
      const { endpoints } = action;
      return {
        ...state,
        endpoints
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

    default:
      return state;
  }
};

export default reducer;
