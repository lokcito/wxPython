###############################################################################
# Name: mssql.py                                                              #
# Purpose: Define Microsoft SQL syntax for highlighting and other features    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
FILE: mssql.py                                                              
AUTHOR: Cody Precord                                                        
@summary: Lexer configuration module for Microsoft SQL.
@todo: too many to list                                                     

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
import wx.stc as stc

# Local Imports
import syndata

#-----------------------------------------------------------------------------#

#---- Keyword Specifications ----#

# Data Types
MSSQL_DAT = (0, "")
# System Tables
MSSQL_SYS = (1, "")
# Global Variables
MSSQL_GLOB = (2, "")
# Functions
MSSQL_FUNC = (3, "")
# System Stored Procedures
MSSQL_SYSP = (4, "")
# Operators
MSSQL_OPS = (5, "")

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [ ('STC_MSSQL_DEFAULT', 'default_style'),
                 ('STC_MSSQL_COMMENT', 'comment_style'),
                 ('STC_MSSQL_COLUMN_NAME', 'keyword_style'),
                 ('STC_MSSQL_COLUMN_NAME_2', 'keyword_style'),
                 ('STC_MSSQL_DATATYPE', 'keyword2_style'),
                 ('STC_MSSQL_DEFAULT_PREF_DATATYPE', 'class_style'),
                 ('STC_MSSQL_FUNCTION', 'keyword3_style'),
                 ('STC_MSSQL_GLOBAL_VARIABLE', 'global_style'),
                 ('STC_MSSQL_IDENTIFIER', 'default_style'),
                 ('STC_MSSQL_LINE_COMMENT', 'comment_style'),
                 ('STC_MSSQL_NUMBER', 'number_style'),
                 ('STC_MSSQL_OPERATOR', 'operator_style'),
                 ('STC_MSSQL_STATEMENT', 'keyword_style'),
                 ('STC_MSSQL_STORED_PROCEDURE', 'scalar2_style'),
                 ('STC_MSSQL_STRING', 'string_style'),
                 ('STC_MSSQL_SYSTABLE', 'keyword4_style'),
                 ('STC_MSSQL_VARIABLE', 'scalar_style') ]

#---- Extra Properties ----#
FOLD = ("fold", "1")
FOLD_COMMENT = ("fold.comment", "1")
FOLD_COMPACT = ("fold.compact", "1")

#-----------------------------------------------------------------------------#

class SyntaxData(syndata.SyntaxDataBase):
    """SyntaxData object for MS SQL""" 
    def __init__(self, langid):
        syndata.SyntaxDataBase.__init__(self, langid)

        # Setup
        self.SetLexer(stc.STC_LEX_MSSQL)

    def GetSyntaxSpec(self):
        """Syntax Specifications """
        return SYNTAX_ITEMS

    def GetProperties(self):
        """Returns a list of Extra Properties to set """
        return [FOLD]

    def GetCommentPattern(self):
        """Returns a list of characters used to comment a block of code """
        return [u'--']
