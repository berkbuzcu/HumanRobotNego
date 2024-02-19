import {useSelector} from "react-redux";
import {useEffect, useState} from "react";



const twoDecimal = (v) => {
  let twoDecimalStr = "" + v;

  while (twoDecimalStr.length < 2) {
     twoDecimalStr = "0" + twoDecimalStr;
  }

  return twoDecimalStr;
};


const NegotiationInfoComponent = () => {
    const status = useSelector(state => state.session.status);
    const seconds = useSelector(state => state.session.seconds);
    const minutes = useSelector(state => state.session.minutes);

    const history = useSelector(state => state.history.history);
    const round = useSelector(state => state.session.round);
    const [utility, setUtility] = useState(0);

    const [statusText, setStatusText] = useState();

    useEffect(() => {
        switch (status) {
            case "AGENT_LISTENING":
                setStatusText("Agent Listening");
                break;
            case "AGENT_SPEAKING":
                setStatusText("Agent Speaking");
                break;
            default:
                setStatusText("");
                break;
        }
    }, [status]);


    useEffect(() => {
        for (let i = round; i >= 0; --i) {
            // Human Control
            let key = i + "_HUMAN";

            if ((key in history) && ("utility" in history[key]) && ("offerContent" in history[key]) && (Object.keys(history[key]["offerContent"]).length !== 0)) {
                setUtility(history[key]["utility"]);
                return;
            }

            // Agent Control
            key = i + "_AGENT";
            if ((key in history) && ("utility" in history[key])) {
                setUtility(history[key]["utility"]);
                return;
            }
        }

        setUtility(0);

    }, [round, history]);

    return (
        <div className="row border border-2 rounded" style={{height: "10vh"}}>
            <div className="col-3 border border-1 text-center d-flex align-items-center justify-content-center">
                <span><h3>Time: <b>{twoDecimal(minutes) + ":" + twoDecimal(seconds)}</b></h3></span>
            </div>
            <div className="col-6 border border-1 text-center d-flex align-items-center justify-content-center">
                <span><h3><b>{statusText}</b></h3></span>
            </div>
            <div className="col-3 border border-1 text-center d-flex align-items-center justify-content-center">
                <span><h3>Your utility: <b>{utility}</b></h3></span>
            </div>
        </div>
    );

};


export default NegotiationInfoComponent;
