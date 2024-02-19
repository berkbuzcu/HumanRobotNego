import "./ReviewPage.css"

const ValueComponent = ({value}) => {
    return (
        <div className="col border rounded border-2 border-black">
            <div className="d-flex align-items-center justify-content-center text-center">
                <span className="text-black">{value}</span>
            </div>
        </div>
    );
};


const IssueComponent = ({issueName, values}) => {
    return (
        <div className="row my-1">
            <div className="col-2 d-flex align-items-center justify-content-start text-center">
                <b>{issueName}</b>
            </div>
            <div className="col-10">
                <div className="row d-flex justify-content-between">
                    {values.length > 0 && values.map((value) => <ValueComponent value={value} issueName={issueName}
                                                                                key={issueName + value}/>)}
                </div>
            </div>
        </div>
    );
};


const ReviewPreferencesComponent = ({preferences}) => {
    return (
      <div className="row border border-2 rounded issue-value-component">
          <div className="col h-100">
              {preferences["issues"].length > 0 && preferences["issues"].map((issueName) => <IssueComponent issueName={issueName} values={preferences["issue_values"][issueName]} key={issueName} />)}
          </div>
      </div>
    );
};

export default ReviewPreferencesComponent;
