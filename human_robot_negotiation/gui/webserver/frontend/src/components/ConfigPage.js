import {useState} from "react";
import InfoModal, {MODAL_ERROR} from "./modals/InfoModal";
import axios from "axios";
import {CLIENT_ADDRESS, SERVER_ADDRESS} from "../config";

const ConfigPage = ({setUUID, setPage}) => {
  const [fields, setFields] = useState({
    userName: "Berk Buzcu",
    sessionType: "Session 1",
    agentType: "Solver",
    robotType: "Nao",
    deadline: 10,
    facialExpressionModel: "Face Channel",
    humanInput: "Speech",
    domainFile: "C:/Users/Lenovo/Documents/PythonProjects/HumanRobotNego/domains/Holiday_A/Holiday_A.xml"
  });



  const [errorModal, setErrorModal] = useState(false);

  const submitConfig = async (body) => {
    const response = await axios.post(SERVER_ADDRESS + "/initiate/", JSON.stringify(body), {
      headers: {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': CLIENT_ADDRESS}
    });
    if (response.data.error)
      return {"error": true};
    else {
      console.log("UUID: ", response.data.uuid);
      setUUID(response.data.uuid)
      return {"error": false};
    }
  }

  const handleSubmit = async () => {
    await submitConfig(fields);
    setPage("PREFERENCES");
  };

  const updateField = (key, value) => {
    setFields({...fields, [key]: value});
  }

  return (<>
        <div className="card">
          <div className="container text-centery bg-light">
            <div className="card-issueName"><h4>Config Manager</h4></div>

            <div className="mb-3 input-group">
              <label className="input-group-text">User Name</label>
              <input type="text" className="form-control"
                     value={fields["userName"]} onChange={(e) => updateField("userName", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text">Session Type</label>
              <input type="text" className="form-control"
                     value={fields["sessionType"]} onChange={(e) => updateField("sessionType", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text w-20">Agent Type</label>
              <input type="text"
                     className="form-control"
                     value={fields["agentType"]} onChange={(e) => updateField("agentType", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text w-20">Robot Type</label>
              <input type="text"
                     className="form-control"
                     value={fields["robotType"]} onChange={(e) => updateField("robotType", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text">Deadline</label>
              <input type="text"
                     className="form-control"
                     value={fields["deadline"]} onChange={(e) => updateField("deadline", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text">Facial Expression Model</label>
              <input type="text"
                     className="form-control"
                     value={fields["facialExpressionModel"]}
                     onChange={(e) => updateField("facialExpressionModel", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text">Human Input</label>
              <input type="text"
                     className="form-control"
                     value={fields["humanInput"]}
                     onChange={(e) => updateField("humanInput", e.target.value)}/>
            </div>
            <div className="mb-3 input-group">
              <label className="input-group-text">Domain Path</label>
              <input type="text" className="form-control" placeholder="User Name"
                     value={fields["domainFile"]} onChange={(e) => updateField("domainFile", e.target.value)}/>
            </div>

            <div className="card-footer">
              <div className="d-flex justify-content-start">
                <button className="btn-primary btn rounded fw-bold "
                        onClick={handleSubmit}>Submit
                </button>
              </div>
            </div>
          </div>
        </div>

        {errorModal && <InfoModal modalType={MODAL_ERROR} setModal={setErrorModal} message={"errorMessage"}/>}
      </>);
};

export default ConfigPage;
