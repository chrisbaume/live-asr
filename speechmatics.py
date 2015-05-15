#!/usr/bin/python

import os
import urllib
import urllib2
import itertools
import mimetools
import mimetypes
import time, datetime
import json
import stat
import re
from optparse import OptionParser

class SpeechmaticsClient:
    """ A simple client for the Speechmatics REST API
    Documentation at https://www.speechmatics.com/api-details """

    def __init__(self, api_user_id, api_token):
        self.api_user_id = api_user_id
        self.api_token = api_token
        self.base_url = 'https://api.speechmatics.com/v1.0'
#        self.base_url = 'http://localhost:3100'
#        self.base_url = 'http://0.0.0.0:9999'


    def upload_audio(self, directory, filename, lang):
        """ Upload a new audio file to speechmatics for transcription 
        If upload suceeds then this method will return the id of the new transcription job """
        params = { 'auth_token' : self.api_token}
        try:
            url = self.base_url+'/user/'+str(self.api_user_id)+'/jobs/?'+urllib.urlencode(params, True)
            print url
            opener = urllib2.build_opener(MultipartPostHandler)
            params = { "data_file" : open(os.path.join(directory, filename), "rb"), "model" : lang }
            json_str = opener.open(url, params).read()
            return json.loads(json_str)['id']
        except urllib2.URLError, ue:
            print str(ue)
            if hasattr(ue, 'code'):
                if ue.code==400:
                  print "\nCommon causes of this error are:\nMalformed arguments\nMissing data file\nAbsent / unsupported language selection\nAudio file sampling rate <16KHz\n\nIf you are still unsure why this failed contact speechmatics: support@speechmatics.com"
                elif ue.code==401:
                  print "\nCommon causes of this error are:\nInvalid user id or authentication token\n\nIf you are still unsure why this failed contact speechmatics: support@speechmatics.com"
                elif ue.code==403:
                  print "\nCommon causes of this error are:\nInsufficient credit\nUser id not in our database\nIncorrect authentication token\n\nIf you are still unsure why this failed contact speechmatics: support@speechmatics.com"
            return None 

    def get_job_details(self, job_id):
        """ Checks on the status of the given job. """
        params = { 'auth_token' : self.api_token}
        try:
            url = self.base_url+'/user/'+str(self.api_user_id)+'/jobs/'+str(job_id)+'/?'+urllib.urlencode(params, True)
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            json_str = response.read()
            return json.loads(json_str)['job']
        except urllib2.URLError:
            return None
    
    def get_transcription(self, job_id, text_format):
        """ Downloads transcript for given job. """
        params = { 'auth_token' : self.api_token }
        if text_format:
            params['format'] = 'txt'

        try:
            url = self.base_url+'/user/'+str(self.api_user_id)+'/jobs/'+str(job_id)+'/transcript?'+urllib.urlencode(params, True)
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            
            if text_format:
                return response.read()
            else :
                json_str = response.read()
                return json.loads(json_str)
        except urllib2.URLError:
            return None

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

# Controls how sequences are uncoded. If true, elements may be given multiple values by
#  assigning a sequence.
doseq = 1

class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                 for(key, value) in data.items():
                     if type(value) == file:
                         v_files.append((key, value))
                     else:
                         v_vars.append((key, value))
            except TypeError:
                systype, value, traceback = sys.exc_info()
                raise TypeError, "not a valid non-string sequence or mapping object", traceback

            if len(v_files) == 0:
                data = urllib.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if(request.has_header('Content-Type')
                   and request.get_header('Content-Type').find('multipart/form-data') != 0):
                    print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        return request

    def multipart_encode(vars, files, boundary = None, buffer = None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buffer is None:
            buffer = ''
        for(key, value) in vars:
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"' % key
            buffer += '\r\n\r\n' + value + '\r\n'
        for(key, fd) in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = fd.name.split('/')[-1]
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
            buffer += 'Content-Type: %s\r\n' % contenttype
            # buffer += 'Content-Length: %s\r\n' % file_size
            fd.seek(0)
            buffer += '\r\n' + fd.read() + '\r\n'
        buffer += '--%s--\r\n\r\n' % boundary
        return boundary, buffer
    multipart_encode = Callable(multipart_encode)

    https_request = http_request

def checkRequiredArguments(opts, parser):
    missing_options = []
    for option in parser.option_list:
        if re.match(r'^\[REQUIRED\]', option.help) and eval('opts.' + option.dest) == None:
            missing_options.extend(option._long_opts)
    if len(missing_options) > 0:
        if not opts.lang:
            print "\nTarget language required"
            print "See https://www.speechmatics.com/support for a list of currently supported languaged\n"
        parser.error('Missing REQUIRED parameters: ' + str(missing_options))
        parser.print_help()
        exit(0)

def handle_options():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="[REQUIRED] Create new job to transcribe FILE.", metavar="FILE")
    parser.add_option("-i", "--id", dest="api_user_id",
                      help="[REQUIRED] API User Id.", metavar="API_USER_ID")
    parser.add_option("-o", "--output", dest="output_filename",
                      help="write transcript to FILE", metavar="FILE")
    parser.add_option("-t", "--token", dest="api_token",
                      help="[REQUIRED] API Auth Token.", metavar="API_AUTH_TOKEN")
    parser.add_option("-x", "--text", dest="text_format", action="store_true",
                      help="return transcription in plain text format")
    parser.add_option("-l", "--lang", dest="lang",
                      help="[REQUIRED] Language to use (e.g., en-US).", metavar="LANG")       
    
    (options, args) = parser.parse_args()
    checkRequiredArguments(options, parser)
    return options

if __name__ == "__main__":
    options = handle_options()

    client = SpeechmaticsClient(options.api_user_id, options.api_token)

    for attempt in range(0,10):
        print "Uploading audio file: "+options.filename
        (directory, filename) = os.path.split(os.path.abspath(options.filename))
        job_id = client.upload_audio(directory, filename, options.lang)
        if job_id != None:
            print "New job started with id: "+str(job_id)
            break
        else:
            print "Connection Failure, trying again"
            time.sleep(30)
    else:
        print "Connection Failed, exiting"
        exit(1)

    for attempt in range(0,10):
        details = client.get_job_details(job_id)
        if details == None:
            print "Connection Failure, trying again"
            time.sleep(30)
        else:
            break
    else:
        print "Connection Failed, exiting"
        exit(1)

    oldStatus="NotStarted"
    while details['job_status'] != 'done' and details['job_status'] != 'expired' and details['job_status'] != 'unsupported_file_format':
        if oldStatus != details['job_status']:
          print "Transcription in progress, "+details['job_status']
        oldStatus = details['job_status']
        epoch_now = int(time.time()) 
        wait_s = details['next_check'] - epoch_now
        #print "waiting requested check back time of "+str(wait_s)+"s"
        time.sleep(wait_s)
        for attempt in range(0,10):
            details = client.get_job_details(job_id)
            if details == None:
                print "Connection Failure, trying again"
                time.sleep(30)
            else:
                break
        else:
            print "Connection Failed, exiting"
            exit(1)

    if details['job_status'] == 'unsupported_file_format':
      print "File was in an unsupported file format and could not be transcribed."
      print "You have been reimbursed all credits for this job."
  
    else:
      print "Transcription complete, downloading transcription"
      transcript = client.get_transcription(job_id, options.text_format)
      if options.output_filename:
          f = open(options.output_filename, 'wt')
          if options.text_format:
              f.write(transcript)
          else:
              f.write(json.dumps(transcript, indent = 4))
      else:
          if options.text_format:
              print transcript
          else:
              print json.dumps(transcript, indent = 4)

    



        
