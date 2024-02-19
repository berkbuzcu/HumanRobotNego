import * as types from "../actions/types"

const initialState = {
    userName: null
};


const userReducer = (state = initialState, action) => {
    switch (action.type) {
        case types.LOGIN:
            return {
                ...state,
                userName: action.payload["userName"]
            };
        default:
            return {
                ...state
            };
    }
};


export default userReducer;
