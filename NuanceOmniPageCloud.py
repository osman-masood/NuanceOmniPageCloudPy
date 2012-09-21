# -*- coding: utf-8 -*-

import requests
import time
from BeautifulSoup import BeautifulStoneSoup  # beautifulsoup3
import urllib
import os
import datetime
import re

### NOTICE FOR OS X USERS ###
# pycurl uses command-line tools (from the LLVM package) that must be installed manually via Xcode.
# Starting with Xcode 4.3 - you must now manually install command line tools from Xcode menu > Preferences > Downloads.
# See http://stackoverflow.com/questions/9353444/how-to-use-install-gcc-on-mac-os-x-10-8-xcode-4-4
import pycurl

# The job is created but not started, typically wait for the upload of the input file.
JOB_STATE_CREATED = "Created"
# The job is waiting to be processed by a Conversion Client.
JOB_STATE_STARTED = "Started"
# The job is being processed in a Conversion Client.
JOB_STATE_RUNNING = "Running"
# The job is succesfully done, the content is converted.
JOB_STATE_COMPLETED = "Completed"
# The job has failed completely, the adapter suitable for the conversion type was not able to convert the content.
JOB_STATE_FAILED = "Failed"
# The job was cancelled by the user.
JOB_STATE_CANCELLED = "Cancelled"
# The job was abandoned by the user.
JOB_STATE_ABANDONED = "Abandoned"

JOB_PRIORITY_LOW = 0
JOB_PRIORITY_MEDIUM = 1
JOB_PRIORITY_HIGH = 2

class NuanceOmniPageCloud():
    def __init__(self, account_name, account_key):
        self._account_name = account_name
        self._account_key = account_key
        # identity provider settings
        self._sts_url = "nuance-sts.nuancecomputing.com"
        self._username = self._account_name
        self._password = self._account_key

        # DCS settings
        self._service_host = "dcs-ncus-ctp.nuancecomputing.com"
        self._service_port = "443"
        self._service_base = "ConversionService.svc/pox"

        self._get_job_types_uri = "GetJobTypes"
        self._create_job_uri = "CreateJob"
        self._get_upload_urls_uri = "GetUploadUrls"
        self._start_job_uri = "StartJob"
        self._cancel_job_uri = "CancelJob"
        self._get_job_info_uri = "GetJobInfo"
        self._get_download_urls_uri = "GetDownloadUrls"

        self._token_string = None

        self._def_namespace = "http://tempuri.org/"
        self._dcs_namespace = "http://schemas.datacontract.org/2004/07/Nuance.DCS.ConversionServiceMeta"
        self._arr_namespace = "http://schemas.microsoft.com/2003/10/Serialization/Arrays"

        self._auth_header = "WRAP access_token"

        self._http_header = None
        self._token_string = None

    def convert(self, input_file_path, output_file_path, job_type_id, title="", description="NuanceOmniPageCloud Python"):
        # $conversionServiceBase = "https://".RestTestClient::ServiceHost."/".RestTestClient::ServiceBase;

        conversion_service_base = "https://%s/%s" % (self._service_host, self._service_base)

        # getting security token
        token = self._contact_ac_for_token_using_wrap(self._sts_url, self._username, self._password, conversion_service_base)
        self._token_string = token
        # $this->httpHeader = array("Authorization: ". self::$auth_header. "=\"". $this->mTokenString. "\"");
        # self._http_header = 'Authorization: %s="%s"' % (self._auth_header, self._token_string)
        self._http_header = {'Authorization': '%s="%s"' % (self._auth_header, self._token_string)}

        # get supported conversion types
        job_types = self._get_job_types()

        # create a sample job
        job_id = self._create_job(job_type_id, title, description, "conversion of %s" % input_file_path)

        # get urls where files are uploaded
        upload_urls = self._get_upload_urls(job_id, 1)

        # upload file to the given destination
        url = upload_urls[0]
        file = input_file_path
        self._upload_file(file, url)

        # start job
        job_info = self._start_job(job_id, "PT0M", JOB_PRIORITY_HIGH, None)

        # monitor job progress
        print "starting job progress monitoring"
        while True:
            job_info = self._get_job_info(job_id)
            poll_interval_seconds = job_info.poll_interval.total_seconds()
            if job_info.state == JOB_STATE_COMPLETED:
                print "job is completed!"
                # get the urls of the result files
                download_urls = self._get_download_urls(job_id)
                print "DownloadUrl: %s" % download_urls[0]
                self._download_file(output_file_path, download_urls[0])
                break
            elif job_info.state == JOB_STATE_FAILED:
                print "Conversion is failed\nresult code: %s,\nresult message %s" % (job_info.result_code, job_info.result_message)
                break
            else:
                print "waiting for %s seconds..." % poll_interval_seconds
                time.sleep(poll_interval_seconds)

        print "finishing job progress monitoring"

    def _create_job(self, job_type_id, title, description, metadata):
        print "creating job"
        params = dict(jobTypeId=job_type_id, title=title, description=description, metadata=metadata)
        create_job_result = requests.get(
            "https://%s/%s/%s" % (self._service_host, self._service_base, self._create_job_uri),
            params=params,
            headers=self._http_header
        ).text
        job_id = BeautifulStoneSoup(create_job_result).find('createjobresult').text
        print "creating job finished with job_id %s" % job_id
        return job_id

    def _get_job_types(self):
        print "getting job types"
        get_job_types_result = requests.get(
            "https://%s/%s/%s" % (self._service_host, self._service_base, self._get_job_types_uri),
            headers=self._http_header
        ).text
        document = BeautifulStoneSoup(get_job_types_result)
        supported_job_types = []
        for job_type_tag in document.findAll('jobtype'):
            job_type = JobType()
            job_type.source_format = job_type_tag.find('sourceformat').text
            job_type.target_format = job_type_tag.find('targetformat').text
            job_type.job_type_id = job_type_tag.find('jobtypeid').text
            job_type.description = job_type_tag.find('description').text
            supported_job_types.append(job_type)
        print "returning jobtypes"
        return supported_job_types

    def _get_upload_urls(self, job_id, count):
        print "getting upload urls"
        params = dict(jobId=job_id, count=count)
        get_upload_urls_result = requests.get(
            "https://%s/%s/%s" % (self._service_host, self._service_base, self._get_upload_urls_uri),
            params=params,
            headers=self._http_header
        ).text
        print "getting upload urls done"
        return [string_tag.text for string_tag in BeautifulStoneSoup(get_upload_urls_result).findAll('a:string')]

    def _upload_file(self, file_path, url):
        print "upload the input file %s" % file_path

        try:
            with open(file_path, 'rb') as f: # check to see if file exists
                size = os.stat(file_path).st_size
                c = pycurl.Curl()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.PUT, 1)
                c.setopt(pycurl.INFILE, f)
                c.setopt(pycurl.INFILESIZE, size)
                post_result = c.perform()
                c.close()
                print "upload finished"
                return True
        except IOError as e:
            return False
        return False

    def _start_job(self, job_id, time_to_live, priority, conversion_parameters):
        print "starting job"
        params = dict(jobId=job_id, timeToLive=time_to_live, priority=priority, conversionParameters=conversion_parameters)
        start_job_result = requests.get(
            "https://%s/%s/%s" % (self._service_host, self._service_base, self._start_job_uri),
            params=params,
            headers=self._http_header
        ).text
        # Although PHP sample code loops through all startjobresult tags, we only get the first one, only need to return one anyway
        tag = BeautifulStoneSoup(start_job_result).find('startjobresult')
        print "starting job done"
        return JobInfo(soup_tag = tag)

    def _get_job_info(self, job_id):
        print "getting job info"
        get_job_info_result = requests.get(
            "https://%s/%s/%s" % (self._service_host, self._service_base, self._get_job_info_uri),
            params = dict(jobId=job_id),
            headers = self._http_header
        ).text
        tag = BeautifulStoneSoup(get_job_info_result).find('getjobinforesult')
        print "getting job info done"
        return JobInfo(soup_tag = tag)

    def _get_download_urls(self, job_id):
        params = dict(jobId = job_id)
        get_download_urls_result = requests.get(
            "https://%s/%s/%s" % (self._service_host, self._service_base, self._get_download_urls_uri),
            params=params,
            headers=self._http_header
        ).text
        print "get download urls result %s" % get_download_urls_result
        return []

    def _download_file(self, file_path, url):
        print "download the output file %s" % file_path
        if not url:
            print "invalid url"
            return False
        try:
            with open(file_path, 'wb') as f:
                c = pycurl.Curl()
                c.setopt(pycurl.URL, url)
                c.setopt(pycurl.TIMEOUT, 50)
                c.setopt(pycurl.FILE, f)
                c.setopt(pycurl.FOLLOWLOCATION, True)
                post_result = c.perform()
                c.close()
                print "download finished"
                return True
        except IOError as e:
            return False
        return False


    def _contact_ac_for_token_using_wrap(self, sts_url, username, password, conversion_service_base):
        # sending authorization request to sts
        # note: post params have to be sent as query string (not as an array). This way the request content type will be application/x-www-form-urlencoded.
        response = requests.post(
            "https://%s/%s" % (sts_url, "issue/wrap/WRAPv0.9"),
            data=dict(wrap_name=username, wrap_password=password, wrap_scope=conversion_service_base)
        ).text

        # split response string into array of values
        response_array = response.split('&')
        wrap_access_token_array = response_array[0].split('=')
        wrap_access_token = urllib.unquote(wrap_access_token_array[1])

        # returning security token
        return wrap_access_token

class JobInfo():
    def __init__(self, job_id=None, completeness=None, state=None, estimated_work_time=None, poll_interval=None,
                 started=None, ended=None, job_type_id=None, result_code=None, result_message=None,
                 metadata=None, job_priority=None, soup_tag=None):
        if soup_tag:
            self.job_id = soup_tag.find('jobid').text,
            self.state = soup_tag.find('state').text,
            self.completeness = soup_tag.find('completeness').text,
            self.estimated_work_time = soup_tag.find('estimatedworktime').text,
            self.poll_interval = self._serialized_timespan_to_timedelta(soup_tag.find('pollinterval').text),
            self.started = soup_tag.find('started').text,
            self.ended = soup_tag.find('ended').text,
            self.job_type_id = soup_tag.find('jobtypeid').text,
            self.result_code = soup_tag.find('resultcode').text,
            self.result_message = soup_tag.find('resultmessage').text,
            self.metadata = soup_tag.find('metadata').text,
            self.job_priority = soup_tag.find('jobpriority').text
        else:
            self.job_id = job_id # The identifier of the job.
            self.completeness = completeness # Percentage of the job progress. It has meaning only if the State is Running.
            self.state = state # The current state of the job.
            self.estimated_work_time = estimated_work_time  # Estimated duration until the work is done.
            self.poll_interval = self._serialized_timespan_to_timedelta(poll_interval)  # Estimated time span while the JobType won't be changed. Don't get progress information within this time interval.
            self.started = started #  Start date of the job.
            self.ended = ended # End date of the job.
            self.job_type_id = job_type_id # The id of the conversion type.
            self.result_code = result_code # Result code of the processing.
            self.result_message = result_message # Result message of the processing.
            self.metadata = metadata
            self.job_priority = job_priority
        print "end of init: pollinterval=%s" % self.poll_interval
        print isinstance(self.poll_interval, tuple)
        self.poll_interval = self.poll_interval[0]

    # Have to implement this due to Nuance's horribly serialized time string...i'm sorry, but really, what were they thinking
    def _serialized_timespan_to_timedelta(self, timespan):
        print "timespan at start of conversion: %s" % timespan
        years, months, days, hours, minutes, seconds = 0, 0, 0, 0, 0, 0
        result = re.search(r"([0-9.]*)Y", timespan) # years
        if result: years = float(result.group(1))
        result = re.search(r"^[^T]*?([0-9.]*)M", timespan) # months
        if result: months = float(result.group(1))
        result = re.search(r"([0-9.]*)D", timespan) # days
        if result: days = float(result.group(1))
        result = re.search(r"([0-9.]*)H", timespan)  # hours
        if result: hours = float(result.group(1))
        result = re.search(r"T.*?([0-9.]*)M", timespan)  # minutes
        if result: minutes = float(result.group(1))
        result = re.search(r"([0-9.]*)S", timespan)  # seconds
        if result: seconds = float(result.group(1))
#        seconds = float(seconds + 60 * minutes + 3600 * hours + 3600 * 24 * days + 30 * 3600 * 24 * months + 365 * 3600 * 24 * years)
#        print "value of seconds at end of conversion %s" % seconds
#        return seconds
        return datetime.timedelta(
            days = days + 30 * months + 365 * years,
            hours = hours,
            minutes = minutes,
            seconds = seconds
        )

class JobType():
    def __init__(self):
        self.source_format = None
        self.target_format = None
        self.job_type_id = None
        self.description = None

