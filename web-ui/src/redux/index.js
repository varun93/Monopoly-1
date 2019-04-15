import { createStore, applyMiddleware } from "redux";
import reducer from "./reducers";
import thunk from "redux-thunk";
import properties from "./properties";
import monopolyMiddleware from "./middlewares";

const middlewares = [];

//register our middleware
middlewares.push(monopolyMiddleware);
middlewares.push(thunk);

if (process.env.NODE_ENV === "development") {
  const { logger } = require("redux-logger");
  middlewares.push(logger);
}

const store = createStore(
  reducer,
  { properties },
  applyMiddleware(...middlewares)
);

export default store;
