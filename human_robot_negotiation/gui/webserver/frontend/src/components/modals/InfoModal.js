import React, {useEffect, useState} from "react";
import { Modal } from "react-bootstrap";

export const MODAL_INFO = "INFO_MODAL";

export const MODAL_SUCCESS = "SUCCESS_MODAL";

export const MODAL_WARNING = "WARNING_MODAL";

export const MODAL_ERROR = "ERROR_MODAL";


const InfoModal = ({modalType = MODAL_INFO, message = '', title = '', setModal = (val) => {}, openHandler = null, closeHandler = null, buttons = []}) => {
    const selfOpenHandler = () => {
        setModal(true);
    };

    const selfCloseHandler = () => {
        setModal(false);
    };

    const [realTitle, setRealTitle] = useState(title);
    const [headerColor, setHeaderColor] = useState("");
    const [msg, setMsg] = useState(message);

    const realOpenHandler = !openHandler ? selfOpenHandler : openHandler;
    const realCloseHandler = !closeHandler ? selfCloseHandler : closeHandler;

    useEffect(() => {
        switch (modalType) {
            case MODAL_INFO:
                setHeaderColor("bg-secondary");
                setRealTitle(title && title !== "" ? title : "Info");
                setMsg(message && message !== "" ? message : "");
                break;
            case MODAL_WARNING:
                setHeaderColor("bg-warning");
                setRealTitle(title && title !== "" ? title : "Warning");
                setMsg(message && message !== "" ? message : "A warning occurred during the process.");
                break;
            case MODAL_SUCCESS:
                setHeaderColor("bg-success");
                setRealTitle(title && title !== "" ? title : "Success");
                setMsg(message && message !== "" ? message : "The process successfully completed.");
                break;
            case MODAL_ERROR:
                setHeaderColor("bg-danger");
                setRealTitle(title && title !== "" ? title : "Error");
                setMsg(message && message !== "" ? message : "An error occurred during the process.");
                break;
            default:
                setHeaderColor("bg-light");
                setRealTitle(title && title !== "" ? title : "Modal");
                setMsg(message && message !== "" ? message : "");
                break;
        }
    }, [title, modalType, message]);

    return (
      <Modal show={realOpenHandler} onHide={realCloseHandler} onEscapeKeyDown={realCloseHandler}>
          <Modal.Header className={headerColor} closeButton>
              <Modal.Title>{realTitle}</Modal.Title>
          </Modal.Header>
          <Modal.Body className="bg-white">
              <p>
                  {msg}
              </p>
          </Modal.Body>
          <Modal.Footer>
              <div className="d-flex justify-content-end">
                  { buttons.length === 0 && <button className="btn btn-secondary" onClick={realCloseHandler}>Close</button> }
              </div>
          </Modal.Footer>
      </Modal>
    );
};

export default InfoModal;