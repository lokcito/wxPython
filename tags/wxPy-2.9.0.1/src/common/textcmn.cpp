///////////////////////////////////////////////////////////////////////////////
// Name:        src/common/textcmn.cpp
// Purpose:     implementation of platform-independent functions of wxTextCtrl
// Author:      Julian Smart
// Modified by:
// Created:     13.07.99
// RCS-ID:      $Id$
// Copyright:   (c) wxWidgets team
// Licence:     wxWindows licence
///////////////////////////////////////////////////////////////////////////////

// ============================================================================
// declarations
// ============================================================================

// for compilers that support precompilation, includes "wx.h".
#include "wx/wxprec.h"

#ifdef __BORLANDC__
    #pragma hdrstop
#endif

#ifndef WX_PRECOMP
    #include "wx/event.h"
#endif // WX_PRECOMP

#if wxUSE_TEXTCTRL

#include "wx/textctrl.h"

#ifndef WX_PRECOMP
    #include "wx/intl.h"
    #include "wx/log.h"
#endif // WX_PRECOMP

#include "wx/ffile.h"

// ----------------------------------------------------------------------------
// macros
// ----------------------------------------------------------------------------

// we don't have any objects of type wxTextCtrlBase in the program, only
// wxTextCtrl, so this cast is safe
#define TEXTCTRL(ptr)   ((wxTextCtrl *)(ptr))

// ============================================================================
// implementation
// ============================================================================

IMPLEMENT_DYNAMIC_CLASS(wxTextUrlEvent, wxCommandEvent)

wxDEFINE_EVENT( wxEVT_COMMAND_TEXT_UPDATED, wxCommandEvent );
wxDEFINE_EVENT( wxEVT_COMMAND_TEXT_ENTER, wxCommandEvent );
wxDEFINE_EVENT( wxEVT_COMMAND_TEXT_URL, wxTextUrlEvent );
wxDEFINE_EVENT( wxEVT_COMMAND_TEXT_MAXLEN, wxCommandEvent );

IMPLEMENT_ABSTRACT_CLASS(wxTextCtrlBase, wxControl)

// ============================================================================
// wxTextAttr implementation
// ============================================================================

wxTextAttr::wxTextAttr(const wxColour& colText,
               const wxColour& colBack,
               const wxFont& font,
               wxTextAttrAlignment alignment): m_textAlignment(alignment), m_colText(colText), m_colBack(colBack)
{
    Init();

    if (m_colText.Ok()) m_flags |= wxTEXT_ATTR_TEXT_COLOUR;
    if (m_colBack.Ok()) m_flags |= wxTEXT_ATTR_BACKGROUND_COLOUR;
    if (alignment != wxTEXT_ALIGNMENT_DEFAULT)
        m_flags |= wxTEXT_ATTR_ALIGNMENT;

    GetFontAttributes(font);
}

// Initialisation
void wxTextAttr::Init()
{
    m_textAlignment = wxTEXT_ALIGNMENT_DEFAULT;
    m_flags = 0;
    m_leftIndent = 0;
    m_leftSubIndent = 0;
    m_rightIndent = 0;

    m_fontSize = 12;
    m_fontStyle = wxFONTSTYLE_NORMAL;
    m_fontWeight = wxFONTWEIGHT_NORMAL;
    m_fontUnderlined = false;
    m_fontEncoding = wxFONTENCODING_DEFAULT;
    m_fontFamily = wxFONTFAMILY_DEFAULT;

    m_paragraphSpacingAfter = 0;
    m_paragraphSpacingBefore = 0;
    m_lineSpacing = 0;
    m_bulletStyle = wxTEXT_ATTR_BULLET_STYLE_NONE;
    m_textEffects = wxTEXT_ATTR_EFFECT_NONE;
    m_textEffectFlags = wxTEXT_ATTR_EFFECT_NONE;
    m_outlineLevel = 0;
    m_bulletNumber = 0;
}

// Copy
void wxTextAttr::Copy(const wxTextAttr& attr)
{
    m_colText = attr.m_colText;
    m_colBack = attr.m_colBack;
    m_textAlignment = attr.m_textAlignment;
    m_leftIndent = attr.m_leftIndent;
    m_leftSubIndent = attr.m_leftSubIndent;
    m_rightIndent = attr.m_rightIndent;
    m_tabs = attr.m_tabs;
    m_flags = attr.m_flags;

    m_fontSize = attr.m_fontSize;
    m_fontStyle = attr.m_fontStyle;
    m_fontWeight = attr.m_fontWeight;
    m_fontUnderlined = attr.m_fontUnderlined;
    m_fontFaceName = attr.m_fontFaceName;
    m_fontEncoding = attr.m_fontEncoding;
    m_fontFamily = attr.m_fontFamily;
    m_textEffects = attr.m_textEffects;
    m_textEffectFlags = attr.m_textEffectFlags;

    m_paragraphSpacingAfter = attr.m_paragraphSpacingAfter;
    m_paragraphSpacingBefore = attr.m_paragraphSpacingBefore;
    m_lineSpacing = attr.m_lineSpacing;
    m_characterStyleName = attr.m_characterStyleName;
    m_paragraphStyleName = attr.m_paragraphStyleName;
    m_listStyleName = attr.m_listStyleName;
    m_bulletStyle = attr.m_bulletStyle;
    m_bulletNumber = attr.m_bulletNumber;
    m_bulletText = attr.m_bulletText;
    m_bulletFont = attr.m_bulletFont;
    m_bulletName = attr.m_bulletName;
    m_outlineLevel = attr.m_outlineLevel;

    m_urlTarget = attr.m_urlTarget;
}

// operators
void wxTextAttr::operator= (const wxTextAttr& attr)
{
    Copy(attr);
}

// Equality test
bool wxTextAttr::operator== (const wxTextAttr& attr) const
{
    return  GetFlags() == attr.GetFlags() &&

            GetTextColour() == attr.GetTextColour() &&
            GetBackgroundColour() == attr.GetBackgroundColour() &&

            GetAlignment() == attr.GetAlignment() &&
            GetLeftIndent() == attr.GetLeftIndent() &&
            GetLeftSubIndent() == attr.GetLeftSubIndent() &&
            GetRightIndent() == attr.GetRightIndent() &&
            TabsEq(GetTabs(), attr.GetTabs()) &&

            GetParagraphSpacingAfter() == attr.GetParagraphSpacingAfter() &&
            GetParagraphSpacingBefore() == attr.GetParagraphSpacingBefore() &&
            GetLineSpacing() == attr.GetLineSpacing() &&
            GetCharacterStyleName() == attr.GetCharacterStyleName() &&
            GetParagraphStyleName() == attr.GetParagraphStyleName() &&
            GetListStyleName() == attr.GetListStyleName() &&

            GetBulletStyle() == attr.GetBulletStyle() &&
            GetBulletText() == attr.GetBulletText() &&
            GetBulletNumber() == attr.GetBulletNumber() &&
            GetBulletFont() == attr.GetBulletFont() &&
            GetBulletName() == attr.GetBulletName() &&

            GetTextEffects() == attr.GetTextEffects() &&
            GetTextEffectFlags() == attr.GetTextEffectFlags() &&

            GetOutlineLevel() == attr.GetOutlineLevel() &&

            GetFontSize() == attr.GetFontSize() &&
            GetFontStyle() == attr.GetFontStyle() &&
            GetFontWeight() == attr.GetFontWeight() &&
            GetFontUnderlined() == attr.GetFontUnderlined() &&
            GetFontFaceName() == attr.GetFontFaceName() &&
            GetFontEncoding() == attr.GetFontEncoding() &&
            GetFontFamily() == attr.GetFontFamily() &&

            GetURL() == attr.GetURL();
}

// Partial equality test taking flags into account
bool wxTextAttr::EqPartial(const wxTextAttr& attr, int flags) const
{
    if ((flags & wxTEXT_ATTR_TEXT_COLOUR) && GetTextColour() != attr.GetTextColour())
        return false;

    if ((flags & wxTEXT_ATTR_BACKGROUND_COLOUR) && GetBackgroundColour() != attr.GetBackgroundColour())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_FACE) &&
        GetFontFaceName() != attr.GetFontFaceName())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_SIZE) &&
        GetFontSize() != attr.GetFontSize())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_WEIGHT) &&
        GetFontWeight() != attr.GetFontWeight())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_ITALIC) &&
        GetFontStyle() != attr.GetFontStyle())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_UNDERLINE) &&
        GetFontUnderlined() != attr.GetFontUnderlined())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_ENCODING) &&
        GetFontEncoding() != attr.GetFontEncoding())
        return false;

    if ((flags & wxTEXT_ATTR_FONT_FAMILY) &&
        GetFontFamily() != attr.GetFontFamily())
        return false;

    if ((flags & wxTEXT_ATTR_URL) && GetURL() != attr.GetURL())
        return false;

    if ((flags & wxTEXT_ATTR_ALIGNMENT) && GetAlignment() != attr.GetAlignment())
        return false;

    if ((flags & wxTEXT_ATTR_LEFT_INDENT) &&
        ((GetLeftIndent() != attr.GetLeftIndent()) || (GetLeftSubIndent() != attr.GetLeftSubIndent())))
        return false;

    if ((flags & wxTEXT_ATTR_RIGHT_INDENT) &&
        (GetRightIndent() != attr.GetRightIndent()))
        return false;

    if ((flags & wxTEXT_ATTR_PARA_SPACING_AFTER) &&
        (GetParagraphSpacingAfter() != attr.GetParagraphSpacingAfter()))
        return false;

    if ((flags & wxTEXT_ATTR_PARA_SPACING_BEFORE) &&
        (GetParagraphSpacingBefore() != attr.GetParagraphSpacingBefore()))
        return false;

    if ((flags & wxTEXT_ATTR_LINE_SPACING) &&
        (GetLineSpacing() != attr.GetLineSpacing()))
        return false;

    if ((flags & wxTEXT_ATTR_CHARACTER_STYLE_NAME) &&
        (GetCharacterStyleName() != attr.GetCharacterStyleName()))
        return false;

    if ((flags & wxTEXT_ATTR_PARAGRAPH_STYLE_NAME) &&
        (GetParagraphStyleName() != attr.GetParagraphStyleName()))
        return false;

    if ((flags & wxTEXT_ATTR_LIST_STYLE_NAME) &&
        (GetListStyleName() != attr.GetListStyleName()))
        return false;

    if ((flags & wxTEXT_ATTR_BULLET_STYLE) &&
        (GetBulletStyle() != attr.GetBulletStyle()))
         return false;

    if ((flags & wxTEXT_ATTR_BULLET_NUMBER) &&
        (GetBulletNumber() != attr.GetBulletNumber()))
         return false;

    if ((flags & wxTEXT_ATTR_BULLET_TEXT) &&
        (GetBulletText() != attr.GetBulletText()) &&
        (GetBulletFont() != attr.GetBulletFont()))
         return false;

    if ((flags & wxTEXT_ATTR_BULLET_NAME) &&
        (GetBulletName() != attr.GetBulletName()))
         return false;

    if ((flags & wxTEXT_ATTR_TABS) &&
        !TabsEq(GetTabs(), attr.GetTabs()))
        return false;

    if ((flags & wxTEXT_ATTR_PAGE_BREAK) &&
        (HasPageBreak() != attr.HasPageBreak()))
         return false;

    if (flags & wxTEXT_ATTR_EFFECTS)
    {
        if (HasTextEffects() != attr.HasTextEffects())
            return false;
        if (!BitlistsEqPartial(GetTextEffects(), attr.GetTextEffects(), attr.GetTextEffectFlags()))
            return false;
    }

    if ((flags & wxTEXT_ATTR_OUTLINE_LEVEL) &&
        (GetOutlineLevel() != attr.GetOutlineLevel()))
         return false;

    return true;
}

// Create font from font attributes.
wxFont wxTextAttr::GetFont() const
{
    if ( !HasFont() )
        return wxNullFont;

    int fontSize = 10;
    if (HasFontSize())
        fontSize = GetFontSize();

    int fontStyle = wxNORMAL;
    if (HasFontItalic())
        fontStyle = GetFontStyle();

    int fontWeight = wxNORMAL;
    if (HasFontWeight())
        fontWeight = GetFontWeight();

    bool underlined = false;
    if (HasFontUnderlined())
        underlined = GetFontUnderlined();

    wxString fontFaceName;
    if (HasFontFaceName())
        fontFaceName = GetFontFaceName();

    wxFontEncoding encoding = wxFONTENCODING_DEFAULT;
    if (HasFontEncoding())
        encoding = GetFontEncoding();

    int fontFamily = wxFONTFAMILY_DEFAULT;
    if (HasFontFamily())
        fontFamily = GetFontFamily();

    wxFont font(fontSize, fontFamily, fontStyle, fontWeight, underlined, fontFaceName, encoding);
    return font;
}

// Get attributes from font.
bool wxTextAttr::GetFontAttributes(const wxFont& font, int flags)
{
    if (!font.Ok())
        return false;

    if (flags & wxTEXT_ATTR_FONT_SIZE)
        m_fontSize = font.GetPointSize();

    if (flags & wxTEXT_ATTR_FONT_ITALIC)
        m_fontStyle = font.GetStyle();

    if (flags & wxTEXT_ATTR_FONT_WEIGHT)
        m_fontWeight = font.GetWeight();

    if (flags & wxTEXT_ATTR_FONT_UNDERLINE)
        m_fontUnderlined = font.GetUnderlined();

    if (flags & wxTEXT_ATTR_FONT_FACE)
        m_fontFaceName = font.GetFaceName();

    if (flags & wxTEXT_ATTR_FONT_ENCODING)
        m_fontEncoding = font.GetEncoding();

    if (flags & wxTEXT_ATTR_FONT_FAMILY)
        m_fontFamily = font.GetFamily();

    m_flags |= flags;

    return true;
}

// Resets bits in destination so new attributes aren't merged with mutually exclusive ones
static bool wxResetIncompatibleBits(const int mask, const int srcFlags, int& destFlags, int& destBits)
{
    if ((srcFlags & mask) && (destFlags & mask))
    {
        destBits &= ~mask;
        destFlags &= ~mask;
    }

    return true;
}

bool wxTextAttr::Apply(const wxTextAttr& style, const wxTextAttr* compareWith)
{
    wxTextAttr& destStyle = (*this);

    if (style.HasFontWeight())
    {
        if (!(compareWith && compareWith->HasFontWeight() && compareWith->GetFontWeight() == style.GetFontWeight()))
            destStyle.SetFontWeight(style.GetFontWeight());
    }

    if (style.HasFontSize())
    {
        if (!(compareWith && compareWith->HasFontSize() && compareWith->GetFontSize() == style.GetFontSize()))
            destStyle.SetFontSize(style.GetFontSize());
    }

    if (style.HasFontItalic())
    {
        if (!(compareWith && compareWith->HasFontItalic() && compareWith->GetFontStyle() == style.GetFontStyle()))
            destStyle.SetFontStyle(style.GetFontStyle());
    }

    if (style.HasFontUnderlined())
    {
        if (!(compareWith && compareWith->HasFontUnderlined() && compareWith->GetFontUnderlined() == style.GetFontUnderlined()))
            destStyle.SetFontUnderlined(style.GetFontUnderlined());
    }

    if (style.HasFontFaceName())
    {
        if (!(compareWith && compareWith->HasFontFaceName() && compareWith->GetFontFaceName() == style.GetFontFaceName()))
            destStyle.SetFontFaceName(style.GetFontFaceName());
    }

    if (style.HasFontEncoding())
    {
        if (!(compareWith && compareWith->HasFontEncoding() && compareWith->GetFontEncoding() == style.GetFontEncoding()))
            destStyle.SetFontEncoding(style.GetFontEncoding());
    }

    if (style.HasFontFamily())
    {
        if (!(compareWith && compareWith->HasFontFamily() && compareWith->GetFontFamily() == style.GetFontFamily()))
            destStyle.SetFontFamily(style.GetFontFamily());
    }

    if (style.GetTextColour().Ok() && style.HasTextColour())
    {
        if (!(compareWith && compareWith->HasTextColour() && compareWith->GetTextColour() == style.GetTextColour()))
            destStyle.SetTextColour(style.GetTextColour());
    }

    if (style.GetBackgroundColour().Ok() && style.HasBackgroundColour())
    {
        if (!(compareWith && compareWith->HasBackgroundColour() && compareWith->GetBackgroundColour() == style.GetBackgroundColour()))
            destStyle.SetBackgroundColour(style.GetBackgroundColour());
    }

    if (style.HasAlignment())
    {
        if (!(compareWith && compareWith->HasAlignment() && compareWith->GetAlignment() == style.GetAlignment()))
            destStyle.SetAlignment(style.GetAlignment());
    }

    if (style.HasTabs())
    {
        if (!(compareWith && compareWith->HasTabs() && TabsEq(compareWith->GetTabs(), style.GetTabs())))
            destStyle.SetTabs(style.GetTabs());
    }

    if (style.HasLeftIndent())
    {
        if (!(compareWith && compareWith->HasLeftIndent() && compareWith->GetLeftIndent() == style.GetLeftIndent()
                          && compareWith->GetLeftSubIndent() == style.GetLeftSubIndent()))
            destStyle.SetLeftIndent(style.GetLeftIndent(), style.GetLeftSubIndent());
    }

    if (style.HasRightIndent())
    {
        if (!(compareWith && compareWith->HasRightIndent() && compareWith->GetRightIndent() == style.GetRightIndent()))
            destStyle.SetRightIndent(style.GetRightIndent());
    }

    if (style.HasParagraphSpacingAfter())
    {
        if (!(compareWith && compareWith->HasParagraphSpacingAfter() && compareWith->GetParagraphSpacingAfter() == style.GetParagraphSpacingAfter()))
            destStyle.SetParagraphSpacingAfter(style.GetParagraphSpacingAfter());
    }

    if (style.HasParagraphSpacingBefore())
    {
        if (!(compareWith && compareWith->HasParagraphSpacingBefore() && compareWith->GetParagraphSpacingBefore() == style.GetParagraphSpacingBefore()))
            destStyle.SetParagraphSpacingBefore(style.GetParagraphSpacingBefore());
    }

    if (style.HasLineSpacing())
    {
        if (!(compareWith && compareWith->HasLineSpacing() && compareWith->GetLineSpacing() == style.GetLineSpacing()))
            destStyle.SetLineSpacing(style.GetLineSpacing());
    }

    if (style.HasCharacterStyleName())
    {
        if (!(compareWith && compareWith->HasCharacterStyleName() && compareWith->GetCharacterStyleName() == style.GetCharacterStyleName()))
            destStyle.SetCharacterStyleName(style.GetCharacterStyleName());
    }

    if (style.HasParagraphStyleName())
    {
        if (!(compareWith && compareWith->HasParagraphStyleName() && compareWith->GetParagraphStyleName() == style.GetParagraphStyleName()))
            destStyle.SetParagraphStyleName(style.GetParagraphStyleName());
    }

    if (style.HasListStyleName())
    {
        if (!(compareWith && compareWith->HasListStyleName() && compareWith->GetListStyleName() == style.GetListStyleName()))
            destStyle.SetListStyleName(style.GetListStyleName());
    }

    if (style.HasBulletStyle())
    {
        if (!(compareWith && compareWith->HasBulletStyle() && compareWith->GetBulletStyle() == style.GetBulletStyle()))
            destStyle.SetBulletStyle(style.GetBulletStyle());
    }

    if (style.HasBulletText())
    {
        if (!(compareWith && compareWith->HasBulletText() && compareWith->GetBulletText() == style.GetBulletText()))
        {
            destStyle.SetBulletText(style.GetBulletText());
            destStyle.SetBulletFont(style.GetBulletFont());
        }
    }

    if (style.HasBulletNumber())
    {
        if (!(compareWith && compareWith->HasBulletNumber() && compareWith->GetBulletNumber() == style.GetBulletNumber()))
            destStyle.SetBulletNumber(style.GetBulletNumber());
    }

    if (style.HasBulletName())
    {
        if (!(compareWith && compareWith->HasBulletName() && compareWith->GetBulletName() == style.GetBulletName()))
            destStyle.SetBulletName(style.GetBulletName());
    }

    if (style.HasURL())
    {
        if (!(compareWith && compareWith->HasURL() && compareWith->GetURL() == style.GetURL()))
            destStyle.SetURL(style.GetURL());
    }

    if (style.HasPageBreak())
    {
        if (!(compareWith && compareWith->HasPageBreak()))
            destStyle.SetPageBreak();
    }

    if (style.HasTextEffects())
    {
        if (!(compareWith && compareWith->HasTextEffects() && compareWith->GetTextEffects() == style.GetTextEffects()))
        {
            int destBits = destStyle.GetTextEffects();
            int destFlags = destStyle.GetTextEffectFlags();

            int srcBits = style.GetTextEffects();
            int srcFlags = style.GetTextEffectFlags();

            // Reset incompatible bits in the destination
            wxResetIncompatibleBits((wxTEXT_ATTR_EFFECT_SUPERSCRIPT|wxTEXT_ATTR_EFFECT_SUBSCRIPT), srcFlags, destFlags, destBits);
            wxResetIncompatibleBits((wxTEXT_ATTR_EFFECT_CAPITALS|wxTEXT_ATTR_EFFECT_SMALL_CAPITALS), srcFlags, destFlags, destBits);
            wxResetIncompatibleBits((wxTEXT_ATTR_EFFECT_STRIKETHROUGH|wxTEXT_ATTR_EFFECT_DOUBLE_STRIKETHROUGH), srcFlags, destFlags, destBits);

            CombineBitlists(destBits, srcBits, destFlags, srcFlags);

            destStyle.SetTextEffects(destBits);
            destStyle.SetTextEffectFlags(destFlags);
        }
    }

    if (style.HasOutlineLevel())
    {
        if (!(compareWith && compareWith->HasOutlineLevel() && compareWith->GetOutlineLevel() == style.GetOutlineLevel()))
            destStyle.SetOutlineLevel(style.GetOutlineLevel());
    }

    return true;
}

/* static */
wxTextAttr wxTextAttr::Combine(const wxTextAttr& attr,
                               const wxTextAttr& attrDef,
                               const wxTextCtrlBase *text)
{
    wxFont font;
    if (attr.HasFont())
        font = attr.GetFont();

    if ( !font.Ok() )
    {
        if (attrDef.HasFont())
            font = attrDef.GetFont();

        if ( text && !font.Ok() )
            font = text->GetFont();
    }

    wxColour colFg = attr.GetTextColour();
    if ( !colFg.Ok() )
    {
        colFg = attrDef.GetTextColour();

        if ( text && !colFg.Ok() )
            colFg = text->GetForegroundColour();
    }

    wxColour colBg = attr.GetBackgroundColour();
    if ( !colBg.Ok() )
    {
        colBg = attrDef.GetBackgroundColour();

        if ( text && !colBg.Ok() )
            colBg = text->GetBackgroundColour();
    }

    wxTextAttr newAttr(colFg, colBg, font);

    if (attr.HasAlignment())
        newAttr.SetAlignment(attr.GetAlignment());
    else if (attrDef.HasAlignment())
        newAttr.SetAlignment(attrDef.GetAlignment());

    if (attr.HasTabs())
        newAttr.SetTabs(attr.GetTabs());
    else if (attrDef.HasTabs())
        newAttr.SetTabs(attrDef.GetTabs());

    if (attr.HasLeftIndent())
        newAttr.SetLeftIndent(attr.GetLeftIndent(), attr.GetLeftSubIndent());
    else if (attrDef.HasLeftIndent())
        newAttr.SetLeftIndent(attrDef.GetLeftIndent(), attr.GetLeftSubIndent());

    if (attr.HasRightIndent())
        newAttr.SetRightIndent(attr.GetRightIndent());
    else if (attrDef.HasRightIndent())
        newAttr.SetRightIndent(attrDef.GetRightIndent());

    return newAttr;
}

/// Compare tabs
bool wxTextAttr::TabsEq(const wxArrayInt& tabs1, const wxArrayInt& tabs2)
{
    if (tabs1.GetCount() != tabs2.GetCount())
        return false;

    size_t i;
    for (i = 0; i < tabs1.GetCount(); i++)
    {
        if (tabs1[i] != tabs2[i])
            return false;
    }
    return true;
}

// Remove attributes
bool wxTextAttr::RemoveStyle(wxTextAttr& destStyle, const wxTextAttr& style)
{
    int flags = style.GetFlags();
    int destFlags = destStyle.GetFlags();

    destStyle.SetFlags(destFlags & ~flags);

    return true;
}

/// Combine two bitlists, specifying the bits of interest with separate flags.
bool wxTextAttr::CombineBitlists(int& valueA, int valueB, int& flagsA, int flagsB)
{
    // We want to apply B's bits to A, taking into account each's flags which indicate which bits
    // are to be taken into account. A zero in B's bits should reset that bit in A but only if B's flags
    // indicate it.

    // First, reset the 0 bits from B. We make a mask so we're only dealing with B's zero
    // bits at this point, ignoring any 1 bits in B or 0 bits in B that are not relevant.
    int valueA2 = ~(~valueB & flagsB) & valueA;

    // Now combine the 1 bits.
    int valueA3 = (valueB & flagsB) | valueA2;

    valueA = valueA3;
    flagsA = (flagsA | flagsB);

    return true;
}

/// Compare two bitlists
bool wxTextAttr::BitlistsEqPartial(int valueA, int valueB, int flags)
{
    int relevantBitsA = valueA & flags;
    int relevantBitsB = valueB & flags;
    return (relevantBitsA != relevantBitsB);
}

/// Split into paragraph and character styles
bool wxTextAttr::SplitParaCharStyles(const wxTextAttr& style, wxTextAttr& parStyle, wxTextAttr& charStyle)
{
    wxTextAttr defaultCharStyle1(style);
    wxTextAttr defaultParaStyle1(style);
    defaultCharStyle1.SetFlags(defaultCharStyle1.GetFlags()&wxTEXT_ATTR_CHARACTER);
    defaultParaStyle1.SetFlags(defaultParaStyle1.GetFlags()&wxTEXT_ATTR_PARAGRAPH);

    charStyle.Apply(defaultCharStyle1);
    parStyle.Apply(defaultParaStyle1);

    return true;
}

// apply styling to text range
bool wxTextCtrlBase::SetStyle(long WXUNUSED(start), long WXUNUSED(end),
                              const wxTextAttr& WXUNUSED(style))
{
    // to be implemented in derived classes
    return false;
}

// get the styling at the given position
bool wxTextCtrlBase::GetStyle(long WXUNUSED(position), wxTextAttr& WXUNUSED(style))
{
    // to be implemented in derived classes
    return false;
}

// change default text attributes
bool wxTextCtrlBase::SetDefaultStyle(const wxTextAttr& style)
{
    // keep the old attributes if the new style doesn't specify them unless the
    // new style is empty - then reset m_defaultStyle (as there is no other way
    // to do it)
    if ( style.IsDefault() )
        m_defaultStyle = style;
    else
        m_defaultStyle = wxTextAttr::Combine(style, m_defaultStyle, this);

    return true;
}

// ----------------------------------------------------------------------------
// file IO functions
// ----------------------------------------------------------------------------

bool wxTextCtrlBase::DoLoadFile(const wxString& filename, int WXUNUSED(fileType))
{
#if wxUSE_FFILE
    wxFFile file(filename);
    if ( file.IsOpened() )
    {
        wxString text;
        if ( file.ReadAll(&text) )
        {
            SetValue(text);

            DiscardEdits();

            m_filename = filename;

            return true;
        }
    }

    wxLogError(_("File couldn't be loaded."));
#endif // wxUSE_FFILE

    return false;
}

bool wxTextAreaBase::SaveFile(const wxString& filename, int fileType)
{
    wxString filenameToUse = filename.empty() ? m_filename : filename;
    if ( filenameToUse.empty() )
    {
        // what kind of message to give? is it an error or a program bug?
        wxLogDebug(wxT("Can't save textctrl to file without filename."));

        return false;
    }

    return DoSaveFile(filenameToUse, fileType);
}

bool wxTextCtrlBase::DoSaveFile(const wxString& filename, int WXUNUSED(fileType))
{
#if wxUSE_FFILE
    wxFFile file(filename, _T("w"));
    if ( file.IsOpened() && file.Write(GetValue()) )
    {
        // if it worked, save for future calls
        m_filename = filename;

        // it's not modified any longer
        DiscardEdits();

        return true;
    }
#endif // wxUSE_FFILE

    wxLogError(_("The text couldn't be saved."));

    return false;
}

// ----------------------------------------------------------------------------
// stream-like insertion operator
// ----------------------------------------------------------------------------

wxTextCtrl& wxTextCtrlBase::operator<<(const wxString& s)
{
    AppendText(s);
    return *TEXTCTRL(this);
}

wxTextCtrl& wxTextCtrlBase::operator<<(double d)
{
    return *this << wxString::Format("%.2f", d);
}

wxTextCtrl& wxTextCtrlBase::operator<<(int i)
{
    return *this << wxString::Format("%d", i);
}

wxTextCtrl& wxTextCtrlBase::operator<<(long l)
{
    return *this << wxString::Format("%ld", l);
}

// ----------------------------------------------------------------------------
// streambuf methods implementation
// ----------------------------------------------------------------------------

#if wxHAS_TEXT_WINDOW_STREAM

int wxTextCtrlBase::overflow(int c)
{
    AppendText((wxChar)c);

    // return something different from EOF
    return 0;
}

#endif // wxHAS_TEXT_WINDOW_STREAM

// ----------------------------------------------------------------------------
// emulating key presses
// ----------------------------------------------------------------------------

bool wxTextCtrlBase::EmulateKeyPress(const wxKeyEvent& event)
{
    // we have a native implementation for Win32 and so don't need this one
#ifndef __WIN32__
    wxChar ch = 0;
    int keycode = event.GetKeyCode();
    switch ( keycode )
    {
        case WXK_NUMPAD0:
        case WXK_NUMPAD1:
        case WXK_NUMPAD2:
        case WXK_NUMPAD3:
        case WXK_NUMPAD4:
        case WXK_NUMPAD5:
        case WXK_NUMPAD6:
        case WXK_NUMPAD7:
        case WXK_NUMPAD8:
        case WXK_NUMPAD9:
            ch = (wxChar)(_T('0') + keycode - WXK_NUMPAD0);
            break;

        case WXK_MULTIPLY:
        case WXK_NUMPAD_MULTIPLY:
            ch = _T('*');
            break;

        case WXK_ADD:
        case WXK_NUMPAD_ADD:
            ch = _T('+');
            break;

        case WXK_SUBTRACT:
        case WXK_NUMPAD_SUBTRACT:
            ch = _T('-');
            break;

        case WXK_DECIMAL:
        case WXK_NUMPAD_DECIMAL:
            ch = _T('.');
            break;

        case WXK_DIVIDE:
        case WXK_NUMPAD_DIVIDE:
            ch = _T('/');
            break;

        case WXK_DELETE:
        case WXK_NUMPAD_DELETE:
            // delete the character at cursor
            {
                const long pos = GetInsertionPoint();
                if ( pos < GetLastPosition() )
                    Remove(pos, pos + 1);
            }
            break;

        case WXK_BACK:
            // delete the character before the cursor
            {
                const long pos = GetInsertionPoint();
                if ( pos > 0 )
                    Remove(pos - 1, pos);
            }
            break;

        default:
#if wxUSE_UNICODE
            if ( event.GetUnicodeKey() )
            {
                ch = event.GetUnicodeKey();
            }
            else
#endif
            if ( keycode < 256 && keycode >= 0 && wxIsprint(keycode) )
            {
                // FIXME this is not going to work for non letters...
                if ( !event.ShiftDown() )
                {
                    keycode = wxTolower(keycode);
                }

                ch = (wxChar)keycode;
            }
            else
            {
                ch = _T('\0');
            }
    }

    if ( ch )
    {
        WriteText(ch);

        return true;
    }
#else // __WIN32__
    wxUnusedVar(event);
#endif // !__WIN32__/__WIN32__

    return false;
}

// do the window-specific processing after processing the update event
void wxTextCtrlBase::DoUpdateWindowUI(wxUpdateUIEvent& event)
{
    // call inherited, but skip the wxControl's version, and call directly the
    // wxWindow's one instead, because the only reason why we are overriding this
    // function is that we want to use SetValue() instead of wxControl::SetLabel()
    wxWindowBase::DoUpdateWindowUI(event);

    // update text
    if ( event.GetSetText() )
    {
        if ( event.GetText() != GetValue() )
            SetValue(event.GetText());
    }
}

// ----------------------------------------------------------------------------
// hit testing
// ----------------------------------------------------------------------------

wxTextCtrlHitTestResult
wxTextAreaBase::HitTest(const wxPoint& pt, wxTextCoord *x, wxTextCoord *y) const
{
    // implement in terms of the other overload as the native ports typically
    // can get the position and not (x, y) pair directly (although wxUniv
    // directly gets x and y -- and so overrides this method as well)
    long pos;
    wxTextCtrlHitTestResult rc = HitTest(pt, &pos);

    if ( rc != wxTE_HT_UNKNOWN )
    {
        PositionToXY(pos, x, y);
    }

    return rc;
}

wxTextCtrlHitTestResult
wxTextAreaBase::HitTest(const wxPoint& WXUNUSED(pt), long * WXUNUSED(pos)) const
{
    // not implemented
    return wxTE_HT_UNKNOWN;
}

// ----------------------------------------------------------------------------
// events
// ----------------------------------------------------------------------------

/* static */
bool wxTextCtrlBase::SendTextUpdatedEvent(wxWindow *win)
{
    wxCommandEvent event(wxEVT_COMMAND_TEXT_UPDATED, win->GetId());

    // do not do this as it could be very inefficient if the text control
    // contains a lot of text and we're not using ref-counted wxString
    // implementation -- instead, event.GetString() will query the control for
    // its current text if needed
    //event.SetString(win->GetValue());

    event.SetEventObject(win);
    return win->GetEventHandler()->ProcessEvent(event);
}

#else // !wxUSE_TEXTCTRL

// define this one even if !wxUSE_TEXTCTRL because it is also used by other
// controls (wxComboBox and wxSpinCtrl)

wxDEFINE_EVENT( wxEVT_COMMAND_TEXT_UPDATED, wxCommandEvent );

#endif // wxUSE_TEXTCTRL/!wxUSE_TEXTCTRL
