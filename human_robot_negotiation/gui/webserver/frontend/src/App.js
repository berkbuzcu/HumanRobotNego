import {useState} from "react";
import ConfigPage from "./components/ConfigPage";
import SessionPage from "./components/SessionPage";
import PreferencesPage from "./components/PreferencesPage";
import ReviewPage from "./components/ReviewPage";

function App() {
    const [page, setPage] = useState("CONFIG");
    const [uuid, setUUID] = useState("");

    return (
        <div className="container-fluid p-3 bg-dark vw-100 vh-100">
            <div className="bg-light p-1 m-1 w-100 h-100">
                {page === 'CONFIG' && <ConfigPage setUUID={setUUID} setPage={setPage} />}
                {page === 'PREFERENCES' && <PreferencesPage uuid={uuid} setPage={setPage} /> }
                {page === 'REVIEW' && <ReviewPage uuid={uuid} setPage={setPage} /> }
                {page === 'SESSION' && <SessionPage uuid={uuid} setPage={setPage} />}
            </div>
        </div>
    );
}

export default App;
