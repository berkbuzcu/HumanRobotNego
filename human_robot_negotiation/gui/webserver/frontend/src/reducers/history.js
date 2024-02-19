import * as types from "../actions/types"

const initialState = {
    history: {}
};


const historyReducer = (state = initialState, action) => {
    switch (action.type) {
        case types.RECEIVE_UPDATE:
            let updatedHistory = {...state.history};
            updatedHistory[action.payload["round"] + "_" + action.payload["who"]] = {
               "message": action.payload["message"],
               "offerContent": action.payload["offerContent"],
               "who": action.payload["who"],
               "utility": action.payload["utility"]
            };

            return {
                ...state,
                history: updatedHistory
            }
        default:
            return {
                ...state
            };
    }
};


export default historyReducer;
