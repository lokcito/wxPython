/////////////////////////////////////////////////////////////////////////////
// Name:        dcclient.h
// Purpose:     wxClientDC class
// Author:      Julian Smart
// Modified by:
// Created:     01/02/97
// RCS-ID:      $Id$
// Copyright:   (c) Julian Smart
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#ifndef _WX_DCCLIENT_H_
#define _WX_DCCLIENT_H_

// ----------------------------------------------------------------------------
// headers
// ----------------------------------------------------------------------------

#include "wx/dc.h"
#include "wx/msw/dc.h"
#include "wx/dcclient.h"
#include "wx/dynarray.h"

// ----------------------------------------------------------------------------
// array types
// ----------------------------------------------------------------------------

// this one if used by wxPaintDC only
struct WXDLLIMPEXP_FWD_CORE wxPaintDCInfo;

WX_DECLARE_EXPORTED_OBJARRAY(wxPaintDCInfo, wxArrayDCInfo);

// ----------------------------------------------------------------------------
// DC classes
// ----------------------------------------------------------------------------

class WXDLLIMPEXP_CORE wxWindowDCImpl : public wxMSWDCImpl
{
public:
    // default ctor
    wxWindowDCImpl( wxDC *owner );

    // Create a DC corresponding to the whole window
    wxWindowDCImpl( wxDC *owner, wxWindow *win );

    virtual void DoGetSize(int *width, int *height) const;

protected:
    // initialize the newly created DC
    void InitDC();

    DECLARE_CLASS(wxWindowDCImpl)
    wxDECLARE_NO_COPY_CLASS(wxWindowDCImpl);
};

class WXDLLIMPEXP_CORE wxClientDCImpl : public wxWindowDCImpl
{
public:
    // default ctor
    wxClientDCImpl( wxDC *owner );

    // Create a DC corresponding to the client area of the window
    wxClientDCImpl( wxDC *owner, wxWindow *win );

    virtual ~wxClientDCImpl();

    virtual void DoGetSize(int *width, int *height) const;

protected:
    void InitDC();

    DECLARE_CLASS(wxClientDCImpl)
    wxDECLARE_NO_COPY_CLASS(wxClientDCImpl);
};

class WXDLLIMPEXP_CORE wxPaintDCImpl : public wxClientDCImpl
{
public:
    wxPaintDCImpl( wxDC *owner );

    // Create a DC corresponding for painting the window in OnPaint()
    wxPaintDCImpl( wxDC *owner, wxWindow *win );

    virtual ~wxPaintDCImpl();

    // find the entry for this DC in the cache (keyed by the window)
    static WXHDC FindDCInCache(wxWindow* win);

protected:
    static wxArrayDCInfo ms_cache;

    // find the entry for this DC in the cache (keyed by the window)
    wxPaintDCInfo *FindInCache(size_t *index = NULL) const;

    DECLARE_CLASS(wxPaintDCImpl)
    wxDECLARE_NO_COPY_CLASS(wxPaintDCImpl);
};

/*
 * wxPaintDCEx
 * This class is used when an application sends an HDC with the WM_PAINT
 * message. It is used in HandlePaint and need not be used by an application.
 */

class WXDLLIMPEXP_CORE wxPaintDCEx : public wxPaintDC
{
public:
    wxPaintDCEx(wxWindow *canvas, WXHDC dc);
    
    DECLARE_CLASS(wxPaintDCEx)
    wxDECLARE_NO_COPY_CLASS(wxPaintDCEx);
};

#endif
    // _WX_DCCLIENT_H_
