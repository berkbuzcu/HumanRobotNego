import {useEffect, useState} from "react";
import ReviewPreferencesComponent from "./preferencesComponents/ReviewPageComponents";
import axios from "axios";
import {CLIENT_ADDRESS, SERVER_ADDRESS} from "../config";
import {Initiate} from "../actions/actions";
import InfoModal, {MODAL_ERROR} from "./modals/InfoModal";
import {useDispatch, useSelector} from "react-redux";


const initiateSession = async (uuid) => {
    try {
       const response = await axios.post( SERVER_ADDRESS + "/start_negotiation/",
           JSON.stringify({uuid}), {
           headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': CLIENT_ADDRESS}
       });

       if (!response.data.error)
           return {"error": false, "preferences": response.data["preferences"], "deadline": response.data["deadline"]};
       else
           return {"error": true, "errorMessage": response.data.errorMessage};

    } catch (e) {
        return {"error": true, "errorMessage": e};
    }
};


const ReviewPage = ({uuid, setPage}) => {
    const preferences = useSelector(state => state.session.preferences);

    const [errorModal, setErrorModal] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const [disabled, setDisabled] = useState(false);

    const dispatch = useDispatch();

    useEffect(() => {
        if (JSON.stringify(preferences) === JSON.stringify({})) {
            setPage("PREFERENCES");
        }
    }, [preferences]);

    const handleReset = () => {
        setDisabled(true);
        setPage("PREFERENCES");
    };

    const handleSubmit = async () => {
        setDisabled(true);
        initiateSession(uuid).then((sessionResponse) => {
            if (sessionResponse.error) {
                setErrorMessage(sessionResponse.errorMessage);
                setErrorModal(sessionResponse.error);
            } else {
                dispatch(Initiate(sessionResponse.preferences, sessionResponse.deadline));
                setPage("SESSION");
            }

            setDisabled(false);
        });
    };


    return (
        <>
            <div className=" col-lg-12 col-sm-12 col-md-12 container-fluid">
                <div className="row bg-secondary">
                    <div className="d-inline-flex justify-content-start mt-1">
                        <div className="col align-items-center h-100">
                            <div className="row"><h4><b>Review</b></h4></div>
                            <div className="row p-1"><p>Control your preferences. If it is ok, please click <b>Submit</b> button. Otherwise, click <b>Reset</b> button to edit preferences.</p></div>
                        </div>
                    </div>
                </div>
                <ReviewPreferencesComponent preferences={preferences} />
                <div className="row bg-secondary my-1" style={{height: "10vh"}}>
                    <div className="d-flex justify-content-between align-items-center">
                        <button className="btn btn-danger rounded fw-bold" onClick={handleReset} disabled={disabled}>Reset</button>
                        <button className="btn btn-primary rounded fw-bold" onClick={handleSubmit} disabled={disabled}>Submit</button>
                    </div>
                </div>
            </div>
            {errorModal && <InfoModal modalType={MODAL_ERROR} setModal={setErrorModal} message={errorMessage}/>}
        </>
    );
};

export default ReviewPage;
