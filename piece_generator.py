from piece import Piece
from piece_type import IPiece, JPiece, LPiece, OPiece, TPiece, SPiece, ZPiece


import random


class PieceGenerator:
    PIECES = [OPiece(), TPiece(), IPiece(), LPiece(), JPiece(), SPiece(), ZPiece()]

    def __init__(self):
        self.shuffle()

    def shuffle(self):
        self.bag = PieceGenerator.PIECES.copy()
        random.shuffle(self.bag)

    def next(self):
        if not self.bag:
            self.shuffle()
        return Piece(self.bag.pop())
