from abc import ABC, abstractmethod
from enum import Enum


class Orientation(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    @staticmethod
    def rotate_cw(orientation):
        match orientation:
            case Orientation.NORTH:
                return Orientation.EAST
            case Orientation.EAST:
                return Orientation.SOUTH
            case Orientation.SOUTH:
                return Orientation.WEST
            case Orientation.WEST:
                return Orientation.NORTH


class PieceType(ABC):

    @property
    @abstractmethod
    def CW_ROTATION_OFFSETS(cls):
        """
        Returns offsets of next orientation position after rotation
        """
        pass

    @property
    @abstractmethod
    def NAME(cls):
        pass

    @abstractmethod
    def color(self):
        pass

    @abstractmethod
    def mask(self, orientation):
        pass


class OPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0)],
        Orientation.EAST: [(0, 0)],
        Orientation.SOUTH: [(0, 0)],
        Orientation.WEST: [(0, 0)],
    }

    NAME = "O"

    def color(self):
        return (255, 255, 0)

    def mask(self, orientation):
        return [[0, 1, 1], [0, 1, 1], [0, 0, 0]]


class TPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0), (-1, 0), (-1, 1), (0, 0), (-1, -2)],
        Orientation.EAST: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        Orientation.SOUTH: [(0, 0), (-1, 0), (0, 0), (0, -2), (1, -2)],
        Orientation.WEST: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    }

    NAME = "T"

    def color(self):
        return (255, 0, 255)

    def mask(self, orientation):
        match orientation:
            case Orientation.NORTH:
                return [[0, 1, 0], [1, 1, 1], [0, 0, 0]]
            case Orientation.EAST:
                return [[0, 1, 0], [0, 1, 1], [0, 1, 0]]
            case Orientation.SOUTH:
                return [[0, 0, 0], [1, 1, 1], [0, 1, 0]]
            case Orientation.WEST:
                return [[0, 1, 0], [1, 1, 0], [0, 1, 0]]
            case _:
                raise ValueError("Invalid orientation")


class IPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        Orientation.EAST: [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        Orientation.SOUTH: [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        Orientation.WEST: [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
    }

    NAME = "I"

    def color(self):
        return (0, 255, 255)

    def mask(self, orientation):
        match orientation:
            case Orientation.NORTH:
                return [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]]
            case Orientation.EAST:
                return [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]]
            case Orientation.SOUTH:
                return [[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]]
            case Orientation.WEST:
                return [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]


class LPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        Orientation.EAST: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        Orientation.SOUTH: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        Orientation.WEST: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    }

    NAME = "L"

    def color(self):
        return (255, 165, 0)

    def mask(self, orientation):
        match orientation:
            case Orientation.NORTH:
                return [[0, 0, 1], [1, 1, 1], [0, 0, 0]]
            case Orientation.EAST:
                return [[0, 1, 0], [0, 1, 0], [0, 1, 1]]
            case Orientation.SOUTH:
                return [[0, 0, 0], [1, 1, 1], [1, 0, 0]]
            case Orientation.WEST:
                return [[1, 1, 0], [0, 1, 0], [0, 1, 0]]


class JPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        Orientation.EAST: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        Orientation.SOUTH: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        Orientation.WEST: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    }

    NAME = "J"

    def color(self):
        return (0, 0, 255)

    def mask(self, orientation):
        match orientation:
            case Orientation.NORTH:
                return [[1, 0, 0], [1, 1, 1], [0, 0, 0]]
            case Orientation.EAST:
                return [[0, 1, 1], [0, 1, 0], [0, 1, 0]]
            case Orientation.SOUTH:
                return [[0, 0, 0], [1, 1, 1], [0, 0, 1]]
            case Orientation.WEST:
                return [[0, 1, 0], [0, 1, 0], [1, 1, 0]]


class SPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        Orientation.EAST: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        Orientation.SOUTH: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        Orientation.WEST: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    }

    NAME = "S"

    def color(self):
        return (0, 255, 0)

    def mask(self, orientation):
        match orientation:
            case Orientation.NORTH:
                return [[0, 1, 1], [1, 1, 0], [0, 0, 0]]
            case Orientation.EAST:
                return [[0, 1, 0], [0, 1, 1], [0, 0, 1]]
            case Orientation.SOUTH:
                return [[0, 0, 0], [0, 1, 1], [1, 1, 0]]
            case Orientation.WEST:
                return [[1, 0, 0], [1, 1, 0], [0, 1, 0]]


class ZPiece(PieceType):
    CW_ROTATION_OFFSETS = {
        Orientation.NORTH: [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        Orientation.EAST: [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        Orientation.SOUTH: [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        Orientation.WEST: [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
    }

    NAME = "Z"

    def color(self):
        return (255, 0, 0)

    def mask(self, orientation):
        match orientation:
            case Orientation.NORTH:
                return [[1, 1, 0], [0, 1, 1], [0, 0, 0]]
            case Orientation.EAST:
                return [[0, 0, 1], [0, 1, 1], [0, 1, 0]]
            case Orientation.SOUTH:
                return [[0, 0, 0], [1, 1, 0], [0, 1, 1]]
            case Orientation.WEST:
                return [[0, 1, 0], [1, 1, 0], [1, 0, 0]]
