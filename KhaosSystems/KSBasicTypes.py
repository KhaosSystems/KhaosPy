class KSVector(object):
    x: float = 0.0
    y: float = 0.0 
    z: float = 0.0 

    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z