from numpy import iterable

class Vec:
    def __init__(self, X = None, Y = None):
        if Y is not None:
            if X is not None:
                self.X = X
                self.Y = Y
            else:
                raise TypeError("[Vec] X cannot be None when Y is not None!")
        elif X is None:
            self.X = 0
            self.Y = 0
        elif not iterable(X):
            self.X = X
            self.Y = X
        else:
            it = iter(X)
            self.X = next(it)
            self.Y = next(it)

    def tp(self):
        return (self.X, self.Y)

    def __iter__(self):
        return VecIterator(self)

    def __repr__(self) -> str:
        return f"Vec({self.X}, {self.Y})"
    
    def __getitem__(self, idx):
        if idx == 0:
            return self.X
        elif idx == 1:
            return self.Y
        else:
            raise IndexError(f"[Vec] Can only address indices 0 and 1; {idx} is out of range")
    
    def __setitem__(self, idx, val):
        if idx == 0:
            self.X = val
        elif idx == 1:
            self.Y = val
        else:
            raise IndexError(f"[Vec] Can only address indices 0 and 1; {idx} is out of range")


    # Comparison operators

    def __eq__(self, v) -> bool:
        return self.X == v.X and self.Y == v.Y

    def __lt__(self, v) -> bool:
        return self.X < v.X and self.Y < v.Y

    def __le__(self, v) -> bool:
        return self.X <= v.X and self.Y <= v.Y

    def __gt__(self, v) -> bool:
        return self.X > v.X and self.Y > v.Y

    def __ge__(self, v) -> bool:
        return self.X >= v.X and self.Y >= v.Y

    # Arithmetic operators

    def __add__(self, v):
        if type(v) == Vec:
            return Vec(self.X + v.X, self.Y + v.Y)
        else:
            return Vec(self.X + v, self.Y + v)

    def __sub__(self, v):
        if type(v) == Vec:
            return Vec(self.X - v.X, self.Y - v.Y)
        else:
            return Vec(self.X - v, self.Y - v)
    
    def __mul__(self, v):
        if type(v) == Vec:
            return Vec(self.X * v.X, self.Y * v.Y)
        else:
            return Vec(self.X * v, self.Y * v)

    def __div__(self, v):
        if type(v) == Vec:
            return Vec(self.X / v.X, self.Y / v.Y)
        else:
            return Vec(self.X / v, self.Y / v)
    
    def __floordiv__(self, v):
        if type(v) == Vec:
            return Vec(self.X // v.X, self.Y // v.Y)
        else:
            return Vec(self.X // v, self.Y // v)

    # Other helpful functions

    def bound(self, min = None, max = None):
        ret = self
        if min is not None:
            ret = ret.bound_min(min)
        if max is not None:
            ret = ret.bound_max(max)
        return ret

    def bound_min(self, min):
        if type(min) == Vec:
            return Vec(max(self.X, min.X), max(self.Y, min.Y))
        else:
            return Vec(max(self.X, min), max(self.Y, min))

    def bound_max(self, max):
        if type(max) == Vec:
            return Vec(min(self.X, max.X), min(self.Y, max.Y))
        else:
            return Vec(min(self.X, max), min(self.Y, max))

class VecIterator:
    def __init__(self, v: Vec):
        self.v = v
        self.iter = -1
    
    def __next__(self):
        self.iter += 1

        if self.iter == 0:
            return self.v.X
        elif self.iter == 1:
            return self.v.Y
        else:
            raise StopIteration
