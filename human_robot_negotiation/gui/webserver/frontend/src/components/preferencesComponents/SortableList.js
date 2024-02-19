import "./DragableList.css"
import {DragDropContext, Draggable, Droppable} from "react-beautiful-dnd";
const SortableList = ({issueName, values, disabled, setValues}) => {
    const onDragEndValue = (result) => {
        if (!disabled && result.destination) {
            let newList = [...values];
            newList.splice(result.source.index, 1);
            newList.splice(result.destination.index, 0, values[result.source.index]);

            setValues(issueName, newList);
        }
    };

    const getClass = (index) => {
        if (index % 2 === 0) {
            return "list-group-item rounded border-1";
        } else {
            return "list-group-item rounded border-1 list-group-item-secondary";
        }
    };

    return (
        <>
            <DragDropContext
                onDragEnd={onDragEndValue}>

                <Droppable droppableId={"droppable_" + issueName} key={"droppable_" + issueName} type={issueName}>
                    {(provided, snapshot) => (
                        <ul className="list-group border-2 border-black w-100 shadow-sm" {...provided.droppableProps} ref={provided.innerRef}>
                            <li className="list-group-item rounded border-2 bg-secondary"><b>{issueName}</b></li>
                            {values.length > 0 && values.map((key, index) => (
                                <Draggable key={issueName + "_" + key} draggableId={issueName + "_" + key} index={index} isDragDisabled={disabled} type={issueName}>
                                    {(provided, snapshot) => (
                                        <li className={getClass(index)} ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            style={{...provided.draggableProps.style}}>{key}</li>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </ul>
                    )}
                </Droppable>
            </DragDropContext>

        </>
    );
};

export default SortableList;
