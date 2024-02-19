import {useSelector} from "react-redux";
import {useEffect, useState} from "react";
import "./Session.css"


const ValueComponent = ({issueName, value}) => {
    const history = useSelector(state => state.history.history);
    const round = useSelector(state => state.session.round);
    const isCompleted = useSelector(state => state.session.isCompleted);

    const [who, setWho] = useState("AGENT");
    const [offerContent, setOfferContent] = useState({});

    const [className, setClassName] = useState("");
    const [borderClass, setBorderClass] = useState("border-2 border-black");

    useEffect(() => {
        if (issueName in offerContent) {
            if (offerContent[issueName] === value) {
                if (who === 'HUMAN')
                    setClassName("offer-human");
                else
                    setClassName("offer-agent");
            } else {
                setClassName("text-muted");
            }

            setBorderClass("border-1");
        } else {
            setClassName("text-black");
            setBorderClass("border-2 border-black");
        }
    }, [offerContent, issueName, value, who]);


    useEffect(() => {
        for (let i = round; i >= 0; --i) {
            // Human Control
            let key = i + "_HUMAN";

            if ((key in history) && ("offerContent" in history[key]) && (Object.keys(history[key]["offerContent"]).length !== 0)) {
                setOfferContent(history[key]["offerContent"]);
                setWho("HUMAN");
                return;
            }

            // Agent Control
            key = i + "_AGENT";
            if ((key in history) && ("offerContent" in history[key])) {
                setOfferContent(history[key]["offerContent"]);
                setWho("AGENT");
                return;
            }
        }

        setOfferContent({});

    }, [history, round, isCompleted]);

    return (
        <div className={"col border rounded " + borderClass}>
            <div className="d-flex align-items-center justify-content-center text-center">
                <span className={className}>{value}</span>
            </div>
        </div>
    );
};


const IssueComponent = ({issueName, values}) => {
    return (
        <div className="row my-1 w-100">
            <div className="col-2 d-flex align-items-center justify-content-start text-center">
                <b>{issueName}</b>
            </div>
            <div className="col-10">
                <div className="row justify-content-between">
                    {values.length > 0 && values.map((value) => <ValueComponent value={value} issueName={issueName}
                                                                                key={issueName + value}/>)}
                </div>
            </div>
        </div>
    );
};


const PreferencesComponent = () => {
    const preferences = useSelector(state => state.session.preferences);

    return (
      <div className="row border border-2 rounded" style={{fontSize: "24px"}}>
          <div className="col m-1 h-100">
              {preferences["issues"].length > 0 && preferences["issues"].map((issueName) => <IssueComponent issueName={issueName} values={preferences["issue_values"][issueName]} key={issueName} />)}
          </div>
      </div>
    );
};

export default PreferencesComponent;
