/////////////////////////////////////////////////////////////////////////////
// Name:        _pywindows.i
// Purpose:     SWIG interface for wxPyWindow, and etc.  These classes support
//              overriding many of wxWindow's virtual methods in Python derived
//              classes.
//
// Author:      Robin Dunn
//
// Created:     2-June-1998
// RCS-ID:      $Id$
// Copyright:   (c) 2003 by Total Control Software
// Licence:     wxWindows license
/////////////////////////////////////////////////////////////////////////////

// Not a %module

%{
#ifdef __WXMSW__
#include <wx/msw/dc.h>
#endif
%}

//---------------------------------------------------------------------------
%newgroup

// TODO:  Redo these with SWIG directors?

// TODO:  Which (if any?) of these should be done also???
//      Destroy
//      DoCaptureMouse
//      DoClientToScreen
//      DoHitTest
//      DoMoveWindow
//      DoPopupMenu
//      DoReleaseMouse
//      DoScreenToClient
//      DoSetToolTip
//      Enable
//      Fit
//      GetCharHeight
//      GetCharWidth
//      GetClientAreaOrigin
//      GetDefaultItem
//      IsTopLevel
//      SetBackgroundColour
//      SetDefaultItem
//      SetFocus
//      SetFocusFromKbd
//      SetForegroundColour
//      SetSizeHints
//      SetVirtualSizeHints
//      Show
//
//      GetWindowSizeForVirtualSize
//      DoFreeze
//      DoThaw

//---------------------------------------------------------------------------

%{ // C++ version of Python aware wxWindow
class wxPyWindow : public wxWindow
{
    DECLARE_DYNAMIC_CLASS(wxPyWindow)
public:
    wxPyWindow() : wxWindow() {}
    wxPyWindow(wxWindow* parent, const wxWindowID id,
               const wxPoint& pos = wxDefaultPosition,
               const wxSize& size = wxDefaultSize,
               long style = 0,
               const wxString& name = wxPyPanelNameStr)
        : wxWindow(parent, id, pos, size, style, name) {}


    bool DoEraseBackground(wxDC* dc) {
#ifdef __WXMSW__
        return wxWindow::DoEraseBackground(((wxMSWDCImpl*)dc->GetImpl())->GetHDC());
#else
        dc->SetBackground(wxBrush(GetBackgroundColour()));
        dc->Clear();
        return true;
#endif
    }

    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetSize);
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetClientSize);
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetPosition);

    PYCALLBACK_4_VOID(wxWindow, DoMoveWindow, (int a, int b, int c, int d))    
    PYCALLBACK_5_VOID(wxWindow, DoSetSize, (int a, int b, int c, int d, int e))    
    PYCALLBACK_2_VOID(wxWindow, DoSetClientSize, (int a, int b))
    PYCALLBACK_2_VOID(wxWindow, DoSetVirtualSize, (int a, int b))

    PYCALLBACK_0_EXTRACT_CONST(wxWindow, wxSize, rval, DoGetVirtualSize)
    PYCALLBACK_0_EXTRACT_CONST(wxWindow, wxSize, rval, DoGetBestSize)

    PYCALLBACK_0_VOID(wxWindow, InitDialog)
    PYCALLBACK_0_EXTRACT(wxWindow, bool, rval = false, TransferDataFromWindow)
    PYCALLBACK_0_EXTRACT(wxWindow, bool, rval = false, TransferDataToWindow)
    PYCALLBACK_0_EXTRACT(wxWindow, bool, rval = false, Validate)

    PYCALLBACK_0_EXTRACT_CONST(wxWindow, bool, rval = false, AcceptsFocus)
    PYCALLBACK_0_EXTRACT_CONST(wxWindow, bool, rval = false, AcceptsFocusFromKeyboard)
    PYCALLBACK_0_EXTRACT_CONST(wxWindow, wxSize, rval, GetMaxSize)

    PYCALLBACK_1_VOID(wxWindow, AddChild, (wxWindowBase *a))
    PYCALLBACK_1_VOID(wxWindow, RemoveChild, (wxWindowBase *a))

    PYCALLBACK_0_EXTRACT_CONST(wxWindow, bool, rval = false, ShouldInheritColours)
    PYCALLBACK_0_EXTRACT(wxWindow, wxVisualAttributes, rval, GetDefaultAttributes)

    PYCALLBACK_0_EXTRACT(wxWindow, bool, rval = false, HasTransparentBackground)
    PYCALLBACK_0_VOID(wxWindow, OnInternalIdle)
 
    PYPRIVATE;
};

IMPLEMENT_DYNAMIC_CLASS(wxPyWindow, wxWindow);

IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyWindow, wxWindow, DoGetSize);
IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyWindow, wxWindow, DoGetClientSize);
IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyWindow, wxWindow, DoGetPosition);

%}

// And now the one for SWIG to see
MustHaveApp(wxPyWindow);
class wxPyWindow : public wxWindow
{
public:
    %pythonAppend wxPyWindow         "self._setOORInfo(self);" setCallbackInfo(PyWindow)
    %pythonAppend wxPyWindow()       ""

    wxPyWindow(wxWindow* parent, const wxWindowID id=-1,
               const wxPoint& pos = wxDefaultPosition,
               const wxSize& size = wxDefaultSize,
               long style = 0,
               const wxString& name = wxPyPanelNameStr);

    %RenameCtor(PrePyWindow, wxPyWindow());
    
    void _setCallbackInfo(PyObject* self, PyObject* _class);

    %pythoncode { SetBestSize = wx.Window.SetInitialSize }
    bool DoEraseBackground(wxDC* dc);
    
    void DoMoveWindow(int x, int y, int width, int height);
    void DoSetSize(int x, int y, int width, int height,
                   int sizeFlags = wxSIZE_AUTO);
    void DoSetClientSize(int width, int height);
    void DoSetVirtualSize( int x, int y );

    DocDeclA(
        void, DoGetSize( int *OUTPUT, int *OUTPUT ) const,
        "DoGetSize() -> (width, height)");
    DocDeclA(
        void, DoGetClientSize( int *OUTPUT, int *OUTPUT ) const,
        "DoGetClientSize() -> (width, height)");
    DocDeclA(
        void, DoGetPosition( int *OUTPUT, int *OUTPUT ) const,
        "DoGetPosition() -> (x,y)");

    wxSize DoGetVirtualSize() const;
    wxSize DoGetBestSize() const;

    void InitDialog();
    bool TransferDataToWindow();
    bool TransferDataFromWindow();
    bool Validate();

    bool AcceptsFocus() const;
    bool AcceptsFocusFromKeyboard() const;
    wxSize GetMaxSize() const;

    void AddChild(wxWindow* child);
    void RemoveChild(wxWindow* child);

    bool ShouldInheritColours() const;
    wxVisualAttributes GetDefaultAttributes();

    void OnInternalIdle();

    %MAKE_BASE_FUNC(PyWindow, DoMoveWindow);
    %MAKE_BASE_FUNC(PyWindow, DoSetSize);
    %MAKE_BASE_FUNC(PyWindow, DoSetClientSize);
    %MAKE_BASE_FUNC(PyWindow, DoSetVirtualSize);
    %MAKE_BASE_FUNC(PyWindow, DoGetSize);
    %MAKE_BASE_FUNC(PyWindow, DoGetClientSize);
    %MAKE_BASE_FUNC(PyWindow, DoGetPosition);
    %MAKE_BASE_FUNC(PyWindow, DoGetVirtualSize);
    %MAKE_BASE_FUNC(PyWindow, DoGetBestSize);
    %MAKE_BASE_FUNC(PyWindow, InitDialog);
    %MAKE_BASE_FUNC(PyWindow, TransferDataToWindow);
    %MAKE_BASE_FUNC(PyWindow, TransferDataFromWindow);
    %MAKE_BASE_FUNC(PyWindow, Validate);
    %MAKE_BASE_FUNC(PyWindow, AcceptsFocus);
    %MAKE_BASE_FUNC(PyWindow, AcceptsFocusFromKeyboard);
    %MAKE_BASE_FUNC(PyWindow, GetMaxSize);
    %MAKE_BASE_FUNC(PyWindow, AddChild);
    %MAKE_BASE_FUNC(PyWindow, RemoveChild);
    %MAKE_BASE_FUNC(PyWindow, ShouldInheritColours);
    %MAKE_BASE_FUNC(PyWindow, GetDefaultAttributes);
    %MAKE_BASE_FUNC(PyWindow, OnInternalIdle);
    
};

//---------------------------------------------------------------------------
// Do the same thing for wxControl

// ** See _pycontrol.i, it was moved there because of dependency on wxControl


//---------------------------------------------------------------------------
// and for wxPanel

%{ // C++ version of Python aware wxPanel
class wxPyPanel : public wxPanel
{
    DECLARE_DYNAMIC_CLASS(wxPyPanel)
public:
    wxPyPanel() : wxPanel() {}
    wxPyPanel(wxWindow* parent, const wxWindowID id,
               const wxPoint& pos = wxDefaultPosition,
               const wxSize& size = wxDefaultSize,
               long style = wxTAB_TRAVERSAL | wxNO_BORDER,
               const wxString& name = wxPyPanelNameStr)
        : wxPanel(parent, id, pos, size, style, name) {}

    bool DoEraseBackground(wxDC* dc) {
#ifdef __WXMSW__
        return wxWindow::DoEraseBackground(((wxMSWDCImpl*)dc->GetImpl())->GetHDC());
#else
        dc->SetBackground(wxBrush(GetBackgroundColour()));
        dc->Clear();
        return true;
#endif
    }
    
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetSize);
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetClientSize);
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetPosition);

    PYCALLBACK_4_VOID(wxPanel, DoMoveWindow, (int a, int b, int c, int d))    
    PYCALLBACK_5_VOID(wxPanel, DoSetSize, (int a, int b, int c, int d, int e))    
    PYCALLBACK_2_VOID(wxPanel, DoSetClientSize, (int a, int b))
    PYCALLBACK_2_VOID(wxPanel, DoSetVirtualSize, (int a, int b))

    PYCALLBACK_0_EXTRACT_CONST(wxPanel, wxSize, rval, DoGetVirtualSize)
    PYCALLBACK_0_EXTRACT_CONST(wxPanel, wxSize, rval, DoGetBestSize)

    PYCALLBACK_0_VOID(wxPanel, InitDialog)
    PYCALLBACK_0_EXTRACT(wxPanel, bool, rval = false, TransferDataFromWindow)
    PYCALLBACK_0_EXTRACT(wxPanel, bool, rval = false, TransferDataToWindow)
    PYCALLBACK_0_EXTRACT(wxPanel, bool, rval = false, Validate)

    PYCALLBACK_0_EXTRACT_CONST(wxPanel, bool, rval = false, AcceptsFocus)
    PYCALLBACK_0_EXTRACT_CONST(wxPanel, bool, rval = false, AcceptsFocusFromKeyboard)
    PYCALLBACK_0_EXTRACT_CONST(wxPanel, wxSize, rval, GetMaxSize)

    PYCALLBACK_1_VOID(wxPanel, AddChild, (wxWindowBase *a))
    PYCALLBACK_1_VOID(wxPanel, RemoveChild, (wxWindowBase *a))

    PYCALLBACK_0_EXTRACT_CONST(wxPanel, bool, rval = false, ShouldInheritColours)
    PYCALLBACK_0_EXTRACT(wxPanel, wxVisualAttributes, rval, GetDefaultAttributes)

    PYCALLBACK_0_EXTRACT(wxPanel, bool, rval = false, HasTransparentBackground)
    PYCALLBACK_0_VOID(wxPanel, OnInternalIdle)

    PYPRIVATE;
};

IMPLEMENT_DYNAMIC_CLASS(wxPyPanel, wxPanel);

IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyPanel, wxPanel, DoGetSize);
IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyPanel, wxPanel, DoGetClientSize);
IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyPanel, wxPanel, DoGetPosition);

%}

// And now the one for SWIG to see
MustHaveApp(wxPyPanel);
class wxPyPanel : public wxPanel
{
public:
    %pythonAppend wxPyPanel         "self._setOORInfo(self);" setCallbackInfo(PyPanel)
    %pythonAppend wxPyPanel()       ""

    wxPyPanel(wxWindow* parent, const wxWindowID id=-1,
               const wxPoint& pos = wxDefaultPosition,
               const wxSize& size = wxDefaultSize,
               long style = wxTAB_TRAVERSAL | wxNO_BORDER,
               const wxString& name = wxPyPanelNameStr);

    %RenameCtor(PrePyPanel,  wxPyPanel());

    void _setCallbackInfo(PyObject* self, PyObject* _class);

    %pythoncode { SetBestSize = wx.Window.SetInitialSize }
    bool DoEraseBackground(wxDC* dc);
    
    void DoMoveWindow(int x, int y, int width, int height);
    void DoSetSize(int x, int y, int width, int height,
                        int sizeFlags = wxSIZE_AUTO);
    void DoSetClientSize(int width, int height);
    void DoSetVirtualSize( int x, int y );

    DocDeclA(
        void, DoGetSize( int *OUTPUT, int *OUTPUT ) const,
        "DoGetSize() -> (width, height)");
    DocDeclA(
        void, DoGetClientSize( int *OUTPUT, int *OUTPUT ) const,
        "DoGetClientSize() -> (width, height)");
    DocDeclA(
        void, DoGetPosition( int *OUTPUT, int *OUTPUT ) const,
        "DoGetPosition() -> (x,y)");

    wxSize DoGetVirtualSize() const;
    wxSize DoGetBestSize() const;

    void InitDialog();
    bool TransferDataToWindow();
    bool TransferDataFromWindow();
    bool Validate();

    bool AcceptsFocus() const;
    bool AcceptsFocusFromKeyboard() const;
    wxSize GetMaxSize() const;

    void AddChild(wxWindow* child);
    void RemoveChild(wxWindow* child);

    bool ShouldInheritColours() const ;
    wxVisualAttributes GetDefaultAttributes();

    void OnInternalIdle();

    %MAKE_BASE_FUNC(PyPanel, DoMoveWindow);
    %MAKE_BASE_FUNC(PyPanel, DoSetSize);
    %MAKE_BASE_FUNC(PyPanel, DoSetClientSize);
    %MAKE_BASE_FUNC(PyPanel, DoSetVirtualSize);
    %MAKE_BASE_FUNC(PyPanel, DoGetSize);
    %MAKE_BASE_FUNC(PyPanel, DoGetClientSize);
    %MAKE_BASE_FUNC(PyPanel, DoGetPosition);
    %MAKE_BASE_FUNC(PyPanel, DoGetVirtualSize);
    %MAKE_BASE_FUNC(PyPanel, DoGetBestSize);
    %MAKE_BASE_FUNC(PyPanel, InitDialog);
    %MAKE_BASE_FUNC(PyPanel, TransferDataToWindow);
    %MAKE_BASE_FUNC(PyPanel, TransferDataFromWindow);
    %MAKE_BASE_FUNC(PyPanel, Validate);
    %MAKE_BASE_FUNC(PyPanel, AcceptsFocus);
    %MAKE_BASE_FUNC(PyPanel, AcceptsFocusFromKeyboard);
    %MAKE_BASE_FUNC(PyPanel, GetMaxSize);
    %MAKE_BASE_FUNC(PyPanel, AddChild);
    %MAKE_BASE_FUNC(PyPanel, RemoveChild);
    %MAKE_BASE_FUNC(PyPanel, ShouldInheritColours);
    %MAKE_BASE_FUNC(PyPanel, GetDefaultAttributes);
    %MAKE_BASE_FUNC(PyPanel, OnInternalIdle);
};

//---------------------------------------------------------------------------
// and for wxScrolledWindow

%{ // C++ version of Python aware wxScrolledWindow
class wxPyScrolledWindow : public wxScrolledWindow
{
    DECLARE_DYNAMIC_CLASS(wxPyScrolledWindow)
public:
    wxPyScrolledWindow() : wxScrolledWindow() {}
    wxPyScrolledWindow(wxWindow* parent, const wxWindowID id,
               const wxPoint& pos = wxDefaultPosition,
               const wxSize& size = wxDefaultSize,
               long style = wxHSCROLL | wxVSCROLL,
               const wxString& name = wxPyPanelNameStr)
        : wxScrolledWindow(parent, id, pos, size, style, name) {}

    bool DoEraseBackground(wxDC* dc) {
#ifdef __WXMSW__
        return wxWindow::DoEraseBackground(((wxMSWDCImpl*)dc->GetImpl())->GetHDC());
#else
        dc->SetBackground(wxBrush(GetBackgroundColour()));
        dc->Clear();
        return true;
#endif
    }

    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetSize);
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetClientSize);
    DEC_PYCALLBACK_VOID_INTPINTP_const(DoGetPosition);

    PYCALLBACK_4_VOID(wxScrolledWindow, DoMoveWindow, (int a, int b, int c, int d))    
    PYCALLBACK_5_VOID(wxScrolledWindow, DoSetSize, (int a, int b, int c, int d, int e))    
    PYCALLBACK_2_VOID(wxScrolledWindow, DoSetClientSize, (int a, int b))
    PYCALLBACK_2_VOID(wxScrolledWindow, DoSetVirtualSize, (int a, int b))

    PYCALLBACK_0_EXTRACT_CONST(wxScrolledWindow, wxSize, rval, DoGetVirtualSize)
    PYCALLBACK_0_EXTRACT_CONST(wxScrolledWindow, wxSize, rval, DoGetBestSize)

    PYCALLBACK_0_VOID(wxScrolledWindow, InitDialog)
    PYCALLBACK_0_EXTRACT(wxScrolledWindow, bool, rval = false, TransferDataFromWindow)
    PYCALLBACK_0_EXTRACT(wxScrolledWindow, bool, rval = false, TransferDataToWindow)
    PYCALLBACK_0_EXTRACT(wxScrolledWindow, bool, rval = false, Validate)

    PYCALLBACK_0_EXTRACT_CONST(wxScrolledWindow, bool, rval = false, AcceptsFocus)
    PYCALLBACK_0_EXTRACT_CONST(wxScrolledWindow, bool, rval = false, AcceptsFocusFromKeyboard)
    PYCALLBACK_0_EXTRACT_CONST(wxScrolledWindow, wxSize, rval, GetMaxSize)

    PYCALLBACK_1_VOID(wxScrolledWindow, AddChild, (wxWindowBase *a))
    PYCALLBACK_1_VOID(wxScrolledWindow, RemoveChild, (wxWindowBase *a))

    PYCALLBACK_0_EXTRACT_CONST(wxScrolledWindow, bool, rval = false, ShouldInheritColours)
    PYCALLBACK_0_EXTRACT(wxScrolledWindow, wxVisualAttributes, rval, GetDefaultAttributes)

    PYCALLBACK_0_EXTRACT(wxScrolledWindow, bool, rval = false, HasTransparentBackground)
    PYCALLBACK_0_VOID(wxScrolledWindow, OnInternalIdle)

    PYPRIVATE;
};

IMPLEMENT_DYNAMIC_CLASS(wxPyScrolledWindow, wxScrolledWindow);

IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyScrolledWindow, wxScrolledWindow, DoGetSize);
IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyScrolledWindow, wxScrolledWindow, DoGetClientSize);
IMP_PYCALLBACK_VOID_INTPINTP_const(wxPyScrolledWindow, wxScrolledWindow, DoGetPosition);

%}

// And now the one for SWIG to see
MustHaveApp(wxPyScrolledWindow);
class wxPyScrolledWindow : public wxScrolledWindow
{
public:
    %pythonAppend wxPyScrolledWindow         "self._setOORInfo(self);" setCallbackInfo(PyScrolledWindow)
    %pythonAppend wxPyScrolledWindow()       ""

    wxPyScrolledWindow(wxWindow* parent, const wxWindowID id=-1,
               const wxPoint& pos = wxDefaultPosition,
               const wxSize& size = wxDefaultSize,
               long style = wxHSCROLL | wxVSCROLL,
               const wxString& name = wxPyPanelNameStr);

    %RenameCtor(PrePyScrolledWindow,  wxPyScrolledWindow());

    void _setCallbackInfo(PyObject* self, PyObject* _class);

    %pythoncode { SetBestSize = wx.Window.SetInitialSize }
    bool DoEraseBackground(wxDC* dc);
    
    void DoMoveWindow(int x, int y, int width, int height);
    void DoSetSize(int x, int y, int width, int height,
                        int sizeFlags = wxSIZE_AUTO);
    void DoSetClientSize(int width, int height);
    void DoSetVirtualSize( int x, int y );

    DocDeclA(
        void, DoGetSize( int *OUTPUT, int *OUTPUT ) const,
        "DoGetSize() -> (width, height)");
    DocDeclA(
        void, DoGetClientSize( int *OUTPUT, int *OUTPUT ) const,
        "DoGetClientSize() -> (width, height)");
    DocDeclA(
        void, DoGetPosition( int *OUTPUT, int *OUTPUT ) const,
        "DoGetPosition() -> (x,y)");

    wxSize DoGetVirtualSize() const;
    wxSize DoGetBestSize() const;

    void InitDialog();
    bool TransferDataToWindow();
    bool TransferDataFromWindow();
    bool Validate();

    bool AcceptsFocus() const;
    bool AcceptsFocusFromKeyboard() const;
    wxSize GetMaxSize() const;

    void AddChild(wxWindow* child);
    void RemoveChild(wxWindow* child);

    bool ShouldInheritColours() const;
    wxVisualAttributes GetDefaultAttributes();

    void OnInternalIdle();

    %MAKE_BASE_FUNC(PyScrolledWindow, DoMoveWindow);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoSetSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoSetClientSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoSetVirtualSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoGetSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoGetClientSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoGetPosition);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoGetVirtualSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, DoGetBestSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, InitDialog);
    %MAKE_BASE_FUNC(PyScrolledWindow, TransferDataToWindow);
    %MAKE_BASE_FUNC(PyScrolledWindow, TransferDataFromWindow);
    %MAKE_BASE_FUNC(PyScrolledWindow, Validate);
    %MAKE_BASE_FUNC(PyScrolledWindow, AcceptsFocus);
    %MAKE_BASE_FUNC(PyScrolledWindow, AcceptsFocusFromKeyboard);
    %MAKE_BASE_FUNC(PyScrolledWindow, GetMaxSize);
    %MAKE_BASE_FUNC(PyScrolledWindow, AddChild);
    %MAKE_BASE_FUNC(PyScrolledWindow, RemoveChild);
    %MAKE_BASE_FUNC(PyScrolledWindow, ShouldInheritColours);
    %MAKE_BASE_FUNC(PyScrolledWindow, GetDefaultAttributes);
    %MAKE_BASE_FUNC(PyScrolledWindow, OnInternalIdle);

};


//---------------------------------------------------------------------------
//---------------------------------------------------------------------------
