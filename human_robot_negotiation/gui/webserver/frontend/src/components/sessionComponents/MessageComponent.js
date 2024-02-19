import {useSelector} from "react-redux";
import {useEffect, useState} from "react";
import "./Session.css"


const MessageComponent = ({who}) => {
    const history = useSelector(state => state.history.history);
    const round = useSelector(state => state.session.round);
    const [message, setMessage] = useState("");

    const [whoClass, setWhoClass] = useState("");
    const [whoBgClass, setWhoBgClass] = useState("");

    useEffect(() => {
        for (let i = round; i >= 0; --i) {
            const key = i + "_" + who;

            if ((key in history) && ("message" in history[key]) && history[key]["message"] !== '') {
                setMessage(history[key]["message"]);
                return;
            }
        }

        setMessage("");

    }, [who, history, round]);


    useEffect(() => {
        if (who === 'AGENT') {
            setWhoBgClass("message-agent border border-2 rounded-3 shadow");
            setWhoClass("d-flex justify-content-center align-items-start text-start");
        } else {
            setWhoBgClass("message-human border border-2 rounded-3 shadow");
            setWhoClass("d-flex justify-content-center align-items-end text-end");
        }

    }, [who]);

    return (
        <>
            {message !== '' &&
                <div className={"row border border-1 " + whoClass}>
                    {who === 'HUMAN' && <div className="col-3"></div>}
                    <div className={"col-5 " + whoBgClass}>
                        <div className={"row my-2"}>
                            <p className="text-wrap">{message}</p>
                        </div>
                    </div>
                    {who === 'AGENT' && <div className="col-3"></div>}
                </div>
            }
        </>
    );
};

export default MessageComponent;
