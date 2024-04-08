import pygame
from block import Block
from piece_type import PieceType, Orientation


class Piece:
    START_X = 5
    START_Y = 21

    def __init__(
        self,
        type: PieceType,
        x=START_X,
        y=START_Y,
        orientation=Orientation.NORTH,
        style=Block.Style.FILL,
    ):
        """
        x,y block coordinates based on center of top left 3x3 square within 10x20 board
        Initial generation is at (5,21)
        """
        self.x = x
        self.y = y
        self.type = type
        self.style = style
        self.blocks = pygame.sprite.Group()
        self.orientation = orientation
        pattern = type.mask(self.orientation)
        self.blocks.add(
            *[
                Block(x + (self.x - 1), -y + (self.y + 1), type.color(), style)
                for y, row in enumerate(pattern)
                for x, value in enumerate(row)
                if value
            ]
        )

    def can_fall(self, blocks):
        return all(block.can_fall(blocks) for block in self.blocks)

    def fall(self, blocks):
        if self.can_fall(blocks):
            [block.fall() for block in self.blocks]
            self.y -= 1
            return True
        else:
            return False

    def move_right(self, blocks):
        if all(block.can_move_right(blocks) for block in self.blocks):
            [block.move_right() for block in self.blocks]
            self.x += 1

    def move_left(self, blocks):
        if all(block.can_move_left(blocks) for block in self.blocks):
            [block.move_left() for block in self.blocks]
            self.x -= 1

    def is_blocked(self, blocks):
        return not all(block.not_collided(blocks) for block in self.blocks)

    def rotate_cw(self, blocks):
        new_orientation = Orientation.rotate_cw(self.orientation)
        offsets = self.type.CW_ROTATION_OFFSETS[self.orientation]

        for offset in offsets:
            new_blocks = self.__generate_rotated_blocks(
                offset, self.type.mask(new_orientation)
            )
            if all(block.not_collided(blocks) for block in new_blocks):
                self.blocks.empty()
                self.blocks.add(*new_blocks)
                self.orientation = new_orientation
                self.x += offset[0]
                self.y += offset[1]
                return

    def __generate_rotated_blocks(self, offset, mask):
        return [
            Block(
                x + (self.x - 1) + offset[0],
                -y + (self.y + 1) + offset[1],
                self.type.color(),
                self.style,
            )
            for y, row in enumerate(mask)
            for x, value in enumerate(row)
            if value
        ]

    def draw(self, screen):
        [block.draw(screen) for block in self.blocks]
