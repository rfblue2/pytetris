from piece import Piece
from piece_type import IPiece, JPiece, LPiece, OPiece, TPiece, SPiece, ZPiece


import random


class PieceGenerator:
    PIECES = [OPiece(), TPiece(), IPiece(), LPiece(), JPiece(), SPiece(), ZPiece()]

    def __init__(self):
        self.bag = []
        self.shuffle()

    def shuffle(self):
        new_bag = PieceGenerator.PIECES.copy()
        random.shuffle(new_bag)
        self.bag.extend(new_bag)

    def next(self):
        if not self.bag:
            self.shuffle()
        return Piece(self.bag.pop())

    def peek(self):
        if not self.bag:
            self.shuffle()
        return self.bag[-1]
