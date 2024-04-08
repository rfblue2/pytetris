import pygame
from constants import Constants


from enum import Enum


class Block(pygame.sprite.Sprite):
    Style = Enum("Style", ["FILL", "GHOST"])

    def __init__(self, x, y, color, style):
        super(Block, self).__init__()
        self.x = x
        self.y = y
        self.surf = pygame.Surface((Constants.BLOCK_WIDTH, Constants.BLOCK_HEIGHT))
        if style == Block.Style.FILL:
            self.surf.fill(color)
        else:  # ghost
            self.surf.fill((255, 255, 255))
            self.surf.set_alpha(128)

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
            and self.x <= Constants.BOARD_WIDTH
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
                (self.x - 1) * Constants.BLOCK_WIDTH,
                (Constants.BOARD_HEIGHT - self.y) * Constants.BLOCK_HEIGHT,
            ),
        )
