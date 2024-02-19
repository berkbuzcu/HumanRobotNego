import {useEffect, useState} from "react";
import {useDispatch, useSelector} from "react-redux";
import axios from "axios";
import {CLIENT_ADDRESS, SERVER_ADDRESS} from "../config";
import {SetPreferences} from "../actions/actions";
import InfoModal, {MODAL_ERROR} from "./modals/InfoModal";
import SortableList from "./preferencesComponents/SortableList";
import {DragDropContext, Draggable, Droppable} from "react-beautiful-dnd";


const submitPreferences = async (uuid, domainInfo, issues, issueValues) => {
    try {
       const response = await axios.post( SERVER_ADDRESS + "/create_preferences",
           JSON.stringify({"uuid": uuid, "domain_info": domainInfo, "preferences": {issues: issues, issue_values: issueValues}}), {
           headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': CLIENT_ADDRESS}
       });

       if (!response.data.error)
           return {"error": false};
       else
           return {"error": true, "errorMessage": response.data.errorMessage};

    } catch (e) {
        return {"error": true, "errorMessage": e};
    }
};


const fetchPreferences = async (uuid) => {
    console.log("UUID: ", uuid);
    const response = await axios.post(SERVER_ADDRESS + "/preferences_info",
        JSON.stringify({uuid}), {
        headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': CLIENT_ADDRESS}
    });
    return response.data;
};


const PreferencesPage = ({uuid, setPage}) => {
    const preferences = useSelector(state => state.session.preferences);

    const [issues, setIssues] = useState([]);
    const [issueValues, setIssueValues] = useState({});

    const [domainInfo, setDomainInfo] = useState({});

    const [disabled, setDisabled] = useState(false);

    const [errorModal, setErrorModal] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");

    const dispatch = useDispatch();

    useEffect(() => {
        if (issues.length === 0) {
            if (JSON.stringify(preferences) === JSON.stringify({})) {
                fetchPreferences(uuid).then((response) => {
                    if (response.error) {
                        setErrorMessage(response.errorMessage);
                        setErrorModal(response.error);
                    } else {
                        console.log(response)
                        setDomainInfo(response);
                        setIssueValues(response["issue_values_list"]);
                        setIssues(response["issue_names"]);
                    }
                });
            } else {
                setIssues(preferences["issues"]);
                setIssueValues(preferences["issue_values"]);
            }
        }
    }, [issues, preferences]);

    const handleSubmit = async () => {
        setDisabled(true);
        submitPreferences(uuid, domainInfo, issues, issueValues).then((submitResponse) => {
            if (submitResponse.error) {
                setErrorMessage(submitResponse.errorMessage);
                setErrorModal(submitResponse.error);
            } else {
                dispatch(SetPreferences(issues, issueValues));
                setPage("REVIEW");
            }

            setDisabled(false);
        });
    };

    const onDragEndIssue = (result) => {
        if (!disabled && result.destination) {
            let newList = [...issues];
            newList.splice(result.source.index, 1);
            newList.splice(result.destination.index, 0, issues[result.source.index]);

            setIssues(newList);
        }
    };

    const setValues = (issueName, values) => {
        let newIssueValues = {...issueValues};
        newIssueValues[issueName] = values;

        setIssueValues(newIssueValues);
    };

    return (
        <>
            <div className="col col-lg-12 col-sm-12 col-md-12 container-fluid">
                {issues.length > 0 &&
                    <div className="row bg-secondary">
                        <div className="d-inline-flex justify-content-start mt-1">
                            <div className="col align-items-center h-100">
                                <div className="row"><h4><b>Preference </b></h4></div>
                                <div className="row p-1"><p>The importance of issues decreases from <b>Left</b> to <b>Right</b>. Besides, the utility of values decreases from <b>Up</b> to <b>Bottom</b></p></div>
                            </div>
                        </div>
                    </div>
                }
                <DragDropContext onDragEnd={onDragEndIssue}>
                    <Droppable droppableId={"droppable_issues"} key={"droppable_issues"} direction="horizontal"
                               type="issues">
                        {(provided, snapshot) => (
                            <div
                                className="row bg-light d-flex justify-content-between m-2" {...provided.droppableProps}
                                ref={provided.innerRef}>
                                {issues.length > 0 && issues.map((issueName, index) => (
                                    <Draggable key={"issues_" + issueName} draggableId={"issues_" + issueName}
                                               index={index} isDragDisabled={disabled}>
                                        {(provided, snapshot) => (
                                            <div className="col dragItem mx-1" ref={provided.innerRef}
                                                 {...provided.draggableProps}
                                                 {...provided.dragHandleProps}
                                                 style={{...provided.draggableProps.style}}>
                                                <SortableList issueName={issueName}
                                                              values={[...issueValues[issueName]]}
                                                              disabled={disabled}
                                                              setValues={setValues}
                                                              issueIndex={index}/>
                                            </div>
                                        )}
                                    </Draggable>
                                ))}
                                {provided.placeholder}
                            </div>
                        )}
                    </Droppable>
                </DragDropContext>
                <div className="row bg-secondary my-1" style={{height: "10vh"}}>
                    {issues.length === 0 && <div className="d-flex justify-content-start align-items-center h-100"><h4
                        className="text-start"><b>Loading...</b></h4></div>}
                    <div className="d-flex justify-content-end align-items-center w-100 h-100">
                        {issues.length > 0 &&
                            <button className="btn btn-primary rounded  fw-bold" onClick={handleSubmit}
                                    disabled={disabled}>Submit</button>}
                    </div>
                </div>
            </div>
            {errorModal && <InfoModal modalType={MODAL_ERROR} setModal={setErrorModal} message={errorMessage}/>}
        </>
    );
};

export default PreferencesPage;
