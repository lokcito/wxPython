###############################################################################
# Name: htmlcomp.py                                                           #
# Purpose: Simple input assistant for html and xml.                           #
# Author: Cody Precord                                                        #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Simple autocompletion support for HTML and XML documents.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__cvsid__ = "$Id$"
__revision__ = "$Revision$"

#--------------------------------------------------------------------------#
# Imports
import re
import wx
import wx.stc

# Local Imports
import completer

#--------------------------------------------------------------------------#
# Standard Html Tags
TAGS = ['!--', 'a', 'abbr', 'accept', 'accesskey', 'acronym', 'action',
        'address', 'align', 'alink', 'alt', 'applet', 'archive', 'area', 'axis',
        'b', 'background', 'base', 'basefont', 'bdo', 'bgcolor', 'big',
        'blockquote', 'body', 'border', 'bordercolor', 'br', 'button',
        'caption', 'cellpadding', 'cellspacing', 'center', 'char', 'charoff',
        'charset', 'checked', 'cite', 'cite', 'class', 'classid', 'clear',
        'code', 'codebase', 'codetype', 'col', 'colgroup', 'color', 'cols',
        'colspan', 'compact', 'content', 'coords', 'data', 'datetime', 'dd',
        'declare', 'defer', 'del', 'dfn', 'dir', 'dir', 'disabled', 'div', 'dl',
        'dt', 'dtml-call', 'dtml-comment', 'dtml-if', 'dtml-in', 'dtml-let',
        'dtml-raise', 'dtml-tree', 'dtml-try', 'dtml-unless', 'dtml-var',
        'dtml-with', 'em', 'enctype', 'face', 'fieldset', 'font', 'for', 'form',
        'frame', 'gutter', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head',
        'headers', 'height', 'hr', 'href', 'hreflang', 'hspace', 'html',
        'http-equiv', 'i', 'id', 'iframe', 'img', 'input', 'ins', 'isindex',
        'ismap', 'kbd', 'label', 'lang', 'language', 'legend', 'li', 'link',
        'link', 'longdesc', 'lowsrc', 'map', 'marginheight', 'marginwidth',
        'maxlength', 'menu', 'meta', 'method', 'multiple', 'name', 'nohref',
        'noscript', 'nowrap', 'object', 'ol', 'optgroup', 'option', 'p',
        'param', 'pre', 'profile', 'prompt', 'q', 'readonly', 'rel', 'rev',
        'rows', 'rowspan', 'rules', 's', 'samp', 'scheme', 'scope', 'script',
        'scrolling', 'select', 'selected', 'shape', 'size', 'small', 'span',
        'src', 'standby', 'start', 'strike', 'strong', 'style', 'sub',
        'summary', 'sup', 'tabindex', 'table', 'target', 'tbody', 'td', 'text',
        'textarea', 'tfoot', 'th', 'thead', 'title', 'tr', 'tt', 'type', 'u',
        'ul', 'url', 'usemap', 'valign', 'value', 'valuetype', 'var', 'version',
        'vlink', 'vspace', 'width', 'wrap', 'xmp']

# Tags that usually have a new line inbetween them
NLINE_TAGS = ('body', 'head', 'html', 'ol', 'style', 'table', 'tbody', 'ul')

TAG_RE = re.compile("\<\s*([a-zA-Z][a-zA-Z0-9]*)")

#--------------------------------------------------------------------------#

class Completer(completer.BaseCompleter):
    """Code completer provider"""
    _autocomp_keys = [ord('>'), ord('<')]
    _autocomp_stop = ' '
    _autocomp_fillup = ''

    def __init__(self, stc_buffer):
        completer.BaseCompleter.__init__(self, stc_buffer)

        # Setup
        self.SetAutoCompAfter(True) # Insert Text after cursor on completions

    def GetAutoCompKeys(self):
        """Returns the list of key codes for activating the
        autocompletion.
        @return: list of autocomp activation keys

        """
        return Completer._autocomp_keys

    def GetAutoCompList(self, command):
        """Returns the list of possible completions for a
        command string. If namespace is not specified the lookup
        is based on the locals namespace
        @param command: commadn lookup is done on
        @keyword namespace: namespace to do lookup in

        """
        if command in [None, u'']:
            return u''

        buff = self.GetBuffer()
        cpos = buff.GetCurrentPos()
        cline = buff.GetCurrentLine()

        tmp = buff.GetLine(cline).rstrip()

        # Check if we are completing an open tag
        if tmp.endswith('<'):
            if buff.GetLexer() == wx.stc.STC_LEX_XML:
                return _FindXmlTags(buff.GetText())
            else:
                return TAGS

        tmp = tmp.rstrip('>').rstrip()
        if not tmp.endswith('/'):
            for line in range(cline, -1, -1):
                txt = buff.GetLine(line)
                if line == cline:
                    txt = txt[:buff.GetColumn(cpos)]

                idx = txt.rfind('<')
                if idx != -1:
                    parts = txt[idx:].lstrip('<').strip().split()
                    if len(parts):
                        tag = parts[0].rstrip('>')
                        if len(tag) and \
                           tag not in ('img', 'br', '?php', '?xml', '?') and \
                           not tag[0] in ('!', '/'):
                            rtag = u"</" + tag + u">"
                            if tag in NLINE_TAGS:
                                rtag = buff.GetEOLChar() + rtag

                            if not parts[-1].endswith('>'):
                                rtag = u">" + rtag
                            return [rtag, ]
                    break

        return list()

    def GetAutoCompStops(self):
        """Returns a string of characters that should cancel
        the autocompletion lookup.
        @return: string of keys that will cancel autocomp/calltip actions

        """
        return Completer._autocomp_stop

    def GetAutoCompFillups(self):
        """List of keys to fill up autocompletions on"""
        return Completer._autocomp_fillup

#--------------------------------------------------------------------------#

def _FindXmlTags(text):
    """Dynamically generate a list of possible xml tags based on tags found in
    the given text.
    @param text: string
    @return: sorted list

    """
    matches = TAG_RE.findall(text)
    if len(matches):
        matches.append(u'!--')
        matches = list(set(matches))
        matches.sort()
    else:
        matches = [u'!--', ]
    return matches
