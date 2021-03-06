''' Module implementing different transforms '''

class ITransform(object):
    ''' Interface for all transforms. A transform must be callable.
        When called, coords are transformed and the transformed coordinates are
        returned.
    '''
    def __call__(self, coords):
        pass


import numpy
from math import radians, degrees

class LinearTransform(object):
    ''' Implements an arbitrary n-dimensional linear homogenous transform.
        It's based around a matrix which is 3x3 for a 2-dimensional transform.
        The matrix holds scale and translation of an object.
        Inverse and transpose can also be computed.
        The linear transform can also be concatenated with different other
        transforms.
        
        Todo: The concatenation of transforms should be moved into some kind of
        'TransformManager' which decides how to concatenate the different
        transforms.
    '''
    #implements(ITransform)
    def __init__(self, dimension, matrix = None ):
        if not matrix is None:
            self.matrix = matrix
        else:
            self.matrix = numpy.eye( *dimension )     # identity matrix
    
    def __call__(self, coords):
        ''' transforms coords (which need to be an array of 2-vectors
             (numpy.arrays of size 2) ).
            A bit messy, it basically appends 1s to the coordinates and later
            removes them again.
        '''
        if len(coords) == 0:
            return coords
        return numpy.dot( numpy.column_stack( (coords, numpy.ones(len(coords))) ), numpy.transpose( self.matrix ) )[ ..., :-1 ]

    def _getTranslation(self):
        return self.matrix[..., -1][:-1]

    def _setTranslation(self, translation):
        self.matrix[..., -1][:-1] = translation

    # can probably be rewritten 
    def _getScale(self):
        ''' returns the scale of this transform.
            The assumption is that our matrix is composed like
               self.matrix = t * r * s --> s = r^-1 * t^-1 * self.matrix
            where t = translation, r = rotation and = scale.
            The scale can then be computed by the length of the column vectors
            in the matrix upper 2x2.
        '''
        temp =  numpy.transpose(self.matrix[:-1, :-1])  # eliminate t part
        normalized = numpy.array( [ col / numpy.sqrt( numpy.dot( col, col ) ) for col in temp ] )
        scaleMatrix = numpy.dot( temp, numpy.linalg.inv( normalized ) ) # same as self.matrix * inv(normalized)
        return scaleMatrix.diagonal()

    def _setScale(self, scale):
        current_scale = self.scale
        for row in self.matrix[:-1]:
            row[:-1] *= scale / current_scale
            
    def _getInverse(self):
        return self.__class__( (), matrix = numpy.linalg.inv( self.matrix ) )

    def _getTranspose(self):
        return self.__class__( (), matrix = numpy.transpose( self.matrix ) )

    def __mul__(self, other):
        ''' multiplies this transform by another one.
            Todo: The concatenation of transforms should be moved into some kind
            of 'TransformManager' which decides how to concatenate the different
            transforms.
        '''
        if isinstance(other, LinearTransform):
            return self.__class__( (), matrix = numpy.dot( self.matrix, other.matrix ) )
        elif isinstance(other, LinearAndArbitraryCompoundTransform):
            linearPart = self.__class__( (), matrix = numpy.dot( self.matrix, other.transform1.matrix ) )
            return LinearAndArbitraryCompoundTransform( linearPart, other.transform2 )
        else:
            return LinearAndArbitraryCompoundTransform( self, other )

    translation = property( _getTranslation, _setTranslation )
    position = pos = translation
    scale = property( _getScale, _setScale )
    inverse = property( _getInverse )
    transpose = property( _getTranspose )


class LinearTransform2D(LinearTransform):
    ''' A specialized linear transform for the 2D case. Also supports rotation.
    '''
    def __init__(self, dimension = (3,3), matrix = None):
        LinearTransform.__init__( self, dimension = (3, 3), matrix = matrix )
        
    def _getRotation(self):
        ''' only returns meaningful results if the matrix is orthogonal '''
        return degrees( numpy.arctan2( self.matrix[1][0] / self.scale[0], self.matrix[0][0] / self.scale[0] ) )
        
    def _setRotation(self, angle_in_degree):
        ''' Angle in degrees, NOT radians.
            Don't want to generalize this to n-dimensional rotations now
        '''
        scale = self.scale
        angle_in_radian = radians( angle_in_degree )
        self.matrix[0][:-1] = ( numpy.cos( angle_in_radian ), -numpy.sin( angle_in_radian ) )
        self.matrix[1][:-1] = ( numpy.sin( angle_in_radian ),  numpy.cos( angle_in_radian ) )
        self.matrix[:-1,:-1] *= scale

    rotation = property( _getRotation, _setRotation, )
    
    
class ArbitraryTransform(object):
    ''' An arbitrary transform which transforms the coords by calling a function
        which returns the transformed coords.
        Concatenated by executing the function one after another of the result
        of the previous function applied to the coords.
    '''
    #implements(ITransform)
    def __init__(self, func = lambda x: x):
        self.func = func

    def __call__(self, coords):
        return self.func(coords) 

    def __mul__(self, otherArbitrary):
        return CompoundTransform( self, otherArbitrary )
    
    
class CompoundTransform(object):
    ''' A transform which consists of two other transforms '''
    #implements(ITransform)
    def __init__(self, transform1, transform2):
        self.transform1 = transform1
        self.transform2 = transform2
        
    def __call__(self, coords):
        return self.transform1( self.transform2(coords) )
    
    def __mul__(self, other):
        return CompoundTransform( self, other )
    
    
class LinearAndArbitraryCompoundTransform(CompoundTransform):
    ''' A transform which consists of a linear part and another transform '''
    def __getattr__(self, name):
        #if name in ('transform1', 'transform2'):
        #    return super( CompoundTransform, self ).__getattr__( name )
        
        if hasattr( self.transform1, name ):
            return getattr( self.transform1, name )
        elif hasattr( self.transform2, name ):
            return getattr( self.transform2, name )
        else:
            raise NameError(name)   

    def __setattr__(self, name, value):
        if name in ('transform1', 'transform2'):
            return super( CompoundTransform, self ).__setattr__( name, value )

        if hasattr( self.transform1, name ):
            return setattr( self.transform1, name, value )
        elif hasattr( self.transform2, name ):
            return setattr( self.transform2, name, value )
        else:
            raise NameError(name)   

    def __mul__(self, other):
        return LinearAndArbitraryCompoundTransform( self.transform1, CompoundTransform( self.transform2, other ) )

    def _getInverse(self):
        if hasattr(self.transform2, 'inverse'):
            #return self.__class__( self.transform1.inverse, self.transform2.inverse )
            return CompoundTransform( self.transform2.inverse, self.transform1.inverse )
        else:
            return self.transform1.inverse
    
    inverse = property( _getInverse )


class InverseMercatorTransform(object):
    def __init__(self, longitudeCenter = 0, scaleFactor = 100):
        self.longitudeCenter = longitudeCenter
        self.scaleFactor = scaleFactor

    # can probably be made faster
    def __call__(self, coords):
        def mercator_lat_inv(y):
            #return -numpy.log( numpy.tan( numpy.pi / 4 + lat / 2 ) )
            #return numpy.arcsinh( numpy.tan( lat ) )
            return numpy.arcsin( numpy.tanh( y ) )

        result = numpy.array( coords )
        result /= self.scaleFactor
        result[::,::2] += self.longitudeCenter
        result[::,1::2] = mercator_lat_inv( result[::,1::2] )
                
        return result

    def _getInverse(self):
        return MercatorTransform( self.longitudeCenter, self.scaleFactor )

    inverse = property( _getInverse )

class MercatorTransform(object):
    ''' Implements a mercator projection, see 
        http://en.wikipedia.org/wiki/Mercator_projection . Input coords are
        2-tuples of (longitude, latitude), result is in cartesian system.
        
    '''
    #implements(ITransform)
    def __init__(self, longitudeCenter = 0, scaleFactor = 100):
        self.longitudeCenter = longitudeCenter
        self.scaleFactor = scaleFactor
    
    # can probably be made faster
    def __call__(self, coords):
        def mercator_lat(lat):
            #return -numpy.log( numpy.tan( numpy.pi / 4 + lat / 2 ) )
            #return numpy.arcsinh( numpy.tan( lat ) )
            return numpy.arctanh( numpy.sin( lat ) )

        result = numpy.array( coords )
        result[::,::2] -= self.longitudeCenter
        result[::,1::2] = mercator_lat( result[::,1::2] )
        
        result *= self.scaleFactor
        
        return result

    def _getInverse(self):
        return InverseMercatorTransform( self.longitudeCenter, self.scaleFactor )

    inverse = property( _getInverse )

class ThreeDProjectionTransform(LinearTransform):
    ''' An experimental transform to show that floatcanvas can handle arbitrary
        input coordinats. For example 3-tuples which are 3d positions. These can
        then be projected onto a 2d surface. Could be used to render a 3d wire-
        frame cube.
    '''
    def __init__(self, width, height, fov, znear, zfar):
        LinearTransform.__init__( self, (4,4) )

        self.matrix = m = numpy.zeros( (4,4) )

        aspect = float(width) / height
        right = znear * numpy.tan ( fov / 2 * numpy.pi / 180.0 )
        top = right / aspect

        m[0][0] = 2 * znear / right / 2
        m[1][1] = 2 * znear / top / 2
        m[2][2] = -( zfar + znear ) / ( zfar - znear )

        m[2][3] = -zfar * znear / ( zfar - znear )
        m[3][2] = -1

