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
    @abstractmethod
    def color(self):
        pass

    @abstractmethod
    def mask(self, orientation):
        pass

    @abstractmethod
    def rotate_cw(self, orientation, point):
        """
        Returns offsets of next orientation position after rotation
        """
        pass


class OPiece(PieceType):
    def color(self):
        return (255, 255, 0)

    def mask(self, orientation):
        return [[0, 1, 1], [0, 1, 1], [0, 0, 0]]

    def rotate_cw(self, orientation, point):
        return (0, 0)


class TPiece(PieceType):
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

    def rotate_cw(self, orientation, point):
        if point == 1:
            return (0, 0)
        # TODO other points


class IPiece(PieceType):
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

    def rotate_cw(self, orientation, point):
        if point == 1:
            return (0, 0)
        # TODO other points


class LPiece(PieceType):
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

    def rotate_cw(self, orientation, point):
        if point == 1:
            return (0, 0)
        # TODO other points


class JPiece(PieceType):
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

    def rotate_cw(self, orientation, point):
        if point == 1:
            return (0, 0)
        # TODO other points


class SPiece(PieceType):
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

    def rotate_cw(self, orientation, point):
        if point == 1:
            return (0, 0)
        # TODO other points


class ZPiece(PieceType):
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

    def rotate_cw(self, orientation, point):
        if point == 1:
            return (0, 0)
        # TODO other points
