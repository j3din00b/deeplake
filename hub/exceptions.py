
class OutOfBoundsError(Exception):
    """Raised upon finding a missing chunk."""
    pass

class AlignmentError(Exception):
    """Raised when there is an Alignment error."""
    pass

class IncompatibleShapes(Exception):
    """Shapes do not match"""
    pass

class IncompatibleBroadcasting(Exception):
    """Broadcasting issue"""
    pass

class IncompatibleTypes(Exception):
    """Types can not cast"""
    pass
