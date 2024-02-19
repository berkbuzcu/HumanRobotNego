import * as types from "./types"

export const Initiate = (preferences, deadline) => {
  return {
      type: types.SESSION_START,
      payload: {
          "preferences": preferences,
          "deadline": deadline
      }
  };
};


export const SetPreferences = (issues, issueValues) => {
    return {
        type: types.UPDATE_PREFERENCES,
        payload: {
            "preferences": {"issues": issues, "issue_values": issueValues}
        }
    }
};


export const IncreaseTime = () => {
    return {
        type: types.SESSION_UPDATE_TIME,
        payload: null
    };
};


export const ReceiveUpdate = (data) => {
    return {
        type: types.RECEIVE_UPDATE,
        payload: data
    };
};
