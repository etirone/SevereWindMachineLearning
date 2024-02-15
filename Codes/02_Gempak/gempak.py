#-------------------------------------------------------------------
# gempak.py
#
# Module for interface with gempak package
#-------------------------------------------------------------------

"""Python interface for gempak applications.

INTRODUCTION
This gempak interface is built contained the 'app' (application) class
whose entry point is:
        foo = gempak.app('application'[,clean=1])
where 'application' is a string containing the name of the gempak
application (e.g. gdplot2, sncfil, etc).  Several methods are available
to the user for setting gempak variables (macros) and executing commands
or full applications.

METHODS
        foo = gempak.app('application'[,clean=1][,hardcopy=0]) - Class
                constructor.  If 'clean' is boolean true (default), then
                the IPC buffer cleanup utility is run following the
                completion of the application.  If 'hardcopy' is set to
                true (false by default), then the IPC cleaner is used
                at the end of each recursion - this is necessary for the
                production of hardcopy graphics output.  Generally,
                clean=1,hardcopy=0 is applied to diagnostics, grid
                handling and X-windows generation while hardcopy=1 is
                applied to other graphics generation.
        foo.set(macro,value) - Set the given 'macro' to 'value'.
        foo.get(macro) - Get the value for 'macro'
        foo.clear([macro=None]) - Clear value of 'macro' (if given).  If
                no value is given for 'macro', then all macro settings
                for 'foo' are cleared.
        foo.list() - Print a list of the current application and macro
                settings.
        foo.info() - Print information about the utility and macro options
                of the currently-requested application.
        foo.help([macro=None]) - Print help information on the requested macro
                or revert to 'foo.info' if no macro is given.
        foo.nextLayer([clear=0]) - Increment the layer counter to move to
                next layer.  Copy the previous (current) layer attributes
                if clear=0 and the layer is new; otherwise start with a
                clean set of attributes (new layer) or the stored values
                (old layer).
        foo.layer(layerNumber,[clear=0]) - Jump to layer number 'layer'.
                Copy the current layer attributes if clear=0 and the layer
                is new; otherwise start with a clean set of attributes
                (new layer) or the stored values (old layer)
        foo.run() - Run the requested application using the macro settings
                contained in this instance of 'foo'.

CLASS VARIABLES
        GEMEXE - path the the gempak executable directory [$GEMEXE]
"""
from __future__ import print_function
version     = "0.0.0"
__author__  = "Ron McTaggart-Cowan (rmctc@users.sourceforge.net)"

#---------
# Imports
#---------
import subprocess
import os
import string
import re

class gemLayer(dict):
    """macro values for plot layers
    """

    # Constructor (inherit from dictionary class)
    def __init__(self,layer):
        dict.__init__(self)
        # return(self)

    # Public methods
    def set(self,macro,value=''):
        """Set macro value
        """
        self[macro] = value
        return(0)
    def get(self,macro):
        """Get macro value
        """        
        if macro in self.keys():
            return self[macro]
        else:            
            return('')
    def clear(self,macro=None):
        """Clear one or all macro values
        """
        if macro:
            del self[macro]
            return('CLEARED: '+macro)
        else:
            for key in self.keys():
                del self[key]
            return('CLEARED: All Macros')
    def parse(self):
        """Parse macro attributes to string for gempak applications
        """
        return ''.join([k+'='+str(v)+'\n' for (k,v) in self.items()])
    def run(self):
        """
        """
        for (k,v) in self.items():
            saveDevice = not self["device"] and None or self["device"]

class app(dict):
    """gempak application wrapper
    """

    # Public class variable definitions
    GEMEXE = os.getenv('GEMEXE')  #path to gempak executables

    # Private class variable definitions
    _protected = ['application','clean','hardcopy','layer','gemLayer']  #instance vars that are NOT macros
    _ipcCleanupApp = os.path.join(GEMEXE,'gpend')
    _quickListApp = os.path.join(GEMEXE,'gdinfo')
    _layerList = {}
    
    # Constructor (inherit from dictionary class)
    def __init__(self,app,clean=1,hardcopy=0):
        dict.__init__(self)
        self["application"] = os.path.join(self.GEMEXE,app)
        self["clean"] = clean
        self["hardcopy"] = hardcopy
        self["device"] = None
        self["layer"] = 1        
        self.layer(self["layer"])

    # Public methods
    def run(self):
        """Run a gempak application
        """
        current = self["layer"]
        self._run()
        if self["application"] is not self._ipcCleanupApp: self._clean()        
        self.layer(current)
        return('Run Operation Completed')
    def list(self):
        """Print list of current instance macros
        """
        print("\nGEMPAK application: "+self["application"]+"\n")
        print("GEMPAK macros:")
        print(self["gemLayer"].parse())
        print("Cleanup on Exit (0/1)? "+str(self["clean"]))
        return('List Complete')
    def set(self,macro,value=''):
        """Set macro value
        """
        if macro is 'application':
            self[macro] = os.path.join(self.GEMPAK,app) #note: discards GEMPAK if abs
            #path is given for 'app'
        else:
            self["gemLayer"].set(macro,value)
        return('SET: '+ macro.upper()+' = '+str(value))
    def get(self,macro):
        """Get macro value
        """
        if macro in self.keys(): return self[macro]
        if macro in self["gemLayer"].keys(): return self["gemLayer"].get(macro)        
        return('')
    def clear(self,macro=None):
        """Clear one or all macro values
        """
        return self["gemLayer"].clear(macro)
    def info(self):
        """Return information about the requested application
        """
        infoApp = app(self._quickListApp,clean=0)
        infoApp._run(command='h '+str(self._appNameOnly()))
    def help(self,macro=None):
        """Return help information on requested macro
        """
        if macro:
            helpApp = app(self._quickListApp,clean=0)
            helpApp._run(command='h '+str(macro))
        else:
            self.info()
    def layer(self,n,clear=0):
        """Set current layer number (first layer = 1)
        """
        if "gemLayer" in self.keys():
            current = self["gemLayer"]
        else:
            current = None
        if n not in self._layerList:
            self["gemLayer"] = gemLayer(n)
            self._layerList[n] = self["gemLayer"]               
            if current and not clear:
                for (macro,value) in current.items(): self["gemLayer"].set(macro,value)                
        else:
            self["gemLayer"] =   self._layerList[n]            
        self["layer"] = n
    def nextLayer(self,clear=0):
        """Increment layer counter to move to next layer
        """        
        self.layer(int(self["layer"])+1,clear=clear)

    #Private methods
    def _run(self,command=None):
        """Run gempak application
        """
        #Look for lists in first layer (1) only        
        self.layer(1)
        layer = self["gemLayer"]
        if self["application"] == self._ipcCleanupApp:
            inString = ''
        else:
            for (k,v) in layer.items():            
                if type(v) is list:                
                    saveDevice = layer.get('device') and None or layer.get('device')
                    for index in v:
                        self._deviceParser(index)
                        self._setAllLayers(k,index)                    
                        self._run()                    
                        if saveDevice: self._setAllLayers('device',saveDevice)                        
                    layer.set(k,v)
                    return(0)   
            if command:
                inString = command+'\nexit\n'
            else:
                inString = ''
                current = self["layer"]            
                for n in range(1,len(self._layerList)+1):                
                    self.layer(n)
                    layer = self["gemLayer"]
                    clear = layer.get('clear')
                    if n == 1:
                        layer.set('clear','yes')
                    else:
                        layer.set('clear','no')
                    inString += self["gemLayer"].parse()+'r\n\n'
                    layer.set('clear',clear)                
                self.layer(current)
                inString += 'exit\n' 
        try:  
            inString += '\nexit\n' 
            app = subprocess.Popen(self["application"], stdin=subprocess.PIPE)
            (_stdout, _stderr) = app.communicate(input=inString.encode('ascii'), timeout=15)
            if self["hardcopy"] and self["application"] is not self._ipcCleanupApp:
                clean = self["clean"]
                self["clean"] = 1
                self._clean()
                self["clean"] = clean
        except OSError as err:
            print(">>sys.stderr", "Execution failed:",err)
            #if app.stdout:
            #    print("OUTPUT: "+app.stdout+"\n")
        #if app.stderr:
        #    print("ERROR: "+app.stderr)
        return(0) 
    def _clean(self):
        """Run application to clean up process buffers on request
        """        
        if not self["clean"]: return(0)
        try:
            end = app(self._ipcCleanupApp,clean=0)
            end._run()
        except:
            return(-1)
        return('IPC Buffers Cleared')
    def _appNameOnly(self):
        """Trim full application path for name only
        """
        (head,tail) = os.path.split(self["application"])
        return(tail)
    def _deviceParser(self,add):
        """Add information to device name during recursion in hardcopy mode
        """
        layer = self["gemLayer"]        
        if not layer.get('device'): return(-1)
        if not self["hardcopy"]: return(0)        
        set = re.split('(\|)',str(layer.get('device')))
        fixAdd = re.sub('/','_',str(add))
        if len(set) >= 3:
            sep = re.compile('\.')
            if re.search(sep,str(layer.get('device'))):
                set[2] = re.sub(sep,'-'+str(fixAdd)+'.',set[2])
            else:
                set[2] += '-'+str(fixAdd)
        device = ''.join(item for item in set)  
        self._setAllLayers('device',device)        
        return(0)
    def _setAllLayers(self,macro,value):
        """Set all layers to specified value
        """        
        current = self["layer"]
        layer = self["gemLayer"]
        for n in self._layerList:
            self.layer(n)
            self["gemLayer"].set(macro,value)
        self.layer(current)

