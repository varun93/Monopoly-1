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
    console.log("Finally commit the action to the server");
    console.log(state.formData);
    // window.session.publish(relevantAction, payload)
    // make sure you clear the previous form
    // reset form
    return;
  }

  next(action);
};

export default middleware;
