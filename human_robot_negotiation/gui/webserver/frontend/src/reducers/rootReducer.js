import { combineReducers } from "redux";
import userReducer from "./user";
import sessionReducer from "./session"
import historyReducer from "./history";


const rootReducer = combineReducers({
  user: userReducer,
  session: sessionReducer,
  history: historyReducer
});


export default rootReducer;