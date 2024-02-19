import { combineReducers } from "redux";
import sessionReducer from "./session"
import historyReducer from "./history";


const rootReducer = combineReducers({
  session: sessionReducer,
  history: historyReducer
});


export default rootReducer;