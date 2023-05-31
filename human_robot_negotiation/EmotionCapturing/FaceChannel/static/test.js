function load() {
    sessionStorage.clear();

    changeStep("");
}

function changeStep(step) {
    return;

    /*
    $(".btn").attr("disabled", "disabled");
    $("#cameraID").attr("disabled", "disabled");
    $("#experimentID").attr("disabled", "disabled");

    sessionStorage.setItem("step", step);

    if (step === "") {
        $("#joinBtn").removeAttr("disabled");
        $("#cameraID").removeAttr("disabled");
        $("#experimentID").removeAttr("disabled");
    } else if (step === "session1") {
        $("#startBtn").removeAttr("disabled");
        $("#nextBtn").removeAttr("disabled");
    } else if (step === "recording1" || step === "recording2") {
        $("#stopBtn").removeAttr("disabled");
    } else if (step === "session2") {
        $("#startBtn").removeAttr("disabled");
        $("#exitBtn").removeAttr("disabled");
    }
     */
}

function updateStatus(status) {
    sessionStorage.setItem("status", status);

    $("#status").html("" + status);
    if (status === "")
        $("#status").html("Waiting...");

    if (status === false) {
        $("#status").removeClass("text-success");
        $("#status").removeClass("text-warning");
        $("#status").addClass("text-danger");

        changeStep("");
    } else if (status === "") {
        $("#status").removeClass("text-success");
        $("#status").removeClass("text-danger");
        $("#status").addClass("text-warning");

        // $(".btn").attr("disabled", "disabled");
        $("#cameraID").attr("disabled", "disabled");
        $("#experimentID").attr("disabled", "disabled");
        $("#sessionID").attr("disabled", "disabled");
        $("#module").attr("disabled", "disabled");
    } else {
        $("#status").removeClass("text-danger");
        $("#status").removeClass("text-warning");
        $("#status").addClass("text-success");

        changeStep(sessionStorage.getItem("step"));
    }

}

function join() {
    const experimentID = $("#experimentID").val();
    const sessionID = $("#sessionID").val();
    const cameraID = $("#cameraID").val();
    const moduleName = $("#module").val();

    const sessionName = experimentID + "_" + sessionID;

    const request = {"session_name": sessionName, "module_name": moduleName};

    updateStatus("");

    Webcam.set({
            width: 320,
            height: 240,
            image_format: 'jpeg',
            jpeg_quality: 90
        });
    Webcam.attach('#webcam');

    $.ajax({
        type: "POST",
        url: "join",
        data: JSON.stringify(request),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data["status"]) {
                sessionStorage.setItem("session_name", sessionName);
                sessionStorage.setItem("camera_id", cameraID);
            }
            updateStatus(data["status"]);
        }, fail: function () {
            updateStatus(false);
        }, error: function () {
            updateStatus(false);
        }
    });
}

function cap() {
    const session_name = sessionStorage.getItem("session_name");

    Webcam.snap(function (data_uri) {
        $("#imgCapture")[0].src = data_uri;
    });

    updateStatus("");

    $.ajax({
        type: "POST",
        url: "feed/" + session_name + "/",
        data: $("#imgCapture")[0].src,
        processData: false,
        contentType: false,
        cache: false,
        success: function (data) {
            if (data["status"])
                sessionStorage.setItem("step",
                    sessionStorage.getItem("step") === "session1" ? "recording1" : "recording2");

            updateStatus(data["status"]);
        }, fail: function () {
            updateStatus(false);
        }, error: function () {
            updateStatus(false);
        }
    });
}

function predict() {
    const session_name = sessionStorage.getItem("session_name");

    const request = {"session_name": session_name};

    updateStatus("");

    $.ajax({
        type: "POST",
        url: "predict",
        data: JSON.stringify(request),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data["status"])
                sessionStorage.setItem("step",
                    sessionStorage.getItem("step") === "recording1" ? "session1" : "session2");

            $("#arousalOut").html("" + data["prediction"]["Arousal"]);
            $("#valanceOut").html("" + data["prediction"]["Valance"]);

            updateStatus(data["status"]);
        }, fail: function () {
            updateStatus(false);
        }, error: function () {
            updateStatus(false);
        }
    });
}

function exit() {
    const session_name = sessionStorage.getItem("session_name");

    const request = {"session_name": session_name};

    updateStatus("");

    $.ajax({
        type: "POST",
        url: "exit",
        data: JSON.stringify(request),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data["status"]) {
                sessionStorage.setItem("step", "");
                $("#cameraID").removeAttr("disabled");
                $("#experimentID").removeAttr("disabled");
                $("#sessionID").removeAttr("disabled");
                $("#module").removeAttr("disabled");
            }

            updateStatus(data["status"]);
        }, fail: function () {
            updateStatus(false);
        }, error: function () {
            updateStatus(false);
        }
    });
}