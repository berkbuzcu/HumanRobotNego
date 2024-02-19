import PreferencesComponent from "./sessionComponents/PreferencesComponent";
import NegotiationInfoComponent from "./sessionComponents/NegotiationInfoComponent";
import {useEffect, useState} from "react";
import {useDispatch, useSelector} from "react-redux";
import {IncreaseTime, ReceiveUpdate} from "../actions/actions";
import axios from "axios";
import {CLIENT_ADDRESS, SERVER_ADDRESS} from "../config";
import InfoModal, {MODAL_ERROR} from "./modals/InfoModal";
import HistoryComponent from "./sessionComponents/HistoryComponent";


const receiveSessionInfo = async (userName) => {
    try {
       const response = await axios.post( SERVER_ADDRESS + "/receive/" + userName,
           JSON.stringify({}), {
           headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': CLIENT_ADDRESS}
       });

       if (!response.data.error)
           return {"error": false,
               "message": response.data["message"],
               "offerContent": response.data["offer_content"],
               "round": response.data["round"],
               "status": response.data["status"],
               "utility": response.data["utility"],
               "is_completed": response.data["is_completed"],
               "who": response.data["who"],
           };
       else
           return {"error": true, "errorMessage": response.data.errorMessage};

    } catch (e) {
        return {"error": true, "errorMessage": e};
    }
};


const SessionPage = (uuid, setPage) => {
    const userName = useSelector(state => state.user.userName);
    const dispatch = useDispatch();

    const [errorModal, setErrorModal] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    useEffect(() => {
        const interval = setInterval(() => dispatch(IncreaseTime()), 1000);

        return () => clearInterval(interval);
    });

    useEffect(() => {
        const interval = setInterval(() => {
            receiveSessionInfo(userName).then((response) => {
                if (response.error) {
                    setErrorMessage(response.error.errorMessage);
                    setErrorModal(true);
                } else {
                    dispatch(ReceiveUpdate(response));
                }
            });
        }, 1000);

        return () => clearInterval(interval);
    });

    return (
        <>
            <div className="col bg-light m-3">
                <NegotiationInfoComponent />
                <PreferencesComponent />
                <HistoryComponent />
            </div>
            {errorModal && <InfoModal modalType={MODAL_ERROR} setModal={setErrorModal} message={errorMessage}/>}
        </>
    );
};


export default SessionPage;
