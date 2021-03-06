###############################################################################
# Name: Cody Precord                                                          #
# Purpose: File abstraction layer and text utilities                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Text/Unicode handling functions and File wrapper class

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import os
import sys
import re
import time
import wx
import threading
import codecs
import encodings
import locale
import types
from StringIO import StringIO

# Local Imports
from util import Log
from profiler import Profile_Get
import ed_msg
from ebmlib import GetFileModTime, GetFileSize

#--------------------------------------------------------------------------#
# Globals

# The default fallback encoding
DEFAULT_ENCODING = locale.getpreferredencoding()
try:
    codecs.lookup(DEFAULT_ENCODING)
except (LookupError, TypeError):
    DEFAULT_ENCODING = 'utf-8'

# File Helper Functions
BOM = { 'utf-8' : codecs.BOM_UTF8,
        'utf-16' : codecs.BOM }

# Regex for extracting magic comments from source files
# i.e *-* coding: utf-8 *-*, encoding=utf-8, ect...
# The first group from this expression will be the encoding.
RE_MAGIC_COMMENT = re.compile("coding[:=]\s*\"*([-\w.]+)\"*")

# File Load States
FL_STATE_START   = 0
FL_STATE_READING = 1
FL_STATE_PAUSED  = 2
FL_STATE_END     = 3
FL_STATE_ABORTED = 4

#--------------------------------------------------------------------------#

class ReadError(Exception):
    """Error happened while trying to read the file"""
    pass

class WriteError(Exception):
    """Error happened while trying to write the file"""
    pass

#--------------------------------------------------------------------------#

class EdFile(object):
    """Wrapper for representing a file object that stores data
    about the file encoding and path.

    """
    def __init__(self, path='', modtime=0):
        """Create the file wrapper object
        @param path: the absolute path to the file

        """
        object.__init__(self)

        # Attribtues
        self._handle = None
        self._magic = dict(comment=None, bad=False)
        self.encoding = Profile_Get('ENCODING', default=DEFAULT_ENCODING)
        self.open = False
        self.path = path
        self.bom = None
        self.modtime = modtime
        self.last_err = None
        self._mcallback = list()

    def AddModifiedCallback(self, callback):
        """Set modified callback method
        @param callback: callable

        """
        self._mcallback.append(callback)

    def ClearLastError(self):
        """Reset the error marker on this file"""
        del self.last_err
        self.last_err = None

    def Close(self):
        """Close the file handle
        @note: this is normally done automatically after a read/write operation

        """
        try:
            self._handle.close()
        except:
            pass

        self.open = False

    def CleanUp(self):
        """Cleanup callback"""
        pass

    def DoOpen(self, mode):
        """Opens and creates the internal file object
        @param mode: mode to open file in
        @return: True if opened, False if not
        @postcondition: self._handle is set to the open handle

        """
        if not len(self.path):
            return False

        try:
            file_h = open(self.path, mode)
        except (IOError, OSError), msg:
            self.last_err = msg
            return False
        else:
            self._handle = file_h
            self.open = True
            return True

    @property
    def Encoding(self):
        """File encoding property"""
        return self.encoding

    def FireModified(self):
        """Fire the modified callback(s)"""
        remove = list()
        for idx, mcallback in enumerate(self._mcallback):
            try:
                mcallback()
            except:
                remove.append(idx)

        # Cleanup any bad callbacks
        if len(remove):
            remove.reverse()
            for idx in remove:
                self._mcallback.pop(idx)

    def GetEncoding(self):
        """Get the encoding used by the file it may not be the
        same as the encoding requested at construction time
        @return: string encoding name

        """
        return self.encoding

    def GetExtension(self):
        """Get the files extension if it has one else simply return the
        filename minus the path.
        @return: string file extension (no dot)

        """
        fname = os.path.split(self.path)
        return fname[-1].split(os.extsep)[-1].lower()

    def GetLastError(self):
        """Return the last error that occured when using this file
        @return: err traceback or None

        """
        return str(self.last_err).replace("u'", "'")

    def GetMagic(self):
        """Get the magic comment if one was present
        @return: string or None

        """
        return self._magic['comment']

    def GetModtime(self):
        """Get the timestamp of this files last modification"""
        return self.modtime

    def GetPath(self):
        """Get the path of the file
        @return: string

        """
        return self.path

    def GetSize(self):
        """Get the size of the file
        @return: int

        """
        if self.path:
            return GetFileSize(self.path)
        else:
            return 0

    def HasBom(self):
        """Return whether the file has a bom byte or not
        @return: bool

        """
        return self.bom is not None

    def IsOpen(self):
        """Check if file is open or not
        @return: bool

        """
        return self.open

    def IsReadOnly(self):
        """Is the file Read Only
        @return: bool

        """
        if os.path.exists(self.path):
            return not os.access(self.path, os.R_OK|os.W_OK)
        else:
            return False

    @property
    def Modtime(self):
        """File modification time propery"""
        return self.GetModtime()

    def Read(self, store=None, chunk=512):
        """Get the contents of the file as a string, automatically handling
        any decoding that may be needed.

        @keyword store: generator method to pass read results through
        @keyword chunk: read size
        @note: the store param overrides incremental
        @return: unicode str

        """
        if self.DoOpen('rb'):
            lines = [ self._handle.readline() for x in range(2) ]
            self._handle.seek(0)
            enc = None
            if len(lines):
                enc = CheckBom(lines[0])
                if enc is None:
                    self.bom = None
                    if not self._magic['bad']:
                        enc = CheckMagicComment(lines)
                        if enc:
                            self._magic['comment'] = enc
                else:
                    Log("[ed_txt][info] File Has %s BOM" % enc)
                    self.bom = unicode(BOM.get(enc, None), enc)

            if enc is not None:
                self.encoding = enc
            try:
                reader = codecs.getreader(self.encoding)(self._handle)
                txt = u''
                if store is None:
                    while 1:
                        tmp = reader.read(chunk)
                        if not len(tmp):
                            break
                        txt += tmp
                else:
                    store(reader, chunk)
                reader.close()
            except Exception, msg:
                Log("[ed_txt][err] Error while reading with %s" % self.encoding)
                Log("[ed_txt][err] %s" % msg)
                self.last_err = str(msg)
                self.Close()
                if self._magic['comment']:
                    self._magic['bad'] = True

                enc, txt = FallbackReader(self.path)
                if enc is not None:
                    Log("[ed_txt][info] Fallback reader succeeded with: %s" % enc)
                    # TODO: don't clear the error and allow the client to
                    #       analyze it for error reporting.
                    self.ClearLastError()
                    self.encoding = enc
                else:
                    raise UnicodeDecodeError, msg

            if self.bom is not None:
                Log("[ed_txt][info] Stripping %s BOM from text" % self.encoding)
                txt = txt.replace(self.bom, u'', 1)

            Log("[ed_txt][info] Decoded %s with %s" % (self.path, self.encoding))
            self.SetModTime(GetFileModTime(self.path))
            return txt
        else:
            raise ReadError, self.last_err

    def ReadAsync(self, control):
        """Read the file asynchronously on a separate thread
        @param control: text control to send text to

        """
        pid = control.GetTopLevelParent().GetId()
        filesize = GetFileSize(self.path)
        ed_msg.PostMessage(ed_msg.EDMSG_PROGRESS_STATE, (pid, 1, filesize))
        thread = FileReadThread(control, self.ReadGenerator, 4096)
        thread.start()

    def ReadGenerator(self, chunk=512):
        """Get the contents of the file as a string, automatically handling
        any decoding that may be needed.

        @keyword chunk: read size
        @return: unicode str

        """
        if self.DoOpen('rb'):
            lines = [ self._handle.readline() for x in range(2) ]
            self._handle.seek(0)
            enc = None
            if len(lines):
                enc = CheckBom(lines[0])
                if enc is None:
                    self.bom = None
                    if not self._magic['bad']:
                        enc = CheckMagicComment(lines)
                        if enc:
                            self._magic['comment'] = enc
                else:
                    Log("[ed_txt][info] File Has %s BOM" % enc)
                    self.bom = unicode(BOM.get(enc, None), enc)

            if enc is not None:
                self.encoding = enc

            try:
                reader = codecs.getreader(self.encoding)(self._handle)
                while 1:
                    tmp = reader.read(chunk)
                    if not len(tmp):
                        break
                    yield tmp
                reader.close()
            except Exception, msg:
                Log("[ed_txt][err] Error while reading with %s" % self.encoding)
                Log("[ed_txt][err] %s" % msg)
                self.last_err = unicode(msg)
                self.Close()
                if self._magic['comment']:
                    self._magic['bad'] = True

                # TODO: handle incremental mode for 
#                enc, txt = FallbackReader(self.path)
#                if enc is not None:
#                    self.encoding = enc
#                else:
#                    raise UnicodeDecodeError, msg

            Log("[ed_txt][info] Decoded %s with %s" % (self.path, self.encoding))
            self.SetModTime(GetFileModTime(self.path))
        else:
            raise ReadError, self.last_err

    @property
    def ReadOnly(self):
        """Is the file read only?"""
        return self.IsReadOnly()

    def RemoveModifiedCallback(self, callback):
        """Remove a registered callback
        @param callback: callable to remove

        """
        if callback in self._mcallback:
            self._mcallback.remove(callback)

    def ResetAll(self):
        """Reset all attributes of this file"""
        self._handle = None
        self._magic = dict(comment=None, bad=False)
        self.encoding = Profile_Get('ENCODING', default=DEFAULT_ENCODING)
        self.open = False
        self.path = ''
        self.bom = None
        self.modtime = 0
        self.last_err = None

    def SetEncoding(self, enc):
        """Explicitly set/change the encoding of the file
        @param enc: encoding to change to

        """
        if enc is None:
            enc = DEFAULT_ENCODING
        self.encoding = enc

    def SetPath(self, path):
        """Set the path of the file
        @param path: absolute path to file

        """
        self.path = path

    def SetModTime(self, mtime):
        """Set the modtime of this file
        @param mtime: long int to set modtime to

        """
        self.modtime = mtime

    def ReadLines(self):
        """Get the contents of the file as a list of lines
        @return: list of strings

        """
        raise NotImplementedError

    def Write(self, value):
        """Write the given value to the file
        @param value: (Unicode) String of text to write to disk
        @note: exceptions are allowed to be raised for the writing
               but 

        """
        # Check if a magic comment was added or changed
        tbuff = StringIO(value)
        enc = CheckMagicComment([ tbuff.readline() for x in range(2) ])
        tbuff.close()
        del tbuff

        # Update encoding if necessary
        if enc is not None:
            self.encoding = enc

        # Open and write the file
        if self.DoOpen('wb'):
            Log("[ed_txt][info] Opened %s, writing as %s" % (self.path, self.encoding))
            writer = codecs.getwriter(self.encoding)(self._handle)
            if self.HasBom():
                Log("[ed_txt][info] Adding BOM back to text")
                value = self.bom + value
            writer.write(value)
            writer.close()
            Log("[ed_txt][info] %s was written successfully" % self.path)
        else:
            raise WriteError, self.last_err

#-----------------------------------------------------------------------------#

class FileReadThread(threading.Thread):
    """Worker thread for reading text from a file"""
    def __init__(self, reciever, task, *args, **kwargs):
        """Create the thread
        @param reciever: Window to recieve events
        @param task: generator method to call

        """
        threading.Thread.__init__(self)

        # Attributes
        self.cancel = False
        self._task = task
        self.reciever = reciever
        self._args = args
        self._kwargs = kwargs
        self.pid = reciever.GetTopLevelParent().GetId()

    def run(self):
        """Read the text"""
        evt = FileLoadEvent(edEVT_FILE_LOAD, wx.ID_ANY, None, FL_STATE_START)
        wx.PostEvent(self.reciever, evt)
        time.sleep(.75) # give ui a chance to get ready

        count = 1
        for txt in self._task(*self._args, **self._kwargs):
            if self.cancel:
                break

            evt = FileLoadEvent(edEVT_FILE_LOAD, wx.ID_ANY, txt)
            evt.SetProgress(count * self._args[0])
            wx.PostEvent(self.reciever, evt)
            count += 1

        evt = FileLoadEvent(edEVT_FILE_LOAD, wx.ID_ANY, None, FL_STATE_END)
        wx.PostEvent(self.reciever, evt)

    def Cancel(self):
        """Cancel the running task"""
        self.cancel = True

#-----------------------------------------------------------------------------#

edEVT_FILE_LOAD = wx.NewEventType()
EVT_FILE_LOAD = wx.PyEventBinder(edEVT_FILE_LOAD, 1)
class FileLoadEvent(wx.PyEvent):
    """Event to signal that a chunk of text haes been read"""
    def __init__(self, etype, eid, value=None, state=FL_STATE_READING):
        """Creates the event object"""
        wx.PyEvent.__init__(self, eid, etype)

        # Attributes
        self._state = state
        self._value = value
        self._prog = 0
    
    def HasText(self):
        """Returns true if the event has text
        @return: bool whether the event contains text

        """
        return self._value is not None

    def GetProgress(self):
        """Get the current progress of the load"""
        return self._prog

    def GetState(self):
        """Get the state of the file load action
        @return: int (FL_STATE_FOO)

        """
        return self._state

    def GetValue(self):
        """Returns the value from the event.
        @return: the value of this event

        """
        return self._value

    def SetProgress(self, progress):
        """Set the number of bytes that have been read
        @param progress: int

        """
        self._prog = progress

#-----------------------------------------------------------------------------#
# Utility Function
def CheckBom(line):
    """Try to look for a bom byte at the begining of the given line
    @param line: line (first line) of a file
    @return: encoding or None

    """
    has_bom = None
    for enc, bom in BOM.iteritems():
        if line.startswith(bom):
            has_bom = enc
            break
    return has_bom

def CheckMagicComment(lines):
    """Try to decode the given text on the basis of a magic
    comment if one is present.
    @param lines: list of lines to check for a magic comment
    @return: encoding or None

    """
    enc = None
    for line in lines:
        match = RE_MAGIC_COMMENT.search(line)
        if match:
            enc = match.group(1)
            try:
                codecs.lookup(enc)
            except LookupError:
                enc = None
            break

    Log("[ed_txt][info] MagicComment is %s" % enc)
    return enc

def DecodeString(string, encoding=None):
    """Decode the given string to Unicode using the provided
    encoding or the DEFAULT_ENCODING if None is provided.
    @param string: string to decode
    @keyword encoding: encoding to decode string with

    """
    if encoding is None:
        encoding = DEFAULT_ENCODING

    if not isinstance(string, types.UnicodeType):
        try:
            rtxt = codecs.getdecoder(encoding)(string)[0]
        except Exception, msg:
            Log("[ed_txt][err] DecodeString with %s failed" % encoding)
            Log("[ed_txt][err] %s" % msg)
            rtxt = string
        return rtxt
    else:
        # The string is already unicode so just return it
        return string

def EncodeString(string, encoding=None):
    """Try and encode a given unicode object to a string
    with the provided encoding returning that string. The
    default encoding will be used if None is given for the
    encoding.
    @param string: unicode object to encode into a string
    @keyword encoding: encoding to use for conversion

    """
    if not encoding:
        encoding = DEFAULT_ENCODING

    if isinstance(string, types.UnicodeType):
        try:
            rtxt = codecs.getencoder(encoding)(string)[0]
        except LookupError:
            rtxt = string
        return rtxt
    else:
        return string

def FallbackReader(fname):
    """Guess the encoding of a file by brute force by trying one
    encoding after the next until something succeeds.
    @param fname: file path to read from

    """
    txt = None
    for enc in GetEncodings():
        try:
            handle = open(fname, 'rb')
            reader = codecs.getreader(enc)(handle)
            txt = reader.read()
            reader.close()
        except Exception, msg:
            handle.close()
            continue
        else:
            return (enc, txt)

    return (None, None)

def GetEncodings():
    """Get a list of possible encodings to try from the locale information
    @return: list of strings

    """
    encodings = list()
    encodings.append(Profile_Get('ENCODING', None))

    try:
        encodings.append(locale.getpreferredencoding())
    except:
        pass
    
    encodings.append('utf-8')

    try:
        encodings.append(locale.nl_langinfo(locale.CODESET))
    except:
        pass
    try:
        encodings.append(locale.getlocale()[1])
    except:
        pass
    try:
        encodings.append(locale.getdefaultlocale()[1])
    except:
        pass
    encodings.append(sys.getfilesystemencoding())
    encodings.append('latin-1')

    # Clean the list for duplicates and None values
    rlist = list()
    for enc in encodings:
        if enc is not None and len(enc) and enc not in rlist:
            rlist.append(enc.lower())

    return rlist
