import * as types from "../actions/types"

const initialState = {
    preferences: {},
    round: -1,
    status: null,
    isCompleted: false,
    minutes: 0,
    seconds: 0,
    deadline: 0
};


const sessionReducer = (state = initialState, action) => {
    switch (action.type) {
        case types.SESSION_START:
            return {
                ...state,
                preferences: action.payload["preferences"],
                round: 0,
                status: "AGENT_LISTENING",
                isCompleted: false,
                minutes: action.payload["deadline"],
                seconds: 0,
                message: "",
                offerContent: {},
                deadline: action.payload["deadline"]
            };
        case types.UPDATE_PREFERENCES:
            return {
                ...state,
                preferences: action.payload["preferences"]
            };
        case types.SESSION_UPDATE_TIME:
            let newSeconds = state.seconds - 1;
            let newMinutes = state.minutes;

            if (newSeconds < 0) {
                newSeconds = 59;
                newMinutes -= 1;
            }

            return {
                ...state,
                seconds: newSeconds,
                minutes: newMinutes
            };
        case types.RECEIVE_UPDATE:
            return {
                ...state,
                round: action.payload["round"],
                status: action.payload["status"],
                isCompleted: action.payload["isCompleted"]
            }
        default:
            return {
                ...state
            };
    }
};


export default sessionReducer;
