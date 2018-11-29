var tr_str_a = '<tr>';
var tr_str_z = '</tr>';
var td_str_a = '<td>';
var td_str_z = '</td>';
var th_str_a = '<th scope="row">';
var th_str_z = '</th>';
var btn_str_s_a = '<button type="button" class="btn btn-success btn-xs" onclick="jobBtnOnclick(\'';
var btn_str_w_a = '<button type="button" class="btn btn-warning btn-xs" onclick="jobBtnOnclick(\'';
var btn_str_d_a = '<button type="button" class="btn btn-danger btn-xs" onclick="jobBtnOnclick(\'';
var btn_str_removefile_a = '<button type="button" class="btn btn-danger btn-xs" onclick="removeFileOnclick(\'';
var btn_str_removefile_z = '\')">remove</button>';
var btn_str_resumePausedJob_a = '<button type="button" class="btn btn-success btn-xs" onclick="resumePausedJobOnclick(\'';
var btn_str_resumePausedJob_z = '\')">resume</button>';
var btn_str_s_z = '\', \'resume\')">Resume</button>';
var btn_str_w_z = '\', \'pause\')">Pause</button>';
var btn_str_d_z = '\', \'remove\')">Remove</button>';


function getCurrentTime(){
    var currentdate = new Date(); 
    var datetime = "[ " + currentdate.getFullYear() + "/"
                + (currentdate.getMonth()+1)  + "/" 
                + currentdate.getDate() + " @ "  
                + currentdate.getHours() + ":"  
                + currentdate.getMinutes() + ":" 
                + currentdate.getSeconds() + " ]: ";
    return datetime;
}

function updateServerMessage(data) {
    res = JSON.parse(data);
    if (res.hasError === true) {
        $("#server_message").append("<small class='server-response-error'>" + "<b>" + getCurrentTime() + "</b>" + res.message + "</small>");
    }
    else {
        $("#server_message").append("<small class='server-response-info'>" + "<b>" + getCurrentTime() + "</b>" + res.message + "</small>");
    }
    stopSpinner();
}
function updateServerException(data) {
    $("#server_message").append("<small class='server-response-error'>" + getCurrentTime() + data + "</small>");
    stopSpinner();
}


function startSpinner() {
    $("#spinner").addClass("is-active");
}
function stopSpinner() {
    setTimeout(function () { $("#spinner").removeClass("is-active"); }, 1000);
}

function bindFormSubmit() {
    $("#addJobBtn").click(function () {
        // var form = $('form')[0];
        if ((!$("#jobId").val()) || (!$("#interval_sec").val()) || (!$("#pyMethodName").val()) || (!$("#pyFileName").val())) {
            updateServerException('You must input jobId, interval_sec, pyMethodName, pyFileName');
            return false;
        }
        startSpinner();
        var formdata = new FormData();
        formdata.append("jobId", $("#jobId").val());
        formdata.append("interval_sec", $("#interval_sec").val());
        formdata.append("pyMethodName", $("#pyMethodName").val());
        formdata.append("pyClassName", $("#pyClassName").val());
        formdata.append("pyFileName", $("#pyFileName").val());
        formdata.append("pyParameter", $("#pyParameter").val());

        $.ajax({
            url: "/job/addJob",
            type: "POST",
            data: formdata,
            cache: false,
            processData: false,
            contentType: false
        }).done(function (data) {
            updateServerMessage(data);
        })
            .fail(function (jqxhr, textStatus, error) {
                updateServerException(textStatus + " " + error);
            })
    });
}

function bindFileSubmit() {
    $("#submitFileBtn").click(function () {
        // var form = $('form')[0];
        if (!($("#pythonFile")[0].files[0])) {
            alert('No file to upload!')
            return false;
        }
        startSpinner();
        var formdata = new FormData();
        var tmpfile = $("#pythonFile")[0].files[0];
        if (tmpfile) {
            formdata.append("pythonFile", tmpfile);
        }

        $.ajax({
            url: "/job/uploadJobFile",
            type: "POST",
            data: formdata,
            cache: false,
            processData: false,
            contentType: false
        }).done(function (data) {
            updateServerMessage(data);
            stopSpinner();
        })
            .fail(function (jqxhr, textStatus, error) {
                updateServerException(textStatus + " " + error);
                stopSpinner();
            })
    });
}

function bindInfoPanelTutorTab(){
    
    $("#info_panel_tutorial_tab").click(function () {
        $("#info_panel_tutorial_tab").addClass("info-panel-title-brick-active")
        $("#info_panel_apis_tab").removeClass("info-panel-title-brick-active")
        $("#info_panel_tutorial").show();
        $("#info_panel_apis").hide();
    })
}

function bindInfoPanelAPIsTab(){
    $("#info_panel_apis_tab").click(function () {
        $("#info_panel_tutorial_tab").removeClass("info-panel-title-brick-active")
        $("#info_panel_apis_tab").addClass("info-panel-title-brick-active")
        $("#info_panel_tutorial").hide();
        $("#info_panel_apis").show();
    })
}

function bindClearServerMessage(){
    $("#clearServerMessage").click(function () {
        $("#server_message").html("");
    })
}

function bindSchedulerBtn(btnName) {
    var btn_id = '#scheduler_btn_' + btnName;
    var url = 'job/' + btnName + 'Scheduler';
    $(btn_id).click(function () {
        startSpinner()
        var settings = {
            "async": true,
            "crossDomain": true,
            "url": url,
            "method": "GET",
            "headers": {
                "content-type": "application/json",
                "cache-control": "no-cache",
            },
            "processData": false
        }
        $.ajax(settings)
            .done(function (data) {
                updateServerMessage(data);
            })
            .fail(function (jqxhr, textStatus, error) {
                updateServerException(textStatus + " " + error);
            })
    });
}

function jobBtnOnclick(jobId, btnName) {
    //resume/pause/remove
    startSpinner();
    var url = 'job/' + btnName + 'Job';

    var settings = {
        "async": true,
        "crossDomain": true,
        "url": url,
        "method": "POST",
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-cache",
        },
        "processData": false,
        "data": "{\"jobId\":\"" + jobId + "\"}"
    }

    $.ajax(settings)
        .done(function (data) {
            updateServerMessage(data);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
        })
}

function removeFileOnclick(filename) {
    startSpinner();
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": 'job/removeFile',
        "method": "POST",
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-cache",
        },
        "processData": false,
        "data": "{\"filename\":\"" + filename + "\"}"
    }
    $.ajax(settings)
        .done(function (data) {
            updateServerMessage(data);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
        })
}

function resumePausedJobOnclick(jobId) {
    startSpinner();
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": 'job/resumeJob',
        "method": "POST",
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-cache",
        },
        "processData": false,
        "data": "{\"jobId\":\"" + jobId + "\"}"
    }
    $.ajax(settings)
        .done(function (data) {
            updateServerMessage(data);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
        })
}

function getAllJobs() {
    $.getJSON('job/showAllJobInfo')
        .done(function (data) {
            var htmlstr = "";
            if (data.result) {
                data.result.forEach(function (item, idx) {
                    var rowStr = tr_str_a + th_str_a + item.id + th_str_z +
                        td_str_a + item.name + td_str_z +
                        td_str_a + item.executor + td_str_z +
                        td_str_a + item.max_instances + td_str_z +
                        td_str_a + item.next_run_time + td_str_z +
                        td_str_a + 
                        // btn_str_s_a + item.id + btn_str_s_z +
                        // btn_str_w_a + item.id + btn_str_w_z +
                        (item.next_run_time === ''? btn_str_s_a + item.id + btn_str_s_z : btn_str_w_a + item.id + btn_str_w_z) + 
                        btn_str_d_a + item.id + btn_str_d_z +
                        td_str_z + tr_str_z;
                    htmlstr = htmlstr + rowStr;
                });
            }
            $("#jobTableTbody").html(htmlstr);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
            $("#jobTableTbody").html('');
        });

}
function getAllJobFiles() {
    $.getJSON('job/getAllJobFiles')
        .done(function (data) {
            var htmlstr = "";
            if (data.result) {
                data.result.forEach(function (item, idx) {
                    var rowStr = tr_str_a + td_str_a + item + td_str_z +
                        td_str_a + btn_str_removefile_a + item + btn_str_removefile_z + td_str_z + tr_str_z
                    htmlstr = htmlstr + rowStr;
                });
            }
            $("#fileTableTbody").html(htmlstr);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
            $("#fileTableTbody").html('');
        });
}

function bindFileLoadBtn() {
    $("#pythonFile").on("change", function (e) {
        $("#uploadFileText").val(e.target.files[0].name);
    });
}

$(function () {
    //button actions for scheduler
    bindSchedulerBtn('start');
    bindSchedulerBtn('stop');
    bindSchedulerBtn('resume');
    bindSchedulerBtn('pause');

    //button actions for adding a job to scheduler
    bindFormSubmit();

    bindFileLoadBtn();
    bindFileSubmit();
    bindClearServerMessage();

    bindInfoPanelAPIsTab()
    bindInfoPanelTutorTab()

    setInterval(function () {
        getSchedulerStatus();
        getCPUandMemStatus();
        getAllJobs();
        getAllJobFiles();
        // getPausedJobIds();
    }, 3000);
});

function getSchedulerStatus() {
    $.getJSON("job/getSchedulerStatus")
        .done(function (data) {
            var htmlString = "Scheduler Status: <span class='text-info'>Unknown</span>";
            if (data) {
                switch (data.result) {
                    case 0:
                        htmlString = "Scheduler Status: <span class='text-danger'>Stopped</span>";
                        break;
                    case 1:
                        htmlString = "Scheduler Status: <span class='text-success'>Running</span>";
                        break;
                    case 2:
                        htmlString = "Scheduler Status: <span class='text-warning'>Paused</span>";
                        break;
                    default:
                        htmlString = "Scheduler Status: <span class='text-info'>Unknown</span>";
                }
            }
            $("#schedulerStatus").html(htmlString);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
        });
};

function getCPUandMemStatus() {
    $.getJSON("job/getSysInfo")
        .done(function (data) {
            var cpu_info = '0%';
            var mem_info = '0%';
            if (data) {
                if (data.result) {
                    cpu_info = data.result.cpu_pct;
                    mem_info = data.result.mem_pct;
                }
            }
            $("#cpu_info").text('CPU: ' + cpu_info);
            $("#mem_info").text('Memory: ' + mem_info);
        })
        .fail(function (jqxhr, textStatus, error) {
            updateServerException(textStatus + " " + error);
        });
};