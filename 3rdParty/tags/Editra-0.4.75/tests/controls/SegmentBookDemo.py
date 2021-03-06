###############################################################################
# Name: SegmentBookDemo.py                                                    #
# Purpose: SegmentBook control demo and test file                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2009 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################

"""
Test file for testing the SegmentBook control.

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import sys
import os
import wx

sys.path.insert(0, os.path.abspath('../../'))
import src.eclib.segmentbk as segmentbk
import src.eclib.ctrlbox as ctrlbox

# Local imports
import IconFile

#-----------------------------------------------------------------------------#

class TestPanel(segmentbk.SegmentBook):
    def __init__(self, parent, log):
        segmentbk.SegmentBook.__init__(self, parent,
                                       style=segmentbk.SEGBOOK_STYLE_NO_DIVIDERS|\
                                             segmentbk.SEGBOOK_STYLE_LABELS)

        # Attributes
        self.log = log
        self._menu = None
        self._imglst = wx.ImageList(32, 32, mask=False)

        # Setup
        bmp = IconFile.Monkey.GetBitmap()
        self._imglst.Add(bmp)
        bmp = IconFile.Devil.GetBitmap()
        self._imglst.Add(bmp)
        self.SetImageList(self._imglst)

        self.AddPage(wx.TextCtrl(self, style=wx.TE_MULTILINE, value="Hello"),
                     "Text Editor", img_id=0)
        self.AddPage(wx.GenericDirCtrl(self), "File Browser", img_id=1)
        self.AddPage(wx.TextCtrl(self, style=wx.TE_MULTILINE, value="Test Control"),
                     "Text Editor2", img_id=0)
        todo = wx.ListBox(self, choices=['Wake up',
                                         'Finish Event handling',
                                         'Take a nap',
                                         'Procrastinate for a while',
                                         'Drink some coffee',
                                         'Check in code'])
        self.AddPage(todo, "TODO List", img_id=1)

        # Add a sub controlbar
        cbar = ctrlbox.ControlBar(self, style=ctrlbox.CTRLBAR_STYLE_GRADIENT)
        cbar.SetVMargin(3, 3)
        self.SetControlBar(cbar, wx.BOTTOM)
        cbar.AddControl(wx.Button(cbar, wx.ID_NEW))
        cbar.AddControl(wx.Button(cbar, wx.ID_DELETE))

        # Event Handlers
        self.Bind(segmentbk.EVT_SB_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(segmentbk.EVT_SB_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(segmentbk.EVT_SB_PAGE_CONTEXT_MENU, self.OnPageMenu)
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_MENU, self.OnButton, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnButton, id=wx.ID_DELETE)

    def OnButton(self, evt):
        """Handle button clicks from control bar"""
        e_id = evt.GetId()
        if e_id == wx.ID_NEW:
            self.log.write("SegmentBook New Page")
            self.GetParent().Freeze()
            txt = wx.TextCtrl(self, style=wx.TE_MULTILINE, value="Enter Text Here")
            self.AddPage(txt, "Text Editor", select=True, img_id=0)
            self.GetParent().Thaw()
        elif e_id == wx.ID_DELETE:
            self.log.write("SegmentBook Delete Page")
            sel = self.GetSelection()
            if sel != -1:
                self.DeletePage(sel)

    def OnPageChanging(self, evt):
        """Handle the page changing events"""
        old = evt.GetOldSelection()
        new = evt.GetSelection()
        self.log.write("SegmentBook Page Changing: from %d, to %d" % (old, new))

    def OnPageChanged(self, evt):
        """Handle the page changed events"""
        new = evt.GetSelection()
        self.log.write("SegmentBook Page Changed to: to %d" % new)

    def OnPageMenu(self, evt):
        """Handle when a segment is right clicked on"""
        sel = evt.GetSelection()
        self.log.write("SegmentBook Segment Right Click: %d" % sel)
        if self._menu is None:
            self._menu = wx.Menu()
            self._menu.Append(wx.ID_NEW, "New")
            self._menu.AppendSeparator()
            self._menu.Append(wx.ID_DELETE, "Close")
        self.PopupMenu(self._menu)

#-----------------------------------------------------------------------------#

def MakeTestFrame(segment=False):
    frame = wx.Frame(None, title="SegmentBook Test")
    fsizer = wx.BoxSizer(wx.VERTICAL)
    panel = TestPanel(frame, TestLog())
    fsizer.Add(panel, 1, wx.EXPAND)
    return frame

#-----------------------------------------------------------------------------#

class TestLog:
    def __init__(self):
        pass

    def write(self, msg):
        print msg

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    try:
        import sys
        import run
    except ImportError:
        app = wx.PySimpleApp(False)
        frame = MakeTestFrame()
        frame.Show()
        app.MainLoop()
    else:
        run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
