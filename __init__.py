import os
import subprocess

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG
from mycroft.util.parse import extract_number


#####################################################################
#
# TESTS
#  1: search for file in linux desktop
#  2: open file in linux desktop
#    
# Sample:
#  search for init using file search in home Sathishkanna Downloads
#
# TODO:
#  1. case insensitive, proper '/'-ing and return path in checkNotDir()
#  2. update needed to test for negative and positive statements 
#    in handle_search_file() openCmd
#
#####################################################################

        
class SearchFileOpen(MycroftSkill):
    def __init__(self):
        super(SearchFileOpen, self).__init__("SearchFileOpen")
        
    def checkNotDir(self, userLoc):
        userLoc = '/' + userLoc.replace(' ', '/')
        if os.path.isdir(userLoc):
            userLoc = '/' + userLoc + '/'
        else:
            return None
        return userLoc
        
    def openFileOption(self, fileLoc = [], tst=0):
        cmd = 'xdg-open \"' + str(fileLoc[tst]) + '\"'
        subprocess.call(cmd, shell=True) # file open command
        fileName = fileLoc[tst].split('/')[-1]
        self.speak_dialog("process.done")
	    
	    
    @intent_file_handler('search.file.open.intent')
    def handle_search_file(self, message):
        keyName = message.data['file']
        if 'location' not in message.data:
            userLoc = self.get_response('ask.where')
            if userLoc is None:
                self.speak_dialog("process.terminated")
                return
        else:
            userLoc = message.data['location']
        userLoc = userLoc.strip()
        userDir = self.checkNotDir(userLoc)
        if userDir is None:
            self.speak_dialog("loc.notexist", data={"location": userLoc})
            return 
        userLoc = userDir
        cmd = 'find ' + userLoc + " -type f -iname *'" + keyName.strip().replace(' ', '*') + "'*"
        return_value = str(subprocess.check_output(cmd, shell=True))[2:-1] # file search command
        fileLoc = return_value.split('\\n')
        
        if len(fileLoc) < 2:
            self.speak_dialog("file.notexist", data={"file": keyName, "location": userLoc})
        else:
            self.speak_dialog("file.count", data={"file": keyName, "location": userLoc, "count": len(fileLoc)-1})
            if len(fileLoc) <= 6:
                if 'open' not in message.data:
                    openCmd = self.get_response('ask.open')
                    if openCmd is None:
                        self.speak_dialog("process.terminated")
                        return
                else:
                    openCmd = message.data['open'] 
                    
                if 'no' in openCmd:
                    self.speak_dialog("process.done.open")
                    return
                elif len(fileLoc) > 1 and len(fileLoc) < 3:
                    self.openFileOption(fileLoc)
                else:
                    self.speak_dialog('file.which', data={"count": len(fileLoc)-1})
                    i=0
                    for loc in fileLoc:
                        fileName = loc.split('/')[-1]
                        if fileLoc.index(loc) < len(fileLoc)-1:
                            self.speak_dialog("file.opt", data={"opt": fileLoc.index(loc) + 1, "file": fileName.strip()})
                        else :
                            self.speak_dialog("file.opt", data={"opt": fileLoc.index(loc) + 1, "file": ' *Exit*'})
                    openCmd = self.get_response('ask.which')
                    while True:
                        if openCmd is not None:
                            openOpt = extract_number(openCmd)
                        else :
                            openCmd = self.get_response('choose an option')
                            continue
                        if openOpt < len(fileLoc) and int(openOpt) >= 1:
                            self.openFileOption(fileLoc,int(openOpt-1))
                            return
                        elif openOpt == len(fileLoc):
                            return
                        else:
                            openCmd = self.get_response('wrong option')
                    
    @intent_file_handler('open.file.intent')
    def handle_file_open(self, message):
        keyName = message.data['file']
        if 'location' not in message.data:
            userLoc = self.get_response('ask.where')
            if userLoc is None:
                self.speak_dialog("process.terminated")
                return
        else:
            userLoc = message.data['location']
        userLoc = userLoc.strip().replace(' ', '/')
        userDir = self.checkNotDir(userLoc)
        if userDir is None:
            self.speak_dialog("loc.notexist", data={"location": userLoc})
            return 
        userLoc = userDir
        
        cmd = 'find ' + userLoc + " -type f -iname *'" + keyName.strip().replace(' ', '*') + "'*"
        
        return_value = str(subprocess.check_output(cmd, shell=True))[2:-1] # file search command
        fileLoc = return_value.split('\\n')
        
        if len(fileLoc) < 2:
            self.speak_dialog("file.notexist", data={"file": keyName, "location": userLoc})
        else:
            if len(fileLoc) <= 6:
                if len(fileLoc) > 1 and len(fileLoc) < 3:
                    self.openFileOption(fileLoc)
                else:
                    self.speak_dialog('file.which', data={"count": len(fileLoc)-1})
                    i=0
                    for loc in fileLoc:
                        fileName = loc.split('/')[-1]
                        if fileLoc.index(loc) < len(fileLoc)-1:
                            self.speak_dialog("file.opt", data={"opt": fileLoc.index(loc) + 1, "file": fileName.strip()})
                        else :
                            self.speak_dialog("file.opt", data={"opt": fileLoc.index(loc) + 1, "file": ' *Exit*'})
                    openCmd = self.get_response('ask.which')
                    while True:
                        if openCmd is not None:
                            openOpt = extract_number(openCmd)
                        else :
                            openCmd = self.get_response('choose an option')
                            continue
                        if openOpt < len(fileLoc) and int(openOpt) >= 1:
                            self.openFileOption(fileLoc,int(openOpt-1))
                            return
                        elif openOpt == len(fileLoc):
                            return
                        else:
                            openCmd = self.get_response('wrong option')
            else:
                self.speak_dialog("file.count.many", data={"file": keyName, "location": userLoc, "count": len(fileLoc)-1})


def create_skill():
    return SearchFileOpen()
