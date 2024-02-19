import {useSelector} from "react-redux";
import {useEffect, useState} from "react";
import MessageComponent from "./MessageComponent";


const HistoryComponent = () => {
    const status = useSelector(state => state.session.status);

    const [order, setOrder] = useState([]);

    useEffect(() => {
        switch (status) {
            case "AGENT_LISTENING":
                setOrder(["HUMAN", "AGENT"]);
                break;
            case "AGENT_SPEAKING":
                setOrder(["AGENT", "HUMAN"]);
                break;
            default:
                setOrder([]);
                break;
        }
    }, [status]);

    return (
        <>
            {order.length > 0 && order.map((key, index) => (
                <MessageComponent who={key} key={"MessageComponent_" + key} />
            ))}
        </>
    );
};


export default HistoryComponent;
