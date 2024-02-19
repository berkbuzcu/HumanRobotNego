import {useEffect, useState} from "react";
import "./DragableList.css"


const ElicitationStep = ({preferences, index}) => {
    const [title, setTitle] = useState(index === 0 ? "Issues" : preferences["issues"][index - 1]);
    const [values, setValues] = useState(index === 0 ? [...preferences["issues"]] : [...preferences["issue_values"][preferences["issues"][index - 1]]]);

    useEffect(() => {
        if (index === 0) {
            setTitle("Issues");
            setValues([...preferences["issues"]]);
        } else {
            setTitle(preferences["issues"][index - 1]);
            setValues([...preferences["issue_values"][preferences["issues"][index - 1]]]);
        }

    }, [preferences, index]);

    const getItemClass = (index) => {
        if (index % 2 === 0) {
            return "list-group-item rounded border-1";
        } else {
            return "list-group-item rounded border-1 list-group-item-secondary";
        }
    };

    return (
        <ul className="list-group border-2 border-black w-100 shadow-sm">
            <li className="list-group-item rounded border-2 bg-secondary">{title}</li>
            {values.length > 0 && values.map((valueName, index) =>
                <li className={getItemClass(index)}>{valueName}</li>
            )};
        </ul>

    );
}

export default ElicitationStep;
