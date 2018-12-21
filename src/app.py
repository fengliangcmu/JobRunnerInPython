# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort, redirect, url_for, request
from flask import render_template
from flask import send_file
import json
import os
import sys
import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from importlib import import_module
import psutil
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
# don't need normal access logs
# more cases for logs: http://flask.pocoo.org/docs/dev/logging/ 
log.setLevel(logging.ERROR) 
# don't need normal access logs
# more cases for logs: http://flask.pocoo.org/docs/dev/logging/ 

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(APP_ROOT, 'jobs'))
my_scheduler = None

def getResultJson():
    res = {
        "hasError":False,
        "message":None,
        "result": None
    }
    return res
#ingore exception handling for now
def handleError(message):
    resObj = getResultJson()
    resObj['hasError'] = True
    resObj['message'] = message
    return resObj
#ingore exception handling for now
def handleSuccess(message, data):
    resObj = getResultJson()
    resObj['hasError'] = False
    resObj['message'] = message
    resObj['result'] = data
    return resObj

@app.route('/')
def root_page():
    return render_template('index.html')

@app.route('/index')
def index_page():
    return render_template('index.html')

@app.route('/home')
def home_page():
    return render_template('index.html')

# get sys information
@app.route('/job/getSysInfo', methods=['GET'])
def getSysInfo():
    cpu_pct = psutil.cpu_percent(interval=0.5)
    mem_info = psutil.virtual_memory()
    res = handleSuccess('',{"cpu_pct": str(cpu_pct) + '%', "mem_pct": str(mem_info.percent) + '%'})
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# start scheduler
@app.route('/job/startScheduler', methods=['GET'])
def startScheduler():
    global my_scheduler
    res = None
    if my_scheduler is None:
        my_scheduler = BackgroundScheduler()
        my_scheduler.start()
        res = handleSuccess('Scheduler is started!', None)
    else:
        #0 stopped,1 running,2 pasued
        if my_scheduler.state == 1:
            res = handleError('Scheduler is already running!')
        elif my_scheduler.state == 2:
            res = handleError('Scheduler is paused, please resume!')
        else:
            my_scheduler.start()
            res = handleSuccess('Scheduler is started!', None)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# stop scheduler
@app.route('/job/stopScheduler', methods=['GET'])
def stopScheduler():
    global my_scheduler
    res = None
    if my_scheduler is not None:
        my_scheduler.shutdown(wait=False)
        # pausedJobIds.clear()
        res = handleSuccess('Scheduler is stopped!', None)
    else:
        res = handleError('Scheduler instance is not found!')
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# get scheduler state info
@app.route('/job/getSchedulerStatus', methods=['GET'])
def getSchedulerStatus():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        #0 stopped,1 running,2 paused
        res = handleSuccess('', my_scheduler.state)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# Pausing scheduler
@app.route('/job/pauseScheduler', methods=['GET'])
def pauseScheduler():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        if my_scheduler.state == 1:
            my_scheduler.pause()
            res = handleSuccess('Scheduler is paused!', None)
        else:
            res = handleError('Scheduler is already stopped or paused!')
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# Resuming scheduler
@app.route('/job/resumeScheduler', methods=['GET'])
def resumeScheduler():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        if my_scheduler.state == 2:
            my_scheduler.resume()
            res = handleSuccess('Scheduler is resumed!',None)
        else:
            res = handleError('Scheduler is in not PAUSED state, nothing to resume!')
    return json.dumps(res), 200, {'ContentType':'application/json'} 


#payload should be including tag info
#{"jobId":"jobId1","crontab_exp":5,"pyFileName":"JobExampleClass","pyClassName":"JobExampleClass","pyMethodName":"printSomething","pyParameter":"'aaa','bbb'"}
@app.route('/job/addJob', methods=['POST'])
def addJob():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        if my_scheduler.state == 1:
            jobId = request.form['jobId']
            crontab_exp = request.form['crontab_exp']
            pyClassName = request.form['pyClassName'] 
            pyMethodName = request.form['pyMethodName']
            pyFileName = request.form['pyFileName']
            pyParameter = request.form['pyParameter']
            targetFolder = os.path.join(APP_ROOT, 'jobs')
            destination = "/".join([targetFolder, pyFileName])
            # sched.add_job(job_function, CronTrigger.from_crontab('0 0 1-15 may-aug *'))
            if os.path.isfile(destination):
                result = pyFileName.split ('.')
                module_local = import_module(result[0])
                eval_str = 'my_scheduler.add_job(module_local.'
                if pyClassName.strip():
                    eval_str = eval_str + pyClassName + '.' + pyMethodName
                else:
                    eval_str = eval_str + pyMethodName
                #eval_str = eval_str + ', \'interval\', seconds=' + str(crontab_exp) +', id=\'' + jobId + '\''
                eval_str = eval_str + ', CronTrigger.from_crontab(\'' + crontab_exp +'\'), id=\'' + jobId + '\''
                if pyParameter.strip():
                    eval_str = eval_str + ',args=['+ pyParameter.strip() + ']'
                eval_str = eval_str + ')'
                print(eval_str)
                eval(eval_str)
                #sched.add_job(my_job, args=['text'])
                res = handleSuccess('Job:'+ jobId +' is added and running!', None)
            else:
                res = handleError('Failed to find job file!')
        else:
            res = handleError('Scheduler is not running, no job is added!')

    return json.dumps(res), 200, {'ContentType':'application/json'} 

#payload should be including tag info
#{"jobId":"jobId1"}
@app.route('/job/removeJob', methods=['POST'])
def removeJob():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        data = request.get_data()
        json_re = json.loads(data)
        my_scheduler.remove_job(json_re['jobId'])
        res = handleSuccess('Job:'+ json_re['jobId'] +' is removed!', None)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# Pausing a job
#{"jobId":"jobId1"}
@app.route('/job/pauseJob', methods=['POST'])
def pauseJob():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        data = request.get_data()
        json_re = json.loads(data)
        my_scheduler.pause_job(json_re['jobId'])
        # pausedJobIds.append(json_re['jobId'])
        res = handleSuccess('Job:'+ json_re['jobId'] +' is paused!', None)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# Resume a job
#{"jobId":"jobId1"}
@app.route('/job/resumeJob', methods=['POST'])
def resumeJob():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        data = request.get_data()
        json_re = json.loads(data)
        my_scheduler.resume_job(json_re['jobId'])
        # pausedJobIds.pop(pausedJobIds.index(json_re['jobId']))
        res = handleSuccess('Job:'+ json_re['jobId'] +' is resumed!', None)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

# show all job info
@app.route('/job/showAllJobInfo', methods=['GET'])
def showAllJobInfo():
    global my_scheduler
    res = None
    if my_scheduler is None:
        res = handleError('No scheduler is running!')
    else:
        jobList = my_scheduler.get_jobs()
        tempRes = []
        if len(jobList) > 0:
            for x in jobList:
                if x is not None:
                    temp_time = ''
                    if x.next_run_time:
                        #temp_time = x.next_run_time.isoformat(' ', 'seconds')
                        temp_time = x.next_run_time.strftime('%Y/%m/%d/%H:%M:%S')
                    tempObj = {
                        "id":x.id,
                        "name":x.name,
                        "executor":x.executor,
                        "max_instances":x.max_instances,
                        "next_run_time":temp_time
                    }
                    tempRes.append(tempObj)
        res = handleSuccess('',tempRes)
    return json.dumps(res), 200, {'ContentType':'application/json'}

@app.route('/job/uploadJobFile', methods=['POST'])
def uploadJobFile():
    myFile = None
    targetFolder = os.path.join(APP_ROOT, 'jobs')
    destination = ''
    myFile = request.files['pythonFile']
    if not os.path.isdir(targetFolder):
        os.mkdir(targetFolder)
    destination = "/".join([targetFolder, myFile.filename])
    myFile.save(destination) 
    res = handleSuccess('file: ' + myFile.filename + ' is uploaded!', None)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

#{"filename":"aaaa.py"}
@app.route('/job/isFileExisting', methods=['POST'])
def isFileExisting():
    targetFolder = os.path.join(APP_ROOT, 'jobs')
    data = request.get_data()
    json_re = json.loads(data)
    destination = "/".join([targetFolder, json_re['filename']])
    res = None
    if os.path.isfile(destination):
        res = handleSuccess('', True)
    else:
        res = handleSuccess('', False)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

#{"filename":"aaaa.py"}
@app.route('/job/removeFile', methods=['POST'])
def removeFile():
    targetFolder = os.path.join(APP_ROOT, 'jobs')
    data = request.get_data()
    json_re = json.loads(data)
    destination = "/".join([targetFolder, json_re['filename']])
    res = None
    if os.path.isfile(destination):
        os.remove(destination)
        res = handleSuccess('File deleted!', None)
    else:
        res = handleSuccess('File does not exist!', None)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.route('/job/getAllJobFiles', methods=['GET'])
def getAllJobFiles():
    filelist = []
    mypath = os.path.join(APP_ROOT, 'jobs')
    for file in os.listdir(mypath):
        if file.endswith(".py"):
            filelist.append(file)
    # onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
    res = handleSuccess('', filelist)
    return json.dumps(res), 200, {'ContentType':'application/json'} 

@app.errorhandler(Exception)
def handle_error(e):
    res = handleError(str(e))
    return json.dumps(res), 200, {'ContentType':'application/json'}
    # return render_template("500.html", error = str(e))

if __name__ == '__main__':
    #app.run()
    # app.jinja_env.auto_reload = True
    # app.config['TEMPLATES_AUTO_RELOAD'] = True
    # app.run(debug=True, host='0.0.0.0',port=8888)
    app.run(host='0.0.0.0',port=8888)