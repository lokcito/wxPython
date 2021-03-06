///////////////////////////////////////////////////////////////////////////////
// Name:        tests/toplevel/toplevel.cpp
// Purpose:     Tests for wxTopLevelWindow
// Author:      Kevin Ollivier
// Created:     2008-05-25
// RCS-ID:      $Id: toplevel.cpp 53741 2008-05-25 03:08:31Z VZ $
// Copyright:   (c) 2009 Kevin Ollivier <kevino@theolliviers.com>
///////////////////////////////////////////////////////////////////////////////

// ----------------------------------------------------------------------------
// headers
// ----------------------------------------------------------------------------

#include "testprec.h"

#ifdef __BORLANDC__
    #pragma hdrstop
#endif

#ifndef WX_PRECOMP
    #include "wx/app.h"
    #include "wx/window.h"
#endif // WX_PRECOMP

#include "wx/evtloop.h"

// ----------------------------------------------------------------------------
// test class
// ----------------------------------------------------------------------------

class TopLevelWindowTestCase : public CppUnit::TestCase
{
public:
    TopLevelWindowTestCase() { }

    virtual void setUp();
    virtual void tearDown();

private:
    CPPUNIT_TEST_SUITE( TopLevelWindowTestCase );
        CPPUNIT_TEST( DialogShowTest );
        CPPUNIT_TEST( FrameShowTest );
    CPPUNIT_TEST_SUITE_END();

    void DialogShowTest();
    void FrameShowTest();
    void TopLevelWindowShowTest(wxTopLevelWindow* tlw);

    DECLARE_NO_COPY_CLASS(TopLevelWindowTestCase)
};

// register in the unnamed registry so that these tests are run by default
CPPUNIT_TEST_SUITE_REGISTRATION( TopLevelWindowTestCase );

// also include in it's own registry so that these tests can be run alone
CPPUNIT_TEST_SUITE_NAMED_REGISTRATION( TopLevelWindowTestCase, "TopLevelWindowTestCase" );

// ----------------------------------------------------------------------------
// test initialization
// ----------------------------------------------------------------------------

void TopLevelWindowTestCase::setUp()
{
}

void TopLevelWindowTestCase::tearDown()
{
}

// ----------------------------------------------------------------------------
// tests themselves
// ----------------------------------------------------------------------------

void TopLevelWindowTestCase::DialogShowTest()
{
    wxDialog* dialog = new wxDialog(NULL, -1, "Dialog Test");
    TopLevelWindowShowTest(dialog);
    dialog->Destroy();
}

void TopLevelWindowTestCase::FrameShowTest()
{
    wxFrame* frame = new wxFrame(NULL, -1, "Frame test");
    TopLevelWindowShowTest(frame);
    frame->Destroy();
}

void TopLevelWindowTestCase::TopLevelWindowShowTest(wxTopLevelWindow* tlw)
{
    CPPUNIT_ASSERT(!tlw->IsShown());
    
    wxTextCtrl* textCtrl = new wxTextCtrl(tlw, -1, "test");
    textCtrl->SetFocus();
    
// only run this test on platforms where ShowWithoutActivating is implemented.
#ifdef __WXMSW__ || defined(__WXMAC__)
    tlw->ShowWithoutActivating();
    CPPUNIT_ASSERT(tlw->IsShown());
    CPPUNIT_ASSERT(!tlw->IsActive());
    
    tlw->Hide();
    CPPUNIT_ASSERT(!tlw->IsShown());
    CPPUNIT_ASSERT(!tlw->IsActive());
#endif
    
    tlw->Show(true);
    CPPUNIT_ASSERT(tlw->IsActive());
    CPPUNIT_ASSERT(tlw->IsShown());
    
    tlw->Hide();
    CPPUNIT_ASSERT(!tlw->IsShown());
    CPPUNIT_ASSERT(tlw->IsActive());
}
