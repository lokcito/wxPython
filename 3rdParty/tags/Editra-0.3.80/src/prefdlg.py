###############################################################################
# Name: prefdlg.py                                                            #
# Purpose: UI for configuring User Profile                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
The classes and functions contained in this file are used for creating the
preference dialog that allows for dynamically configuring most of the options
and setting of the program by setting values in the Profile.

@summary: Editra's Preference Dialog

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#----------------------------------------------------------------------------#
# Dependancies
import wx
import wx.lib.mixins.listctrl as listmix
import locale
import encodings
import os
import sys

# Editra Libraries
import ed_glob
import profiler
from profiler import Profile_Get, Profile_Set
import ed_i18n
import ed_event
import ed_crypt
import updater
import util
import syntax.syntax as syntax
import ed_msg
import eclib.elistmix as elistmix

#----------------------------------------------------------------------------#
# Globals
ID_CHECK_UPDATE = wx.NewId()
ID_DOWNLOAD     = wx.NewId()
ID_UPDATE_MSG   = wx.NewId()

_ = wx.GetTranslation
#----------------------------------------------------------------------------#
# Class Globals
from extern.embeddedimage import PyEmbeddedImage

ButtonBackground = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAfhJ"
    "REFUWIXtlz9uGkEUh7/ZWbDdEAWH0ltRYCKRigNQxhFS3EUuUjlGspQLODfIAVxEkVPFzgmc"
    "LhegCoolupWQ6GIcWIvE7DwmBX9iwGBiMG74SVvM6M37ffPeaEarGFQceJbJZA611inmKBEp"
    "l0qlfeA7UOvNq2sxu6lUKpfNZne2nm+x/mR9nv6c/zzn9OspxWLxuFwuvwakB+BEIpE3hb3C"
    "+2QyGfM8b67Gw6pUKhy8O/jQbDb3AVFAbvvl9rd8Pn+vxtdVrVY5+nR07Pv+W3djw9vzPI8g"
    "uATsQgBisUdsbqZ3fN//6EZc91UikSAIGrcutNZirUUphVLq1vhJeppOc3b249A1xlD/VZ9s"
    "3K2MYjbTkbxtm3KNGBpT7H58FrgrlxGDKyI0GsHdAWaQiNBpQX2wBRM3ZKcJmry0J2MMrhjh"
    "MnigChjBDY2hVrtAaz3zyZ5W1lpEhNAYFN3KxB/HiUai/SCtNdHoylwMW60rROTfOGxRu+g8"
    "B32AYWmtWYmuDswppVhbXcNxnJH4tm0ThiHGhNihjFetPwMAAznHAYyTqyNA50IaosNaS7t9"
    "s9E4/TfAvDVayyXAEmAJsARYAixWLxzgywMC/AbI0XmQFv19pvMvigMUgPoCzevA7nA5CgsE"
    "KNzUD6fbjpN7ND7pevQP/18X4iAGbqux9wAAAABJRU5ErkJggg==")

def MakeThemeTool(tool_id):
    """Makes a themed bitmap for the tool book of the pref dialog.
    @param tool_id: An art identifier id
    @return: 32x32 bitmap

    """
    osize = Profile_Get('ICON_SZ', 'size_tuple', (24, 24))
    Profile_Set('ICON_SZ', (24, 24))
    over = wx.ArtProvider.GetBitmap(str(tool_id), wx.ART_TOOLBAR)
    Profile_Set('ICON_SZ', osize)
    mdc = wx.MemoryDC(ButtonBackground.GetBitmap())
    if over.IsOk():
        # Create overlay
        if over.GetSize() != (24, 24):
            over = over.ConvertToImage()
            over.Rescale(24, 24, wx.IMAGE_QUALITY_HIGH)
            over = over.ConvertToBitmap()

        # Draw overlay onto button
        mdc.SetBrush(wx.TRANSPARENT_BRUSH)
        mdc.DrawBitmap(over, 4, 4, True)
    return mdc.GetAsBitmap()

#----------------------------------------------------------------------------#

class PreferencesDialog(wx.Frame):
    """Preference dialog for configuring the editor
    @summary: Provides an interface into configuring profile settings

    """
    __name__ = u'PreferencesDialog'

    def __init__(self, parent, id_=wx.ID_ANY,
                 style=wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL):
        """Initialises the preference dialog
        @param parent: The parent window of this window
        @param id_: The id of this window

        """
        wx.Frame.__init__(self, parent, id_,
                          _("Preferences - Editra"), style=style)
        util.SetWindowIcon(self)

        # Extra Styles
        self.SetTransparent(Profile_Get('ALPHA', 'int', 255))

        # Attributes
        self._accel = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CLOSE)])
        self.SetAcceleratorTable(self._accel)
        self._tbook = PrefTools(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Layout
        sizer.Add(self._tbook, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()
        wx.GetApp().RegisterWindow(repr(self), self, True)

        # Bind Events
        self.Bind(wx.EVT_MENU, lambda evt: self.Close(), id=wx.ID_CLOSE)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SHOW, self.OnShow)

    def OnClose(self, evt):
        """Hanles the window closer event
        @param evt: Event that called this handler

        """
        # XXX More strange wx is None errors have been reported here
        #     really need to find the cause of this!
        if wx is not None:
            wx.GetApp().UnRegisterWindow(repr(self))

        # Save profile settings
        profiler.Profile().Write(profiler.Profile_Get('MYPROFILE'))

        evt.Skip()

    def OnShow(self, evt):
        """Hanles the window closer event
        @param evt: Event that called this handler

        """
        self._tbook.OnPageChanged()
        evt.Skip()

#-----------------------------------------------------------------------------#

class PrefTools(wx.Toolbook):
    """Main sections of the configuration pages
    @note: implements the top level book control for the prefdlg
    @todo: when using BK_BUTTONBAR style so that the icons have text
           under them the icons get scaled to larger size on the Mac
           causing them to look poor.

    """
    GENERAL_PG = 0
    APPEAR_PG  = 1
    DOC_PG     = 2
    UPDATE_PG  = 3
    ADV_PG     = 4

    def __init__(self, parent, tbid=wx.ID_ANY, style=wx.BK_BUTTONBAR):
        """Initializes the main book control of the preferences dialog
        @summary: Creates the top level notebook control for the prefdlg
                  a toolbar is used for changing pages.
        @todo: There is some nasty dithering/icon rescaling happening on
               osx. need to se why this is.
        @note: Look into wxtoolbook source and see why images cant be changed
               after they have been set. Because of this when the theme is
               changed the toolbook icons cannont be updated instantly.

        """
        wx.Toolbook.__init__(self, parent, tbid, style=style)

        # Attributes
        self._imglst = wx.ImageList(32, 32)
        self._imglst.Add(MakeThemeTool(ed_glob.ID_PREF))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_THEME))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_DOCPROP))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_WEB))
        self._imglst.Add(MakeThemeTool(ed_glob.ID_ADVANCED))
        self.SetImageList(self._imglst)

        self.AddPage(GeneralPanel(self), _("General"),
                     imageId=self.GENERAL_PG)
        self.AddPage(AppearancePanel(self), _("Appearance"),
                     imageId=self.APPEAR_PG)
        self.AddPage(DocumentPanel(self), _("Document"),
                     imageId=self.DOC_PG)
        self.AddPage(NetworkPanel(self), _("Network"),
                     imageId=self.UPDATE_PG)
        self.AddPage(AdvancedPanel(self), _("Advanced"),
                     imageId=self.ADV_PG)

        # Event Handlers
        self.Bind(wx.EVT_TOOLBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPageChanged(self, evt=None):
        """Resizes the dialog based on the pages size
        @todo: animate the resizing so its smoother

        """
        util.Log("[prefdlg][evt] toolbook page changed")
        page = self.GetPage(self.GetSelection())
        page.SetInitialSize()
        parent = self.GetParent()
        psz = page.GetSize()
        tbh = self.GetToolBar().GetSize().GetHeight()

        # Make sure not to resize the width less than the size needed to show
        # all the books icons.
        tbw = self.GetToolBar().GetBestSize().GetWidth()
        if psz.GetWidth() >= tbw:
            width = psz.GetWidth()
        else:
            width = tbw

        page.Freeze()
        parent.SetClientSize((width, psz.GetHeight() + tbh))
        parent.SendSizeEvent()
        parent.Layout()
        page.Thaw()
        if evt is not None:
            evt.Skip()

    def OnPaint(self, evt):
        """Paint the toolbar's background
        @todo: it would be nice to use a unified toolbar style on osx
        @note: unified toolbar is available in 2.8.5+ maybe create custom
               window using native toolbar to accomidate this.

        """
        # This is odd but I have recieved a number of error reports where
        # wx is being reported as None in this function
        if 'wx' not in globals() or wx is None:
            evt.Skip()
            return

        dc = wx.PaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        col1 = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        col2 = util.AdjustColour(col1, -10)
        rect = self.GetToolBar().GetRect()

        # Create the background path
        path = gc.CreatePath()
        path.AddRectangle(0, 0, rect.width, (rect.height + 3))

        gc.SetPen(wx.Pen(col1, 1))
        grad = gc.CreateLinearGradientBrush(0, 0, 0, rect.height, col1, col2)
        gc.SetBrush(grad)
        gc.DrawPath(path)

        evt.Skip()

#-----------------------------------------------------------------------------#

class GeneralPanel(wx.Panel):
    """Creates a panel with controls for Editra's general settings
    @summary: Panel with a number of controls that affect the users
              global profile setting for how Editra should operate.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Attributes
        self.SetToolTipString(_("Changes made in this dialog are saved in your "
                                "current profile. Some Items such as Language "
                                "require the program to be restarted before "
                                "taking effect."))

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_COMBOBOX, self.OnChoice)

    def __DoLayout(self):
        """Add the controls and do the layout
        @note: do not call this after __init__

        """
        # Startup Section
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([(wx.StaticText(self, label=_("Editor Mode") + u": "),
                         0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (ExChoice(self, ed_glob.ID_PREF_MODE,
                                  choices=['CODE', 'DEBUG'],
                                  default=Profile_Get('MODE')),
                          0, wx.ALIGN_CENTER_VERTICAL)])

        psizer = wx.BoxSizer(wx.HORIZONTAL)
        psizer.AddMany([(wx.StaticText(self, label=_("Printer Mode") + u": "),
                         0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (ExChoice(self, ed_glob.ID_PRINT_MODE,
                                  choices=GetPrintModeStrings(),
                                  default=Profile_Get('PRINT_MODE')),
                         0, wx.ALIGN_CENTER_VERTICAL)])

        reporter_cb = wx.CheckBox(self, ed_glob.ID_REPORTER,
                                  _("Disable Error Reporter"))
        reporter_cb.SetValue(not Profile_Get('REPORTER'))
        sess_cb = wx.CheckBox(self, ed_glob.ID_SESSION, _("Load Last Session"))
        sess_cb.SetValue(Profile_Get('SAVE_SESSION'))
        sess_cb.SetToolTipString(_("Load files from last session on startup"))
        splash_cb = wx.CheckBox(self, ed_glob.ID_APP_SPLASH,
                                _("Show Splash Screen"))
        splash_cb.SetValue(Profile_Get('APPSPLASH'))
        chk_update = wx.CheckBox(self, ed_glob.ID_PREF_CHKUPDATE,
                                 _("Check for updates on startup"))
        chk_update.SetValue(Profile_Get('CHECKUPDATE'))

        # File settings
        fhsizer = wx.BoxSizer(wx.HORIZONTAL)
        fhsizer.AddMany([(wx.StaticText(self,
                          label=_("File History Length") + u": "),
                          0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                         (ExChoice(self, ed_glob.ID_PREF_FHIST,
                                   choices=[str(val) for val in range(1, 10)],
                                   default=Profile_Get('FHIST_LVL', 'str')),
                         0, wx.ALIGN_CENTER_VERTICAL)])

        win_cb = wx.CheckBox(self, ed_glob.ID_NEW_WINDOW,
                             _("Open files in new windows by default"))
        win_cb.SetValue(Profile_Get('OPEN_NW'))
        pos_cb = wx.CheckBox(self, ed_glob.ID_PREF_SPOS,
                             _("Remember File Position"))
        pos_cb.SetValue(Profile_Get('SAVE_POS'))
        chkmod_cb = wx.CheckBox(self, ed_glob.ID_PREF_CHKMOD,
                                _("Check if on disk file has been "
                                  "modified by others"))
        chkmod_cb.SetValue(Profile_Get('CHECKMOD'))

        # Locale
        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        lsizer.AddMany([(wx.StaticText(self, label=_("Language") + u": "),
                         0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (ed_i18n.LangListCombo(self, ed_glob.ID_PREF_LANG,
                                               Profile_Get('LANG')),
                         0, wx.ALIGN_CENTER_VERTICAL)])

        # Layout items
        sizer = wx.FlexGridSizer(15, 2, 5, 5)
        sizer.AddMany([((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self,
                        label=_("Startup Settings") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), (msizer, 0),
                       ((5, 5),), (psizer, 0),
                       ((5, 5),), (reporter_cb, 0),
                       ((5, 5),), (sess_cb, 0),
                       ((5, 5),), (splash_cb, 0),
                       ((5, 5),), (chk_update, 0),
                       ((5, 5),), ((5, 5),),
                       (wx.StaticText(self, label=_("File Settings") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), (fhsizer, 0),
                       ((5, 5),), (win_cb, 0),
                       ((5, 5),), (pos_cb, 0),
                       ((5, 5),), (chkmod_cb, 0),
                       ((5, 5),), ((5, 5),),
                       (wx.StaticText(self, label=_("Locale Settings") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), (lsizer, 0),
                       ((10, 10), 0)])
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((10, 10), 0), (sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

    @staticmethod
    def OnCheck(evt):
        """Handles events from the check boxes
        @param evt: event that called this handler

        """
        util.Log("[prefdlg][evt] General Page: Check box clicked")
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_APP_SPLASH, ed_glob.ID_PREF_SPOS,
                    ed_glob.ID_PREF_CHKMOD, ed_glob.ID_SESSION,
                    ed_glob.ID_NEW_WINDOW, ed_glob.ID_PREF_CHKUPDATE]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
        elif e_id == ed_glob.ID_REPORTER:
            Profile_Set(ed_glob.ID_2_PROF[e_id], not e_obj.GetValue())
        else:
            pass
        evt.Skip()

    @staticmethod
    def OnChoice(evt):
        """Handles events from the choice controls
        @param evt: event that called this handler
        @note: Also handles the Language ComboBox

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id in [ed_glob.ID_PREF_MODE,
                    ed_glob.ID_PREF_FHIST,
                    ed_glob.ID_PREF_LANG]:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
            if e_id == ed_glob.ID_PREF_MODE:
                ed_glob.DEBUG = ('DEBUG' in e_obj.GetValue())
        elif e_id == ed_glob.ID_PRINT_MODE:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetSelection())
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

class DocumentPanel(wx.Panel):
    """Creates a panel with controls for Editra's editing settings
    @summary: Contains a wx.Notebook that contains a number of pages with
              setting controls for how documents are handled by the
              ed_stc.EditraStc text control.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Attributes
        self._DoLayout()
        self.SetAutoLayout(True)

    def _DoLayout(self):
        """Do the layout of the panel
        @note: Do not call this after __init__

        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        nbook = wx.Notebook(self)
        nbook.AddPage(DocGenPanel(nbook), _("General"))
        nbook.AddPage(DocCodePanel(nbook), _("Code"))
        nbook.AddPage(DocSyntaxPanel(nbook), _("Syntax Highlighting"))
        sizer.AddMany([((10, 10), 0), (nbook, 1, wx.EXPAND), ((10, 10), 0)])
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.AddMany([(sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

    def GetSize(self):
        """Get the size of the panel
        @return: wx.Size

        """
        sz = wx.Panel.GetSize(self)
        return wx.Size(sz[0] + 35, sz[1])

class DocGenPanel(wx.Panel):
    """Panel used for general document settings in the DocumentPanel's
    notebook.
    @summary: Panel with controls for setting the general attributes of
              how a document is managed.

    """
    ID_FONT_PICKER = wx.NewId()
    ID_FONT_PICKER2 = wx.NewId()

    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnUpdateEditor)
        self.Bind(wx.EVT_CHOICE, self.OnUpdateEditor)
        self.Bind(ed_event.EVT_NOTIFY, self.OnFontChange)

    def __DoLayout(self):
        """Layout the controls
        @note: Do not call this after __init__

        """
        # Format Section
        tabsz = wx.BoxSizer(wx.HORIZONTAL)
        tabsz.AddMany([(wx.StaticText(self, label=_("Tab Width") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                       (ExChoice(self, ed_glob.ID_PREF_TABW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=Profile_Get('TABWIDTH', 'str')), 0,
                        wx.ALIGN_CENTER_VERTICAL)])

        indentsz = wx.BoxSizer(wx.HORIZONTAL)
        indentsz.AddMany([(wx.StaticText(self, label=_("Indent Width") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                       (ExChoice(self, ed_glob.ID_PREF_INDENTW,
                          choices=['2','3','4','5','6','7','8','9','10'],
                          default=Profile_Get('INDENTWIDTH', 'str')), 0,
                        wx.ALIGN_CENTER_VERTICAL)])

        ut_cb = wx.CheckBox(self, ed_glob.ID_PREF_TABS,
                            _("Use Tabs Instead of Spaces"))
        ut_cb.SetValue(Profile_Get('USETABS', 'bool', False))
        bsu_cb = wx.CheckBox(self, ed_glob.ID_PREF_UNINDENT,
                             _("Backspace Unindents"))
        bsu_cb.SetValue(Profile_Get('BSUNINDENT', 'bool', True))
        eolsz = wx.BoxSizer(wx.HORIZONTAL)
        eolsz.AddMany([(wx.StaticText(self,
                        label=_("Default EOL Mode") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                       (ExChoice(self, ed_glob.ID_EOL_MODE,
                                 choices=[_("Macintosh (\\r)"), _("Unix (\\n)"),
                                          _("Windows (\\r\\n)")],
                                 default=Profile_Get('EOL')),
                        0, wx.ALIGN_CENTER_VERTICAL)])

        # Encoding options
        d_encoding = Profile_Get('ENCODING',
                                  default=locale.getpreferredencoding())
        d_encoding = encodings.normalize_encoding(d_encoding)
        enc_ch = ExChoice(self, ed_glob.ID_PREF_ENCODING,
                          choices=util.GetAllEncodings(),
                          default=d_encoding)
        enc_ch.SetToolTipString(_("Encoding to try when auto detection fails"))

        # View Options
        aa_cb = wx.CheckBox(self, ed_glob.ID_PREF_AALIAS, _("AntiAliasing"))
        aa_cb.SetValue(Profile_Get('AALIASING'))
        seol_cb = wx.CheckBox(self, ed_glob.ID_SHOW_EOL, _("Show EOL Markers"))
        seol_cb.SetValue(Profile_Get('SHOW_EOL'))
        sln_cb = wx.CheckBox(self, ed_glob.ID_SHOW_LN, _("Show Line Numbers"))
        sln_cb.SetValue(Profile_Get('SHOW_LN'))
        sws_cb = wx.CheckBox(self, ed_glob.ID_SHOW_WS, _("Show Whitespace"))
        sws_cb.SetValue(Profile_Get('SHOW_WS'))
        ww_cb = wx.CheckBox(self, ed_glob.ID_WORD_WRAP, _("Word Wrap"))
        ww_cb.SetValue(Profile_Get('WRAP'))
        ww_cb.SetToolTipString(_("Turn off for better performance"))

        # Font Options
        fnt = Profile_Get('FONT1', 'font', wx.Font(10, wx.FONTFAMILY_MODERN,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL))
        fpick = PyFontPicker(self, DocGenPanel.ID_FONT_PICKER, fnt)
        fpick.SetToolTipString(_("Sets the main/default font of the document"))
        fnt = Profile_Get('FONT2', 'font', wx.Font(10, wx.FONTFAMILY_SWISS,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL))
        fpick2 = PyFontPicker(self, DocGenPanel.ID_FONT_PICKER2, fnt)
        fpick2.SetToolTipString(_("Sets a secondary font used for special "
                                  "regions when syntax highlighting is in use"))

        # Layout
        sizer = wx.FlexGridSizer(20, 2, 5, 5)
        sizer.AddGrowableCol(1, 1)
        sizer.AddMany([((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Format") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), (ut_cb, 0),
                       ((5, 5), 0), (bsu_cb, 0),
                       ((5, 5), 0), (tabsz, 0),
                       ((5, 5), 0), (indentsz, 0),
                       ((5, 5), 0), (eolsz, 0),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Prefered Encoding") + u":"),
                        0), (enc_ch, 1),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("View Options") + u": "),
                        0), (aa_cb, 0),
                       ((5, 5), 0), (seol_cb, 0),
                       ((5, 5), 0), (sln_cb, 0),
                       ((5, 5), 0), (sws_cb, 0),
                       ((5, 5), 0), (ww_cb, 0),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Primary Font") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL),
                       (fpick, 1, wx.EXPAND),
                       (wx.StaticText(self, label=_("Secondary Font") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL),
                       (fpick2, 1, wx.EXPAND),
                       ((10, 10), 0), ((10, 10), 0)])
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((10, 10), 0), (sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

    @staticmethod
    def OnFontChange(evt):
        """Handles L{ed_event.EVT_NOTIFY} from the font controls"""
        e_id = evt.GetId()
        if e_id in [DocGenPanel.ID_FONT_PICKER, DocGenPanel.ID_FONT_PICKER2]:
            font = evt.GetValue()
            if not isinstance(font, wx.Font) or font.IsNull():
                return

            if e_id == DocGenPanel.ID_FONT_PICKER:
                Profile_Set('FONT1', font, 'font')
            else:
                Profile_Set('FONT2', font, 'font')

            for main in wx.GetApp().GetMainWindows():
                for stc in main.nb.GetTextControls():
                    stc.SetStyleFont(font, e_id == DocGenPanel.ID_FONT_PICKER)
                    stc.UpdateAllStyles()
        else:
            evt.Skip()

    @staticmethod
    def OnUpdateEditor(evt):
        """Update any open text controls to reflect the changes made in this
        panel from the checkboxes and choice controls.
        @param evt: Event that called this handler

        """
        # XXX Why when running on windows this and other imports randomly 
        #     become None. I have been unable to reproduce this behavior myself
        #     but have recieved enough error reports about it to beleive it.
        #     If they were actually NoneTypes the dialog would not be able to 
        #     be shown so this is very strange!!
        global ed_glob
        if ed_glob is None:
            import ed_glob

        e_id = evt.GetId()
        if e_id in [ed_glob.ID_PREF_TABS, ed_glob.ID_PREF_TABW,
                    ed_glob.ID_PREF_UNINDENT, ed_glob.ID_EOL_MODE,
                    ed_glob.ID_PREF_AALIAS, ed_glob.ID_SHOW_EOL,
                    ed_glob.ID_SHOW_LN, ed_glob.ID_SHOW_WS,
                    ed_glob.ID_WORD_WRAP, ed_glob.ID_PREF_AALIAS,
                    ed_glob.ID_PREF_INDENTW, ed_glob.ID_PREF_ENCODING]:
            Profile_Set(ed_glob.ID_2_PROF[e_id],
                        evt.GetEventObject().GetValue())

            # Do updates for everything but text encoding
            if e_id != ed_glob.ID_PREF_ENCODING:
                wx.CallLater(25, DoUpdates)
        else:
            evt.Skip()

class DocCodePanel(wx.Panel):
    """Panel used for programming settings
    @summary: Houses many of the controls for configuring the editors features
              that are related to programming.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CHOICE, self.OnCheck)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpin)

    def __DoLayout(self):
        """Layout the page
        @note: Do not call this after __init__

        """
        # General Section
        dlex_ch = ExChoice(self, ed_glob.ID_PREF_DLEXER,
                           choices=syntax.GetLexerList(),
                           default=Profile_Get('DEFAULT_LEX',
                                               default="Plain Text"))
        dlex_ch.SetToolTipString(_("Default highlighing for new documents"))
        dlex_sz = wx.BoxSizer(wx.HORIZONTAL)
        dlex_sz.AddMany([(wx.StaticText(self, label=_("Default Lexer") + u": "),
                          0, wx.ALIGN_CENTER_VERTICAL), ((3, 3),),
                          (dlex_ch, 0, wx.ALIGN_CENTER_VERTICAL)])

        # Visual Helpers Section
        vis_lbl = wx.StaticText(self, label=_("Visual Helpers") + u": ")
        br_cb = wx.CheckBox(self, ed_glob.ID_BRACKETHL,
                            _("Bracket Highlighting"))
        br_cb.SetValue(Profile_Get('BRACKETHL'))
        fold_cb = wx.CheckBox(self, ed_glob.ID_FOLDING, _("Code Folding"))
        fold_cb.SetValue(Profile_Get('CODE_FOLD'))
        edge_cb = wx.CheckBox(self, ed_glob.ID_SHOW_EDGE, _("Edge Guide"))
        edge_cb.SetValue(Profile_Get('SHOW_EDGE'))
        edge_sp = wx.SpinCtrl(self, ed_glob.ID_PREF_EDGE,
                              Profile_Get('EDGE', 'str'), min=0, max=120)
        edge_sp.SetToolTipString(_("Guide Column"))
        edge_col = wx.BoxSizer(wx.HORIZONTAL)
        edge_col.AddMany([(edge_cb, 0, wx.ALIGN_CENTER_VERTICAL),
                          ((10, 5), 0), (edge_sp, 0, wx.ALIGN_CENTER_VERTICAL)])
        hlcaret_cb = wx.CheckBox(self, ed_glob.ID_HLCARET_LINE,
                                 _("Highlight Caret Line"))
        hlcaret_cb.SetValue(Profile_Get("HLCARETLINE"))
        ind_cb = wx.CheckBox(self, ed_glob.ID_INDENT_GUIDES,
                             _("Indentation Guides"))
        ind_cb.SetValue(Profile_Get('GUIDES'))

        # Input Helpers
        comp_cb = wx.CheckBox(self, ed_glob.ID_AUTOCOMP, _("Auto-Completion"))
        comp_cb.SetValue(Profile_Get('AUTO_COMP'))
        ai_cb = wx.CheckBox(self, ed_glob.ID_AUTOINDENT, _("Auto-Indent"))
        ai_cb.SetValue(Profile_Get('AUTO_INDENT'))
        vi_cb = wx.CheckBox(self, ed_glob.ID_VI_MODE, _("Enable Vi Emulation"))
        vi_cb.SetValue(Profile_Get('VI_EMU'))

        # Layout the controls
        sizer = wx.FlexGridSizer(13, 2, 5, 5)
        sizer.AddMany([((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("General") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL), (dlex_sz, 0),
                       ((10, 10), 0), ((10, 10), 0),
                       (vis_lbl, 0), (br_cb, 0),
                       ((5, 5), 0), (fold_cb, 0),
                       ((5, 5), 0), (edge_col, 0, wx.ALIGN_CENTER_VERTICAL),
                       ((5, 5), 0), (hlcaret_cb, 0),
                       ((5, 5), 0), (ind_cb, 0),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Input Helpers") + u": "),
                        0), (comp_cb, 0),
                       ((5, 5), 0), (ai_cb, 0),
                       ((5, 5), 0), (vi_cb, 0),
                       ((10, 10), 0), ((10, 10), 0)])
        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((10, 10), 0), (sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

    @staticmethod
    def OnCheck(evt):
        """Handles the events from this panels check boxes
        @param evt: wx.CommandEvent

        """
        e_id = evt.GetId()
        if e_id in (ed_glob.ID_BRACKETHL, ed_glob.ID_SHOW_EDGE,
                    ed_glob.ID_INDENT_GUIDES, ed_glob.ID_FOLDING,
                    ed_glob.ID_AUTOCOMP, ed_glob.ID_AUTOINDENT,
                    ed_glob.ID_PREF_EDGE, ed_glob.ID_VI_MODE,
                    ed_glob.ID_PREF_DLEXER, ed_glob.ID_HLCARET_LINE):
            Profile_Set(ed_glob.ID_2_PROF[e_id],
                        evt.GetEventObject().GetValue())
            wx.CallLater(25, DoUpdates)
        else:
            evt.Skip()

    @staticmethod
    def OnSpin(evt):
        """Catch actions from a slider
        @param evt: wx.SpinEvent

        """
        e_id = evt.GetId()
        if e_id == ed_glob.ID_PREF_EDGE:
            val = evt.GetEventObject().GetValue()
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)

            for mainw in wx.GetApp().GetMainWindows():
                for stc in mainw.nb.GetTextControls():
                    stc.SetEdgeColumn(val)
        else:
            evt.Skip()

class DocSyntaxPanel(wx.Panel):
    """Document syntax config panel
    @summary: Manages the configuration of the syntax highlighting
              of the documents in the editor.

    """
    def __init__(self, parent):
        """Inialize the config panel
        @param parent: parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Attributes
        self._elist = ExtListCtrl(self)
        self._elist.SetMinSize((425, 200))

        # Layout page
        self.__DoLayout()
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHECKBOX, self.OnSynChange)
        self.Bind(wx.EVT_CHOICE, self.OnSynChange)

    def __DoLayout(self):
        """Layout all the controls
        @note: Do not call this after __init__

        """
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Syntax Settings
        syn_cb = wx.CheckBox(self, ed_glob.ID_SYNTAX, _("Syntax Highlighting"))
        syn_cb.SetValue(Profile_Get('SYNTAX'))
        syntheme = ExChoice(self, ed_glob.ID_PREF_SYNTHEME,
                            choices=util.GetResourceFiles(u'styles',
                                                          get_all=True),
                            default=Profile_Get('SYNTHEME', 'str'))
        line = wx.StaticLine(self, size=(-1, 2))
        lsizer = wx.BoxSizer(wx.VERTICAL)
        lsizer.Add(line, 0, wx.EXPAND)
        lst_lbl = wx.StaticText(self, label=_("Filetype Associations") + u": ")

        # Layout the controls
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([(syn_cb, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                        ((5, 5), 1, wx.EXPAND),
                        (wx.StaticText(self, label=_("Color Scheme") + u": "),
                        0, wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL),
                        (syntheme, 0, wx.EXPAND), ((5, 5), 0)])

        sizer.AddMany([((15, 15), 0), (hsizer, 0, wx.EXPAND),
                       ((5, 5), 0), (lsizer, 0, wx.EXPAND),
                       ((15, 15), 0), (lst_lbl, 0, wx.ALIGN_LEFT)])

        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.AddMany([((5, 5), 0), (self._elist, 1, wx.EXPAND), ((5, 5), 0)])

        default_btn = wx.Button(self, wx.ID_DEFAULT, _("Revert to Default"))
        if wx.Platform == '__WXMAC__':
            default_btn.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)
        sizer.AddMany([((10, 10), 0), (hsizer2, 1, wx.EXPAND), ((15, 15), 0),
                       (default_btn, 0, wx.ALIGN_LEFT), ((10, 10), 0)])

        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((5, 5), 0), (sizer, 1, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(msizer)

    def OnButton(self, evt):
        """Reset button handler
        @param evt: Event that called this handler

        """
        if evt.GetId() == wx.ID_DEFAULT:
            syntax.ExtensionRegister().LoadDefault()
            self._elist.UpdateExtensions()
        else:
            evt.Skip()

    @staticmethod
    def OnSynChange(evt):
        """Handles the events from checkbox and choice control for this panel
        @param evt: event that called this handler
        @postcondition: all text controls are updated to reflect the changes
                        made in these controls.

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id == ed_glob.ID_PREF_SYNTHEME:
            Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())

            for mainw in wx.GetApp().GetMainWindows():
                mainw.nb.UpdateTextControls('UpdateAllStyles')

        elif e_id == ed_glob.ID_SYNTAX:
            val = e_obj.GetValue()
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)

            for mainw in wx.GetApp().GetMainWindows():
                mainw.nb.UpdateTextControls('SyntaxOnOff', [val])

        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

class AppearancePanel(wx.Panel):
    """Creates a panel with controls for Editra's appearance settings
    @summary: contains all the controls for configuring the appearance
              related settings in Editra.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Layout
        self._DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_SLIDER, self.OnSetTransparent, \
                  id=ed_glob.ID_TRANSPARENCY)
        self.Bind(ed_event.EVT_NOTIFY, self.OnFontChange)

    def _DoLayout(self):
        """Add and layout the widgets
        @note: Do not call this after __init__

        """
        # Icons Section
        from ed_theme import BitmapProvider
        icons = ['Default']
        icons.extend(BitmapProvider(wx.GetApp().GetPluginManager()).GetThemes())
        iconsz = wx.BoxSizer(wx.HORIZONTAL)
        iconsz.AddMany([(wx.StaticText(self, label=_("Icon Theme") + u": "), 0,
                         wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                       (ExChoice(self, ed_glob.ID_PREF_ICON, icons,
                                 Profile_Get('ICONS', 'str').title()), 0)])
        tbiconsz = wx.BoxSizer(wx.HORIZONTAL)
        tbiconsz.AddMany([(wx.StaticText(self, label=_("Toolbar Icon Size") + u": "),
                           0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                           (ExChoice(self, ed_glob.ID_PREF_ICONSZ,
                                     ['16', '24', '32'],
                             str(Profile_Get('ICON_SZ', 'size_tuple')[0])), 0)])
        tabicon_cb = wx.CheckBox(self, ed_glob.ID_PREF_TABICON,
                                 _("Show Icons on Tabs"))
        tabicon_cb.SetValue(Profile_Get('TABICONS'))

        # Layout Section
        mainw = wx.GetApp().GetActiveWindow()
        if mainw is not None:
            pchoices = mainw.GetPerspectiveList()
        else:
            pchoices = list()
        perspec_sz = wx.BoxSizer(wx.HORIZONTAL)
        perspec_sz.AddMany([(wx.StaticText(self,
                             label=_("Default Perspective") + u": "),
                             0, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                            (ExChoice(self, ed_glob.ID_PERSPECTIVES,
                               pchoices, Profile_Get('DEFAULT_VIEW')), 0)])
        ws_cb = wx.CheckBox(self, ed_glob.ID_PREF_WSIZE, \
                            _("Remember Window Size on Exit"))
        ws_cb.SetValue(Profile_Get('SET_WSIZE'))
        wp_cb = wx.CheckBox(self, ed_glob.ID_PREF_WPOS, \
                            _("Remember Window Position on Exit"))
        wp_cb.SetValue(Profile_Get('SET_WPOS'))
        sb_cb = wx.CheckBox(self, ed_glob.ID_SHOW_SB, _("Show Status Bar"))
        sb_cb.SetValue(Profile_Get('STATBAR'))
        tb_cb = wx.CheckBox(self, ed_glob.ID_VIEW_TOOL, _("Show Toolbar"))
        tb_cb.SetValue(Profile_Get('TOOLBAR'))

        # Font
        fnt = Profile_Get('FONT3', 'font', wx.NORMAL_FONT)
        fpick = PyFontPicker(self, wx.ID_ANY, fnt)
        fpick.SetToolTipString(_("Main display font for various UI components"))

        # Misc
        trans_size = (-1, -1)
        if wx.Platform == '__WXGTK__':
            trans_size = (200, 15)

        # Layout
        sizer = wx.FlexGridSizer(16, 2, 5, 5)
        sizer.AddMany([((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Icons") + u": "), 0,
                        wx.ALIGN_CENTER_VERTICAL), (iconsz, 0),
                       ((5, 5), 0), (tbiconsz, 0),
                       ((5, 5), 0), (tabicon_cb, 0),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Layout") + u": "), 0,
                        wx.ALIGN_CENTER_VERTICAL),
                        (perspec_sz, 0, wx.ALIGN_CENTER_VERTICAL),
                       ((5, 5), 0), (ws_cb, 0),
                       ((5, 5), 0), (wp_cb, 0),
                       ((5, 5), 0), (sb_cb, 0),
                       ((5, 5), 0), (tb_cb, 0),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Transparency") + u": "), 0),
                       (wx.Slider(self, ed_glob.ID_TRANSPARENCY,
                                   Profile_Get('ALPHA'), 100, 255,
                                   size=trans_size, style=wx.SL_HORIZONTAL | \
                                   wx.SL_AUTOTICKS | wx.SL_LABELS), 0, wx.EXPAND),
                       ((10, 10), 0), ((10, 10), 0),
                       (wx.StaticText(self, label=_("Display Font") + u": "),
                        0, wx.ALIGN_CENTER_VERTICAL),
                       (fpick, 1, wx.EXPAND),
                       ((10, 10), 0), ((10, 10), 0),
                       ])

        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((10, 10), 0), (sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

    @staticmethod
    def OnCheck(evt):
        """Updates profile based on checkbox actions
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        evalue = evt.GetEventObject().GetValue()
        if e_id in (ed_glob.ID_PREF_WPOS, ed_glob.ID_PREF_WSIZE):
            Profile_Set(ed_glob.ID_2_PROF[e_id], evalue)
        elif e_id == ed_glob.ID_PREF_TABICON:
            Profile_Set(ed_glob.ID_2_PROF[e_id], evalue)
            ed_msg.PostMessage(ed_msg.EDMSG_THEME_NOTEBOOK)
        elif e_id in (ed_glob.ID_SHOW_SB, ed_glob.ID_VIEW_TOOL):
            Profile_Set(ed_glob.ID_2_PROF[e_id], evalue)
            if e_id == ed_glob.ID_SHOW_SB:
                fun = 'GetStatusBar'
            else:
                fun = 'GetToolBar'

            # Update Window(s)
            for mainw in wx.GetApp().GetMainWindows():
                getattr(mainw, fun)().Show(evalue)
                mainw.SendSizeEvent()
        else:
            evt.Skip()

    @staticmethod
    def OnChoice(evt):
        """Handles selection events from the choice controls
        @param evt: Event that called this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        val = e_obj.GetValue()
        if e_id in [ed_glob.ID_PREF_ICON, ed_glob.ID_PREF_ICONSZ]:
            if e_id == ed_glob.ID_PREF_ICONSZ:
                val = (int(val), int(val))
            Profile_Set(ed_glob.ID_2_PROF[e_id], val)
            wx.GetApp().ReloadArtProvider()
            ed_msg.PostMessage(ed_msg.EDMSG_THEME_CHANGED, True)
        elif e_id == ed_glob.ID_PERSPECTIVES:
            Profile_Set('DEFAULT_VIEW', val)
            for main_win in wx.GetApp().GetMainWindows():
                main_win.SetPerspective(Profile_Get('DEFAULT_VIEW'))
        else:
            evt.Skip()

    @staticmethod
    def OnFontChange(evt):
        """Send out update messages fo rdisplay font changes"""
        font = evt.GetValue()
        if isinstance(font, wx.Font) and not font.IsNull():
            Profile_Set('FONT3', font, 'font')
            ed_msg.PostMessage(ed_msg.EDMSG_DSP_FONT, font)

    @staticmethod
    def OnSetTransparent(evt):
        """Sets the transparency of the editor while the slider
        is being dragged.
        @param evt: Event that called this handler

        """
        if evt.GetId() == ed_glob.ID_TRANSPARENCY:
            value = evt.GetEventObject().GetValue()
            for window in wx.GetApp().GetOpenWindows().values():
                win = window[0]
                if hasattr(win, 'SetTransparent'):
                    win.SetTransparent(value)
            Profile_Set('ALPHA', value)
        else:
            evt.Skip()

#-----------------------------------------------------------------------------#

class NetworkPanel(wx.Panel):
    """Network related configration options"""
    def __init__(self, parent):
        """Create the panel"""
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()
        self.SetAutoLayout(True)

    def __DoLayout(self):
        """Do the layout of the panel
        @note: Do not call this after __init__

        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        nbook = wx.Notebook(self)
        nbook.AddPage(NetConfigPage(nbook), _("Configuration"))
        nbook.AddPage(UpdatePage(nbook), _("Update"))
        sizer.AddMany([((10, 10), 0), (nbook, 1, wx.EXPAND), ((10, 10), 0)])
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.AddMany([(sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

#-----------------------------------------------------------------------------#

ID_USE_PROXY = wx.NewId()
ID_URL = wx.NewId()
ID_PORT = wx.NewId()
ID_USERNAME = wx.NewId()
ID_PASSWORD = wx.NewId()

class NetConfigPage(wx.Panel):
    """Configuration page for network and proxy settings"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck, id=ID_USE_PROXY)
        self.Bind(wx.EVT_BUTTON, self.OnApply, id=wx.ID_APPLY)

    def __DoLayout(self):
        """Layout the controls in the panel"""
        msizer = wx.BoxSizer(wx.VERTICAL)

        sboxsz = wx.StaticBoxSizer(wx.StaticBox(self,
                                   label=_("Proxy Settings")), wx.VERTICAL)
        flexg = wx.FlexGridSizer(4, 2, 10, 5)
        flexg.AddGrowableCol(1, 1)

        proxy_val = Profile_Get('PROXY_SETTINGS', default=dict())
        use_proxy = wx.CheckBox(self, ID_USE_PROXY, _("Use Proxy"))
        use_proxy.SetValue(Profile_Get('USE_PROXY', 'bool', False))
        sboxsz.AddMany([(use_proxy, 0, wx.ALIGN_LEFT), ((10, 10), 0)])

        url_sz = wx.BoxSizer(wx.HORIZONTAL)
        url_lbl = wx.StaticText(self, label=_("Proxy URL") + u":")
        url_txt = wx.TextCtrl(self, ID_URL, proxy_val.get('url', ''))
        port_sep = wx.StaticText(self, label=":")
        port_txt = wx.TextCtrl(self, ID_PORT, proxy_val.get('port', ''))
        port_txt.SetToolTipString(_("Port Number"))
        url_sz.AddMany([(url_txt, 1, wx.EXPAND), ((2, 2)),
                        (port_sep, 0, wx.ALIGN_CENTER_VERTICAL),
                        ((2, 2)), (port_txt, 0, wx.ALIGN_CENTER_VERTICAL)])
        flexg.AddMany([(url_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                       (url_sz, 0, wx.EXPAND)])

        usr_sz = wx.BoxSizer(wx.HORIZONTAL)
        usr_lbl = wx.StaticText(self, label=_("Username") + u":")
        usr_txt = wx.TextCtrl(self, ID_USERNAME, proxy_val.get('uname', ''))
        usr_sz.Add(usr_txt, 1, wx.EXPAND)
        flexg.AddMany([(usr_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                       (usr_sz, 0, wx.EXPAND)])

        pass_sz = wx.BoxSizer(wx.HORIZONTAL)
        pass_lbl = wx.StaticText(self, label=_("Password") + u":")
        pass_txt = wx.TextCtrl(self, ID_PASSWORD,
                               ed_crypt.Decrypt(proxy_val.get('passwd', ''),
                                                proxy_val.get('pid', '')),
                               style=wx.TE_PASSWORD)
        pass_sz.Add(pass_txt, 1, wx.EXPAND)
        flexg.AddMany([(pass_lbl, 0, wx.ALIGN_CENTER_VERTICAL),
                       (pass_sz, 0, wx.EXPAND), ((5, 5), 0)])

        apply_b = wx.Button(self, wx.ID_APPLY)
        flexg.Add(apply_b, 0, wx.ALIGN_RIGHT)

        if wx.Platform == '__WXMAC__':
            for lbl in (use_proxy, url_txt, port_sep, port_txt, url_lbl,
                        usr_lbl, usr_txt, pass_lbl, pass_txt, apply_b):
                lbl.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        self.EnableControls(use_proxy.GetValue())
        sboxsz.Add(flexg, 1, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((5, 5)), (sboxsz, 1, wx.EXPAND), ((5, 5))])
        msizer.AddMany([((10, 10)), (hsizer, 1, wx.EXPAND), ((10, 10))])
        self.SetSizer(msizer)

    def OnApply(self, evt):
        """Apply the changes to the proxy settings
        @param evt: wx.EVT_BUTTON

        """
        if evt.GetId() == wx.ID_APPLY:
            key_map = { ID_USERNAME : 'uname', ID_URL : 'url',
                        ID_PORT : 'port', ID_PASSWORD : 'passwd' }
            proxy_dict = dict(uname='', passwd='', url='', port='')
            for val in (ID_URL, ID_PORT, ID_USERNAME, ID_PASSWORD):
                win = self.FindWindowById(val)
                if win is not None:
                    winval = win.GetValue()
                    if val == ID_PASSWORD:
                        # This is not the most secure method of saving a
                        # sensitive data but it is definitely better than plain
                        # text. ALso as to be able to obtain this info from the
                        # user profile the intruder would already have had to
                        # compromise the users system account making anymore
                        # such security rather moot by this point anyway.
                        pid = os.urandom(8)
                        winval = ed_crypt.Encrypt(winval, pid)
                        proxy_dict['pid'] = pid
                    proxy_dict[key_map[val]] = winval

            Profile_Set('PROXY_SETTINGS', proxy_dict)
        else:
            evt.Skip()

    def EnableControls(self, enable=True):
        """Enable the controls in the box or disable them
        @keyword enable: Enable or Disable

        """
        for child in self.GetChildren():
            if isinstance(child, wx.StaticText) or \
               isinstance(child, wx.TextCtrl) or \
               isinstance(child, wx.Button):
                child.Enable(enable)

    def OnCheck(self, evt):
        """Enable the use of the proxy settings or not
        @param evt: wx.EVT_CHECKBOX

        """
        e_val = evt.GetEventObject().GetValue()
        Profile_Set('USE_PROXY', e_val)
        self.EnableControls(e_val)

#-----------------------------------------------------------------------------#

class UpdatePage(wx.Panel):
    """Creates a panel with controls for updating Editra
    @summary: Panel with controls to check and download updates for Editra

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(ed_event.EVT_UPDATE_TEXT, self.OnUpdateText)

    def __DoLayout(self):
        """Do the layout of the panel
        @note: Do not call this after __init__

        """
        # Status text and bar
        cur_box = wx.StaticBox(self, label=_("Installed Version"))
        cur_sz = wx.StaticBoxSizer(cur_box, wx.HORIZONTAL)
        cur_sz.SetMinSize(wx.Size(150, 40))
        cur_ver = wx.StaticText(self, wx.ID_ANY,  ed_glob.VERSION)
        cur_sz.Add(cur_ver, 0, wx.ALIGN_CENTER_HORIZONTAL)
        e_update = updater.UpdateProgress(self, ed_glob.ID_PREF_UPDATE_BAR)
        upd_box = wx.StaticBox(self, label=_("Latest Version"))
        upd_bsz = wx.StaticBoxSizer(upd_box, wx.HORIZONTAL)
        upd_bsz.SetMinSize(wx.Size(150, 40))
        upd_bsz.Add(wx.StaticText(self, ID_UPDATE_MSG, _(e_update.GetStatus())),
                    0, wx.ALIGN_CENTER_HORIZONTAL)
        upd_bsz.Layout()

        # Layout Controls
        statsz = wx.BoxSizer(wx.HORIZONTAL)
        statsz.AddMany([((15, 15), 0), (cur_sz, 0), ((20, 10), 1),
                        (upd_bsz, 0), ((15, 15), 0)])

        # Control buttons
        dl_b = wx.Button(self, ID_DOWNLOAD, _("Download"))
        dl_b.Disable()

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.AddStretchSpacer()
        bsizer.Add(wx.Button(self, ID_CHECK_UPDATE, _("Check")),
                   0, wx.ALIGN_LEFT)
        bsizer.AddStretchSpacer(2)
        bsizer.Add(dl_b, 0, wx.ALIGN_RIGHT)
        bsizer.AddStretchSpacer()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany([((15, 15), 1), (statsz, 0, wx.EXPAND), ((15, 15), 0),
                       (e_update, 0, wx.EXPAND), ((15, 15), 0),
                       (bsizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL),
                       ((15, 15), 1)])

        msizer = wx.BoxSizer(wx.HORIZONTAL)
        msizer.AddMany([((5, 5), 0), (sizer, 1, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(msizer)

    def OnButton(self, evt):
        """Handles events generated by the panels buttons
        @param evt: event that called this handler

        """
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        if e_id == ID_CHECK_UPDATE:
            util.Log("[prefdlg][evt] Update Page: Check Update Clicked")
            e_obj.Disable()
            prog_bar = self.FindWindowById(ed_glob.ID_PREF_UPDATE_BAR)
            # Note this function returns right away but its result is
            # handled on a separate thread. This window is then notified
            # via a custom event being posted by the control.
            prog_bar.CheckForUpdates()
        elif e_id == ID_DOWNLOAD:
            util.Log("[prefdlg][evt] Update Page: Download Updates Clicked")
            e_obj.Disable()
            self.FindWindowById(ID_CHECK_UPDATE).Disable()
            dl_dlg = updater.DownloadDialog(None, ed_glob.ID_DOWNLOAD_DLG,
                                            _("Downloading Update"))
            dp_sz = wx.GetDisplaySize()
            dl_dlg.SetPosition(((dp_sz[0] - (dl_dlg.GetSize()[0] + 5)), 25))
            dl_dlg.Show()
        else:
            evt.Skip()

    def OnUpdateText(self, evt):
        """Handles text update events"""
        util.Log("[prefdlg][evt] Update Page: Updating version status text")
        upd = self.FindWindowById(ed_glob.ID_PREF_UPDATE_BAR)
        if evt.GetId() == upd.ID_CHECKING:
            self.FindWindowById(ID_UPDATE_MSG).SetLabel(upd.GetStatus())
            if upd.GetUpdatesAvailable():
                self.FindWindowById(ID_DOWNLOAD).Enable()
            self.FindWindowById(ID_CHECK_UPDATE).Enable()
        self.Layout()

        # Trick the notebook into resizing to ensure everything fits
        curr_pg = self.GetParent().GetSelection()
        nbevt = wx.NotebookEvent(wx.wxEVT_COMMAND_TOOLBOOK_PAGE_CHANGED,
                                 0, curr_pg, curr_pg)
        wx.PostEvent(self.GetParent(), nbevt)
        self.Refresh()

#-----------------------------------------------------------------------------#
# Advanced Page

class AdvancedPanel(wx.Panel):
    """Creates a panel for holding advanced configuration options
    @summary: Contains a wx.Notebook that contains a number of pages with
              setting controls for configuring the advanced configuration
              options.

    """
    def __init__(self, parent):
        """Create the panel
        @param parent: Parent window of this panel

        """
        wx.Panel.__init__(self, parent)

        # Layout
        self.__DoLayout()
        self.SetAutoLayout(True)

    def __DoLayout(self):
        """Do the layout of the panel
        @note: Do not call this after __init__

        """
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        nbook = wx.Notebook(self)
        nbook.AddPage(KeyBindingPanel(nbook), _("Keybindings"))
        sizer.AddMany([((10, 10), 0), (nbook, 1, wx.EXPAND), ((10, 10), 0)])
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.AddMany([(sizer, 1, wx.EXPAND), ((10, 10), 0)])
        self.SetSizer(msizer)

#-----------------------------------------------------------------------------#
# Keybinding Panel

ID_MENUS = wx.NewId()
ID_MENU_ITEMS = wx.NewId()
ID_MOD1 = wx.NewId()
ID_MOD2 = wx.NewId()
ID_KEYS = wx.NewId()
ID_BINDING = wx.NewId()
KEYS = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '+', 'Left',
        'Right', 'Down', 'Up', 'Home', 'End', 'Tab']
KEYS.extend(["F" + str(x) for x in range(1, 13)])

if wx.Platform == '__WXMSW__':
    KEYS.remove('Tab')
KEYS.sort()

MODIFIERS = ['', 'Alt', 'Shift']
if wx.Platform == '__WXMAC__':
    MODIFIERS.append('Cmd')
else:
    MODIFIERS.append('Ctrl')
MODIFIERS.sort()

class KeyBindingPanel(wx.Panel):
    """Keybinding configration options"""
    def __init__(self, parent):
        """Create the panel"""
        wx.Panel.__init__(self, parent)

        # Attributes
        self.menub = wx.GetApp().GetActiveWindow().GetMenuBar()
        self.binder = self.menub.GetKeyBinder()
        self.menumap = dict()

        # Load the Menu Map
        def _tupSort(tup1, tup2):
            """Method for sorting the menu tuples"""
            if tup1[1] > tup2[1]:
                return 1
            elif tup1[1] < tup2[1]:
                return -1
            else:
                return 0
        for item in self.menub.GetMenuMap():
            for key, val in item.iteritems():
                if isinstance(val[0], int):
                    val = val[1:]
                self.menumap[key] = sorted(val, _tupSort)

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox)

    def __DoLayout(self):
        """Layout the controls"""
        msizer = wx.BoxSizer(wx.VERTICAL) # Main Sizer
        spacer = ((5, 5), 0)

        # Key profile section
        profsz = wx.BoxSizer(wx.HORIZONTAL)
        kprofiles = self.binder.GetKeyProfiles()
        # Add an empty selection for the default profile
        if len(kprofiles):
            kprofiles.insert(0, '')
        cprofile = Profile_Get('KEY_PROFILE', default=None)
        profiles = wx.Choice(self, ed_glob.ID_KEY_PROFILES, choices=kprofiles)
        profiles.Enable(len(kprofiles))
        if cprofile is None:
            profiles.SetStringSelection('')
        else:
            profiles.SetStringSelection(cprofile)
        profsz.AddMany([spacer,
                        (wx.StaticText(self, label=_("Key Profile") + u":"),
                         0, wx.ALIGN_CENTER_VERTICAL), spacer,
                        (profiles, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL),
                        spacer, (wx.Button(self, wx.ID_NEW, _("New")), 0),
                        spacer, (wx.Button(self, wx.ID_DELETE, _("Delete")), 0),
                        spacer])

        # Left Side Sizer
        lvsizer = wx.BoxSizer(wx.VERTICAL)
        menus = wx.Choice(self, ID_MENUS, choices=sorted(self.menumap.keys()))
        menus.SetSelection(0)
        milbls = [ item[1]
                    for item in self.menumap.get(menus.GetStringSelection()) ]
        lvsizer.AddMany([(wx.StaticText(self, label=_("Menu") + u":"),
                          0, wx.ALIGN_LEFT), spacer,
                         (menus, 0, wx.ALIGN_LEFT|wx.EXPAND), spacer,
                         (wx.ListBox(self, ID_MENU_ITEMS,
                                     choices=sorted(milbls),
                                     style=wx.SIMPLE_BORDER), 1, wx.EXPAND),
                         spacer])

        # Right Side Sizer
        rvsizer = wx.BoxSizer(wx.VERTICAL)
        rvsizer.AddMany([(wx.StaticText(self, label=_("Modifier 1") + u":"),
                          0, wx.ALIGN_LEFT), spacer,
                         (wx.Choice(self, ID_MOD1, choices=MODIFIERS),
                          0, wx.ALIGN_LEFT|wx.EXPAND), spacer,
                         (wx.StaticText(self, label=_("Modifier 2") + u":"),
                          0, wx.ALIGN_LEFT), spacer,
                         (wx.Choice(self, ID_MOD2, choices=[]),
                          0, wx.ALIGN_LEFT|wx.EXPAND), spacer,
                         (wx.StaticText(self, label=_("Key") + u":"),
                          0, wx.ALIGN_LEFT), spacer,
                         (wx.Choice(self, ID_KEYS, choices=KEYS),
                          0, wx.ALIGN_LEFT|wx.EXPAND), spacer,
                         (wx.StaticText(self, label=_("Binding") + u":"),
                          0, wx.ALIGN_LEFT), spacer,
                         (wx.StaticText(self, ID_BINDING, ""),
                          0, wx.ALIGN_LEFT),
                         # Reserve size for widest string
                         ((self.GetTextExtent('Ctrl+Shift+Right')[0], 1), 0),
                        ])

        # Lower Section
        lmsizer = wx.BoxSizer(wx.HORIZONTAL)
        lmsizer.AddMany([spacer, (lvsizer, 1, wx.EXPAND), ((10, 10), 0),
                         (rvsizer, 0, wx.EXPAND), spacer])

        # Main Layout
        line_sz = wx.BoxSizer(wx.HORIZONTAL)
        line_sz.AddMany([(5, 1),
                         (wx.StaticLine(self, size=(-1, 1)), 1, wx.EXPAND),
                         (5, 1)])
        line_sz2 = wx.BoxSizer(wx.HORIZONTAL)
        line_sz2.AddMany([(5, 1),
                         (wx.StaticLine(self, size=(-1, 1)), 1, wx.EXPAND),
                         (5, 1)])
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.AddMany([spacer, (wx.Button(self, wx.ID_REVERT,
                        _("Revert to Default")), 0, wx.ALIGN_LEFT),
                        ((-1, 5), 1, wx.EXPAND),
                        (wx.Button(self, wx.ID_APPLY, _("Apply")),
                        0, wx.ALIGN_RIGHT), spacer])
        msizer.AddMany([((10, 10), 0), (profsz, 0, wx.EXPAND), spacer,
                        (line_sz, 0, wx.EXPAND), spacer,
                        (lmsizer, 1, wx.EXPAND), ((10, 10), 0),
                        (line_sz2, 0, wx.EXPAND), spacer,
                        (bsizer, 0, wx.EXPAND), spacer])

        # Use the small buttons on mac
        if wx.Platform == '__WXMAC__':
            for item in (wx.ID_REVERT, wx.ID_APPLY):
                self.FindWindowById(item).SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        self.SetSizer(msizer)
        self.SetAutoLayout(True)

        # Setup control status
        self.ClearKeyView()
        self.EnableControls(len(profiles.GetStringSelection()))

    def _GetMenuId(self):
        """Get the id of the currently selected menu item
        @return: int or None

        """
        sel_idx = self.FindWindowById(ID_MENU_ITEMS).GetSelection()
        cmenu = self.FindWindowById(ID_MENUS).GetStringSelection()
        menu_id = self.menumap.get(cmenu)[sel_idx][0]
        return menu_id

    def _UpdateBinding(self):
        """Update the current keybinding and its display"""
        binding = self.FindWindowById(ID_BINDING) # StaticText
        bvalue = self.GetBindingValue()
        bstr = u"+".join(bvalue)
        if not len(bstr):
            bstr = _("None")
        binding.SetLabel(bstr)

    def _UpdateKeyDisplay(self, keys):
        """Update the controls that show the key binding of the current
        menu item.
        @param keys: tuple of keys

        """
        mod1 = self.FindWindowById(ID_MOD1) # Choice
        mod1.SetItems(MODIFIERS)
        mod2 = self.FindWindowById(ID_MOD2) # Choice
        mod2.Enable()
        key = self.FindWindowById(ID_KEYS) # Choice

        if keys is None:
            keys = ('')

        # Change the main meta key for display reasons to keep it from
        # being confused with the actual ctrl key since wx translates ctrl
        # to apple key (cmd) automatically.
        if wx.Platform == '__WXMAC__' and len(keys) and 'Ctrl' in keys:
            nkeys = list()
            for keystr in keys:
                if keystr == 'Ctrl':
                    nkeys.append('Cmd')
                else:
                    nkeys.append(keystr)
            keys = nkeys

        if len(keys) >= 3:
            mod1.SetStringSelection(keys[0])
            tmods = list(MODIFIERS)
            tmods.remove(keys[0])
            mod2.SetItems(tmods)
            mod2.SetStringSelection(keys[1])
            key.SetStringSelection(keys[2])
        elif len(keys) == 2:
            mod1.SetStringSelection(keys[0])
            tmods = list(MODIFIERS)
            tmods.remove(keys[0])
            mod2.SetItems(tmods)
            mod2.SetStringSelection('')
            key.SetStringSelection(keys[1])
        elif len(keys) == 1 and keys[0] in KEYS:
            self.ClearKeyView()
            key.SetStringSelection(keys[0])
        else:
            self.ClearKeyView()

        self._UpdateBinding()

    def ClearKeyView(self):
        """Clear all selections in the keybinding controls"""
        self.FindWindowById(ID_MOD1).SetStringSelection('')
        mod2 = self.FindWindowById(ID_MOD2) # Choice
        mod2.Clear()
        mod2.Disable()
        self.FindWindowById(ID_KEYS).SetStringSelection('')
        self._UpdateBinding()

    def EnableControls(self, enable=True):
        """Enable/Disable the controls for editing the keybinding settings
        @keyword enable: enable (True), disable (False)

        """
        for ctrl in (ID_MENUS, ID_MENU_ITEMS,
                     wx.ID_APPLY, wx.ID_REVERT, wx.ID_DELETE):
            self.FindWindowById(ctrl).Enable(enable)

        self.EnableKeyView(enable)

    def EnableKeyView(self, enable=True):
        """Enable/Disable the key view/edit controls
        @keyword enable: enable (True), disable (False)

        """
        for ctrl in (ID_MOD1, ID_MOD2, ID_KEYS, ID_BINDING):
            self.FindWindowById(ctrl).Enable(enable)

    def GetBindingValue(self):
        """Get the values of the keybindings selected in the choice controls
        @return: list

        """
        rval = list()
        for cid in (ID_MOD1, ID_MOD2, ID_KEYS):
            val = self.FindWindowById(cid).GetStringSelection()
            if len(val):
                rval.append(val)
        return rval

    def OnButton(self, evt):
        """Handle button events
        @param evt: wx.CommandEvent

        """
        e_id = evt.GetId()
        profiles = self.FindWindowById(ed_glob.ID_KEY_PROFILES)
        csel = profiles.GetStringSelection()
        if e_id == wx.ID_NEW:
            dlg = wx.TextEntryDialog(self, _("New Profile"),
                                     _("Enter the name of the new key profile"))
            dlg.ShowModal()
            val = dlg.GetValue()
            if len(val):
                choices = profiles.GetItems() + ['', val]
                profiles.SetItems(sorted(list(set(choices))))
                profiles.SetStringSelection(val)
                self.menub.NewKeyProfile(val)
            profiles.Enable(len(profiles.GetItems()))
            self.EnableControls(len(profiles.GetItems()))
        elif e_id == wx.ID_DELETE:
            val = profiles.GetStringSelection()
            if val:
                # Remove the selected profile
                items = profiles.GetItems()
                items.remove(val)
                self.menub.DeleteKeyProfile(val)
                if len(items) == 1 and items[0] == '':
                    items = list()

                profiles.SetItems(items)
                profiles.Enable(len(items))
                if len(items):
                    profiles.SetSelection(0)

            self.EnableControls(len(profiles.GetItems()))
            csel = profiles.GetStringSelection()
            if csel:
                Profile_Set('KEY_PROFILE', csel)
            else:
                Profile_Set('KEY_PROFILE', None) # Use defaults
            ed_msg.PostMessage(ed_msg.EDMSG_MENU_LOADPROFILE,
                               Profile_Get('KEY_PROFILE', default=None))
        elif e_id == wx.ID_REVERT:
            # Revert to the original settings
            Profile_Set('KEY_PROFILE', None)
            ed_msg.PostMessage(ed_msg.EDMSG_MENU_LOADPROFILE, None)
            self.menub.SaveKeyProfile()
            self.FindWindowById(ed_glob.ID_KEY_PROFILES).SetStringSelection('')
            self.EnableControls(False)
        elif e_id == wx.ID_APPLY:
            # Update the menu(s) to the new settings
            profiles = self.FindWindowById(ed_glob.ID_KEY_PROFILES)
            csel = profiles.GetStringSelection()
            if not len(csel):
                csel = None
            Profile_Set('KEY_PROFILE', csel)
            ed_msg.PostMessage(ed_msg.EDMSG_MENU_REBIND)
            self.menub.SaveKeyProfile()
        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handle selections in the choice controls
        @param evt: wx.CommandEvent

        """
        e_id = evt.GetId()
        csel = evt.GetEventObject().GetStringSelection()
        if e_id == ed_glob.ID_KEY_PROFILES:
            if not len(csel):
                csel = None
            self.binder.LoadKeyProfile(csel)
            Profile_Set('KEY_PROFILE', csel)
            ed_msg.PostMessage(ed_msg.EDMSG_MENU_REBIND)
            self.menub.SaveKeyProfile()
            self.EnableControls(csel is not None)
        elif e_id == ID_MENUS:
            mi_listbx = self.FindWindowById(ID_MENU_ITEMS)
            if mi_listbx is not None:
                mi_listbx.SetItems([item[1] for item in self.menumap.get(csel)])
            self.ClearKeyView()
        elif e_id == ID_MOD1:
            mod2 = self.FindWindowById(ID_MOD2)
            if not len(csel):
                mod2.Clear()
                mod2.Disable()
            else:
                mod2.Enable()
                tmods = list(MODIFIERS)
                tmods.remove(csel)
                mod2.SetItems(tmods)
                mod2.SetStringSelection('')
            self._UpdateBinding()
        elif e_id in [ID_MOD2, ID_KEYS]:
            self._UpdateBinding()
        else:
            evt.Skip()

        # Update the keybinding
        if e_id in (ID_MOD1, ID_MOD2, ID_KEYS):
            bval = u"+".join(self.GetBindingValue())
            bval = bval.replace('Cmd', 'Ctrl', 1)
            self.binder.SetBinding(self._GetMenuId(), bval)

    def OnListBox(self, evt):
        """Handle listbox selections and update binding display
        @param evt: wx.CommandEvent

        """
        if evt.GetId() == ID_MENU_ITEMS:
            sel_idx = evt.GetSelection()
            cmenu = self.FindWindowById(ID_MENUS).GetStringSelection()
            menu_id = self.menumap.get(cmenu)[sel_idx][0]
            keys = self.binder.GetRawBinding(menu_id)
            self._UpdateKeyDisplay(keys)
        else:
            evt.Skip()

#----------------------------------------------------------------------------#
class ExtListCtrl(wx.ListCtrl,
                  listmix.ListCtrlAutoWidthMixin,
                  listmix.TextEditMixin,
                  elistmix.ListRowHighlighter):
    """Class to manage the file extension associations
    @summary: Creates a list control for showing file type to file extension
              associations as well as providing an interface to editing these
              associations

    """
    FILE_COL = 0
    EXT_COL = 1
    def __init__(self, parent):
        """Initializes the Profile List Control
        @param parent: The parent window of this control

        """
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY,
                             wx.DefaultPosition, wx.DefaultSize,
                             style=wx.LC_REPORT | wx.LC_SORT_ASCENDING | \
                                   wx.LC_VRULES | wx.BORDER)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        elistmix.ListRowHighlighter.__init__(self)

        # Setup
        self.InsertColumn(ExtListCtrl.FILE_COL, _("Lexer"))
        self.InsertColumn(ExtListCtrl.EXT_COL, \
                          _("Extensions (space separated, no dots)"))
        self._extreg = syntax.ExtensionRegister()
        self._editing = None
        self.LoadList()
        listmix.TextEditMixin.__init__(self)

    def CloseEditor(self, evt=None):
        """Update list and extension register after edit window
        closes.
        @keyword evt: Action that triggered this function

        """
        listmix.TextEditMixin.CloseEditor(self, evt)
        def UpdateRegister(itempos):
            """Update the ExtensionRegister
            @param itempos: position of the item to base updates on

            """
            vals = self.GetItem(itempos[1], itempos[0]).GetText()
            ftype = self.GetItem(itempos[1], ExtListCtrl.FILE_COL).GetText()
            self._editing = None
            self._extreg.SetAssociation(ftype, vals)

        if self._editing != None:
            wx.CallAfter(UpdateRegister, self._editing)
        wx.CallAfter(self.UpdateExtensions)

    def LoadList(self):
        """Loads the list of filetypes to file extension mappings into the
        list control.
        @postcondition: The running configuration data that is kept by the
                        syntax manager that relates to file associations is
                        loaded into the list control in alphabetical order

        """
        for key in sorted(self._extreg.keys()):
            index = self.InsertStringItem(sys.maxint, key)
            self.SetStringItem(index, ExtListCtrl.FILE_COL, key)
            self.SetStringItem(index, ExtListCtrl.EXT_COL, \
                               u'  %s' % u' '.join(self._extreg[key]))

        self.SetColumnWidth(ExtListCtrl.FILE_COL, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(ExtListCtrl.EXT_COL, wx.LIST_AUTOSIZE)

    def OpenEditor(self, col, row):
        """Disable the editor for the first column
        @param col: Column to edit
        @param row: Row to edit

        """
        if col != self.FILE_COL:
            self._editing = (col, row)
            listmix.TextEditMixin.OpenEditor(self, col, row)

    def UpdateExtensions(self):
        """Updates the values in the EXT_COL to reflect changes
        in the ExtensionRegister.
        @postcondition: Any configuration changes made in the control are
                        set in the Extension register.
        @see: L{syntax.syntax.ExtensionRegister}

        """
        for row in xrange(self.GetItemCount()):
            ftype = self.GetItem(row, ExtListCtrl.FILE_COL).GetText()
            self.SetStringItem(row, ExtListCtrl.EXT_COL, \
                               u'  ' + u' '.join(self._extreg[ftype]))

#----------------------------------------------------------------------------#
class ExChoice(wx.Choice):
    """Class to extend wx.Choice to have the GetValue
    function. This allows the application function to remain
    uniform in its value retrieval from all objects. This also extends
    wx.Choice to have a default selected value on init.

    """
    def __init__(self, parent, cid=wx.ID_ANY, choices=list(), default=None):
        """Constructs a Choice Control
        @param parent: The parent window of this control

        """
        if len(choices) and isinstance(choices[0], int):
            for ind in range(len(choices)):
                choices[ind] = str(choices[ind])
        wx.Choice.__init__(self, parent, cid, choices=choices)
        if default != None and isinstance(default, basestring):
            self.SetStringSelection(default)
        elif default is not None:
            self.SetSelection(default)

    def GetValue(self):
        """Gets the Selected Value
        @return: the value of the currently selected item
        @rtype: string

        """
        val = self.GetStringSelection()
        if val.isalpha():
            val.lower()
        return val

class PyFontPicker(wx.Panel):
    """A slightly enhanced wx.FontPickerCtrl that displays the choosen font in
    the text control using the choosen font as well as the font's size using
    nicer formatting.

    """
    def __init__(self, parent, id_=wx.ID_ANY, default=wx.NullFont):
        """Initializes the PyFontPicker
        @param default: The font to initialize as selected in the control

        """
        wx.Panel.__init__(self, parent, id_, style=wx.NO_BORDER)

        # Attributes
        if default == wx.NullFont:
            self._font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
        else:
            self._font = default
        self._text = wx.TextCtrl(self, style=wx.TE_CENTER | wx.TE_READONLY)
        self._text.SetFont(default)
        self._text.SetValue(u"%s - %dpt" % (self._font.GetFaceName(), \
                                            self._font.GetPointSize()))
        self._button = wx.Button(self, label=_("Set Font") + u'...')

        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([(self._text, 1, wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                       (self._button, 0, wx.ALIGN_CENTER_VERTICAL)])
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, lambda evt: self.ShowFontDlg(), self._button)
        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.OnChange)

    def GetFontValue(self):
        """Gets the currently choosen font
        @return: wx.Font

        """
        return self._font

    def GetTextCtrl(self):
        """Gets the widgets text control
        @return: wx.TextCtrl

        """
        return self._text

    def OnChange(self, evt):
        """Updates the text control using our custom stylings after
        the font is changed.
        @param evt: The event that called this handler

        """
        font = evt.GetFont()
        if font.IsNull():
            return
        self._font = font
        self._text.Clear()
        self._text.SetFont(self._font)
        self._text.SetValue(u"%s - %dpt" % (font.GetFaceName(), \
                                            font.GetPointSize()))
        evt = ed_event.NotificationEvent(ed_event.edEVT_NOTIFY,
                                         self.GetId(), self._font, self)
        wx.PostEvent(self.GetParent(), evt)

    def SetButtonLabel(self, label):
        """Sets the buttons label"""
        self._button.SetLabel(label)
        self._button.Refresh()

    def SetToolTipString(self, tip):
        """Sets the tooltip of the window
        @param tip: string

        """
        self._text.SetToolTipString(tip)
        self._button.SetToolTipString(tip)
        wx.Panel.SetToolTipString(self, tip)

    def ShowFontDlg(self):
        """Opens the FontDialog and processes the result"""
        fdata = wx.FontData()
        fdata.SetInitialFont(self._font)
        fdlg = wx.FontDialog(self.GetParent(), fdata)
        fdlg.ShowModal()
        fdata = fdlg.GetFontData()
        fdlg.Destroy()
        wx.PostEvent(self, wx.FontPickerEvent(self, self.GetId(),
                                              fdata.GetChosenFont()))

#-----------------------------------------------------------------------------#
# Utility Functions

def GetPrintModeStrings():
    """Get the strings for describing the print modes
    @note: defined in a function so translations can take place at runtime
    @note: Order must be kept in sync with the PRINT_ vals in ed_glob

    """
    return [_('Black/White'),       # PRINT_BLACK_WHITE
            _('Colour/White'),      # PRINT_COLOR_WHITE
            _('Colour/Default'),    # PRINT_COLOR_DEF
            _('Inverse'),           # PRINT_INVERSE
            _('Normal')]            # PRINT_NORMAL

def DoUpdates():
    """Update all open text controls"""
    for mainw in wx.GetApp().GetMainWindows():
        mainw.nb.UpdateTextControls()
