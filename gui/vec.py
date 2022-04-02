from __future__ import annotations
from math import floor, ceil

from typing import Union
from numpy import iterable

class Vec:
    def __init__(self, X: Union[float, None] = None, Y: Union[float, None] = None):
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

    def tp(self) -> tuple[float, float]:
        return (self.X, self.Y)

    def __iter__(self):
        return VecIterator(self)

    def __repr__(self) -> str:
        return f"Vec({self.X}, {self.Y})"
    
    def __getitem__(self, idx) -> float:
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

    def __abs__(self) -> Vec:
        return Vec(abs(self.X), abs(self.Y))

    # Comparison operators

    def __eq__(self, v) -> bool:
        if type(v) == Vec:
            return self.X == v.X and self.Y == v.Y
        else:
            return False

    def __lt__(self, v) -> bool:
        return self.X < v.X and self.Y < v.Y

    def __le__(self, v) -> bool:
        return self.X <= v.X and self.Y <= v.Y

    def __gt__(self, v) -> bool:
        return self.X > v.X and self.Y > v.Y

    def __ge__(self, v) -> bool:
        return self.X >= v.X and self.Y >= v.Y

    # Arithmetic operators

    def __add__(self, v) -> Vec:
        if type(v) == Vec:
            return Vec(self.X + v.X, self.Y + v.Y)
        else:
            return Vec(self.X + v, self.Y + v)

    def __sub__(self, v) -> Vec:
        if type(v) == Vec:
            return Vec(self.X - v.X, self.Y - v.Y)
        else:
            return Vec(self.X - v, self.Y - v)
    
    def __mul__(self, v) -> Vec:
        if type(v) == Vec:
            return Vec(self.X * v.X, self.Y * v.Y)
        else:
            return Vec(self.X * v, self.Y * v)

    def __div__(self, v) -> Vec:
        if type(v) == Vec:
            return Vec(self.X / v.X, self.Y / v.Y)
        else:
            return Vec(self.X / v, self.Y / v)
    
    def __floordiv__(self, v) -> Vec:
        if type(v) == Vec:
            return Vec(self.X // v.X, self.Y // v.Y)
        else:
            return Vec(self.X // v, self.Y // v)

    # Other helpful functions

    def in_rect(self, corner_1: Vec, corner_2: Vec) -> bool:
        min, max = Vec.minmax(corner_1, corner_2)
        return self >= min and self <= max

    def floor(self) -> Vec:
        return Vec(floor(self.X), floor(self.Y))

    def ceil(self) -> Vec:
        return Vec(ceil(self.X), ceil(self.Y))

    def bound(self, min = None, max = None) -> Vec:
        ret = self
        if min is not None:
            ret = ret.bound_min(min)
        if max is not None:
            ret = ret.bound_max(max)
        return ret

    def bound_min(self, min) -> Vec:
        if type(min) == Vec:
            return Vec(max(self.X, min.X), max(self.Y, min.Y))
        else:
            return Vec(max(self.X, min), max(self.Y, min))

    def bound_max(self, max) -> Vec:
        if type(max) == Vec:
            return Vec(min(self.X, max.X), min(self.Y, max.Y))
        else:
            return Vec(min(self.X, max), min(self.Y, max))

    def minmax(vec1, vec2) -> tuple[Vec, Vec]:
        return (Vec(min(vec1.X, vec2.X), min(vec1.Y, vec2.Y)),
                Vec(max(vec1.X, vec2.X), max(vec1.Y, vec2.Y)))

class VecIterator:
    def __init__(self, v: Vec):
        self.v = v
        self.iter = -1
    
    def __next__(self) -> float:
        self.iter += 1

        if self.iter == 0:
            return self.v.X
        elif self.iter == 1:
            return self.v.Y
        else:
            raise StopIteration

class VecRange:
    def __init__(self, start: Vec, dvec: Vec, max_iters: int):
        self.pos = start
        self.dvec = dvec
        self.max_iters = max_iters
        self.iter = 0

    def __iter__(self):
        return VecRangeIterator(self)


class VecRangeIterator:
    def __init__(self, range: VecRange):
        self.range = range

    def __next__(self):
        if self.range.iter >= self.range.max_iters:
            raise StopIteration

        ret = self.range.pos
        self.range.pos += self.range.dvec
        self.range.iter += 1
        return ret

# Helpful direction vectors
VEC_DOWN = Vec(0, 1)
VEC_UP = Vec(0, -1)
VEC_LEFT = Vec(-1, 0)
VEC_RIGHT = Vec(1, 0)
