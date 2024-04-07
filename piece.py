import pygame
from piece_type import PieceType, Orientation


class Piece:
    START_X = 5
    START_Y = 21

    def __init__(self, type: PieceType):
        """
        x,y block coordinates based on center of top left 3x3 square within 10x20 board
        Initial generation is at (5,21)
        """
        self.x = Piece.START_X
        self.y = Piece.START_Y
        self.type = type
        self.blocks = pygame.sprite.Group()
        self.orientation = Orientation.NORTH
        pattern = type.mask(self.orientation)
        self.blocks.add(
            *[
                Block(x + (self.x - 1), -y + (self.y + 1), type.color())
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

    def rotate_cw(self, blocks):
        new_orientation = Orientation.rotate_cw(self.orientation)
        offsets = self.type.CW_ROTATION_OFFSETS[self.orientation]

        for offset in offsets:
            new_blocks = self.generate_rotated_blocks(
                offset, self.type.mask(new_orientation)
            )
            if all(block.not_collided(blocks) for block in new_blocks):
                self.blocks.empty()
                self.blocks.add(*new_blocks)
                self.orientation = new_orientation
                self.x += offset[0]
                self.y += offset[1]
                return

    def generate_rotated_blocks(self, offset, mask):
        return [
            Block(
                x + (self.x - 1) + offset[0],
                -y + (self.y + 1) + offset[1],
                self.type.color(),
            )
            for y, row in enumerate(mask)
            for x, value in enumerate(row)
            if value
        ]

    def draw(self, screen):
        [block.draw(screen) for block in self.blocks]


class Block(pygame.sprite.Sprite):
    BLOCK_HEIGHT = 40
    BLOCK_WIDTH = 40

    def __init__(self, x, y, color):
        super(Block, self).__init__()
        self.x = x
        self.y = y
        self.surf = pygame.Surface((Block.BLOCK_WIDTH, Block.BLOCK_HEIGHT))
        self.surf.fill(color)

    def fall(self):
        self.y -= 1

    def can_fall(self, blocks):
        return self.y > 1 and (self.x, self.y - 1) not in [
            (block.x, block.y) for block in blocks
        ]

    def move_right(self):
        self.x += 1

    def can_move_right(self, blocks):
        return self.x < 10 and (self.x + 1, self.y) not in [
            (block.x, block.y) for block in blocks
        ]

    def move_left(self):
        self.x -= 1

    def can_move_left(self, blocks):
        return self.x > 1 and (self.x - 1, self.y) not in [
            (block.x, block.y) for block in blocks
        ]

    def not_collided(self, blocks):
        return (
            self.x > 0
            and self.x <= 10
            and self.y > 0
            and (
                self.x,
                self.y,
            )
            not in [(block.x, block.y) for block in blocks]
        )

    def draw(self, screen):
        screen.blit(
            self.surf,
            (
                (self.x - 1) * Block.BLOCK_WIDTH,
                (20 - self.y) * Block.BLOCK_HEIGHT,
            ),
        )
