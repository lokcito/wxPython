import unittest
import wx

import unittest

"""
This file contains classes and methods for unit testing the API of
wx.GraphicsObject.

Methods yet to test:
__del__
"""

class GraphicsObjectTest(unittest.TestCase):
    def setUp(self):
        self.app = wx.PySimpleApp()
        self.testControl = wx.GraphicsObject()
    
    def testConstructor(self):
        """__init__"""
        obj = wx.GraphicsObject()
        self.assert_(isinstance(obj, wx.GraphicsObject))
    
    def testGetRenderer(self):
        """GetRenderer"""
        # TODO: is there any way to set the renderer?
        #       or to check anything else?
        self.assertEquals(None, self.testControl.GetRenderer())
    
    def testIsNullFalse(self):
        """IsNull"""
        for obj in (wx.NullGraphicsBrush,
                    wx.NullGraphicsFont,
                    wx.NullGraphicsMatrix,
                    wx.NullGraphicsPath,
                    wx.NullGraphicsPen):
            self.assert_(obj.IsNull())
            
    def testIsNullTrue(self):
        """IsNull"""
        self.assert_(not self.testControl.IsNull())
        
        
def suite():
    suite = unittest.makeSuite(GraphicsObjectTest)
    return suite
    
if __name__ == '__main__':
    unittest.main(defaultTest='suite')
