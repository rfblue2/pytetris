import pygame
from collections import defaultdict
from enum import Enum
from piece import Block
from piece_generator import PieceGenerator


class Constants:
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    SCREEN_WIDTH = BOARD_WIDTH * Block.BLOCK_WIDTH + 200
    SCREEN_HEIGHT = BOARD_HEIGHT * Block.BLOCK_HEIGHT

    FALL_SPEED_MS = 1000
    AUTO_REPEAT_DELAY_MS = 300
    LOCKDOWN_DELAY_MS = 500

    FALL_EVENT = pygame.USEREVENT + 1
    LOCKDOWN_EVENT = pygame.USEREVENT + 2
    LEFT_AUTO_REPEAT_EVENT = pygame.USEREVENT + 3
    RIGHT_AUTO_REPEAT_EVENT = pygame.USEREVENT + 4


class Phase(Enum):
    GENERATION = 1
    FALLING = 2
    LOCK = 3
    PATTERN = 4
    ELIMINATE = 5
    COMPLETION = 6


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.phase = Phase.GENERATION
        self.piece_generator = PieceGenerator()
        self.piece = None
        self.blocks = pygame.sprite.Group()
        self.running = True
        self.auto_repeat_left = False
        self.auto_repeat_right = False
        self.fall_speed = Constants.FALL_SPEED_MS
        self.hit_list = []

        # lockdown state:
        # TODO: Implement extended placement (15 move limit before lockdown)
        # lowest y coordinate hit by piece under lock down
        self.lockdown_lowest_y = 0
        self.under_lockdown = False
        self.lockdown_start_time = 0

    def run(self):
        while self.running:
            self.loop()
        pygame.quit()

    def loop(self):
        falling = False
        locked = False
        keys_down = defaultdict(bool)
        keys_up = defaultdict(bool)
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    keys_down[event.key] = True
                case pygame.KEYUP:
                    keys_up[event.key] = True
                case Constants.FALL_EVENT:
                    falling = True
                case Constants.LOCKDOWN_EVENT:
                    locked = True
                case Constants.LEFT_AUTO_REPEAT_EVENT:
                    self.auto_repeat_left = True
                case Constants.RIGHT_AUTO_REPEAT_EVENT:
                    self.auto_repeat_right = True

        Game.draw_board(self.screen)

        if keys_down[pygame.K_DOWN]:
            self.fall_speed = Constants.FALL_SPEED_MS // 20
        if keys_up[pygame.K_DOWN]:
            self.fall_speed = Constants.FALL_SPEED_MS
        if keys_up[pygame.K_RIGHT]:
            Game.stop_timer(Constants.RIGHT_AUTO_REPEAT_EVENT)
            self.auto_repeat_right = False
        if keys_up[pygame.K_LEFT]:
            Game.stop_timer(Constants.LEFT_AUTO_REPEAT_EVENT)
            self.auto_repeat_left = False

        match self.phase:
            case Phase.GENERATION:
                self.piece = self.piece_generator.next()
                self.piece.fall(self.blocks)
                self.phase = Phase.FALLING
                pygame.time.set_timer(Constants.FALL_EVENT, self.fall_speed)
            case Phase.FALLING | Phase.LOCK:
                if keys_down[pygame.K_LEFT]:
                    self.piece.move_left(self.blocks)
                    pygame.time.set_timer(
                        Constants.LEFT_AUTO_REPEAT_EVENT, Constants.AUTO_REPEAT_DELAY_MS
                    )

                    # cancel any pre-existing right auto repeat
                    Game.stop_timer(Constants.RIGHT_AUTO_REPEAT_EVENT)
                    self.auto_repeat_right = False
                elif self.auto_repeat_left:
                    self.piece.move_left(self.blocks)

                if keys_down[pygame.K_RIGHT]:
                    self.piece.move_right(self.blocks)
                    pygame.time.set_timer(
                        Constants.RIGHT_AUTO_REPEAT_EVENT,
                        Constants.AUTO_REPEAT_DELAY_MS,
                    )
                    # cancel any pre-existing left auto repeat
                    Game.stop_timer(Constants.LEFT_AUTO_REPEAT_EVENT)
                    self.auto_repeat_left = False
                elif self.auto_repeat_right:
                    self.piece.move_right(self.blocks)

                if keys_down[pygame.K_UP]:
                    self.piece.rotate_cw(self.blocks)

                if keys_down[pygame.K_DOWN] or keys_up[pygame.K_DOWN]:
                    pygame.time.set_timer(Constants.FALL_EVENT, self.fall_speed)

                if keys_down[pygame.K_SPACE]:
                    while self.piece.fall(self.blocks):
                        pass
                    pygame.time.set_timer(Constants.FALL_EVENT, 0)
                    self.phase = Phase.PATTERN

                if falling and not self.piece.fall(self.blocks):
                    Game.stop_timer(Constants.FALL_EVENT)
                    if not self.under_lockdown:
                        self.lockdown_lowest_y = self.piece.y
                        self.lockdown_start_time = pygame.time.get_ticks()
                    pygame.time.set_timer(
                        Constants.LOCKDOWN_EVENT,
                        self.lockdown_start_time
                        + Constants.LOCKDOWN_DELAY_MS
                        - pygame.time.get_ticks(),
                    )
                    self.phase = Phase.LOCK

                if self.phase == Phase.LOCK:
                    # Movement or rotation can cause piece to continue falling
                    # if piece can fall, pause timer until piece lands on a surface
                    # if piece falls below lowest previously hit y coordinate, reset lockdown
                    if self.piece.can_fall(self.blocks):
                        if self.piece.y - 1 < self.lockdown_lowest_y:
                            self.under_lockdown = False
                        Game.stop_timer(Constants.LOCKDOWN_EVENT)
                        pygame.time.set_timer(Constants.FALL_EVENT, self.fall_speed)
                        self.phase = Phase.FALLING

                    if locked:
                        self.under_lockdown = False
                        self.phase = Phase.PATTERN
            case Phase.PATTERN:
                self.blocks.add(*self.piece.blocks.sprites())
                self.piece.blocks.empty()
                for row in range(Constants.BOARD_HEIGHT):
                    block_row = [block for block in self.blocks if block.y == row]
                    if len(block_row) == Constants.BOARD_WIDTH:
                        self.hit_list.extend(block_row)
                self.phase = Phase.ELIMINATE
            case Phase.ELIMINATE:
                eliminated_rows = set(block.y for block in self.hit_list)
                for block in self.hit_list:
                    block.kill()
                self.hit_list = []
                for eliminated_row in sorted(eliminated_rows, reverse=True):
                    for block in self.blocks:
                        if block.y > eliminated_row:
                            block.fall()

                self.phase = Phase.COMPLETION
            case Phase.COMPLETION:
                # TODO
                self.phase = Phase.GENERATION

        self.piece.draw(self.screen)
        [block.draw(self.screen) for block in self.blocks.sprites()]

        self.clock.tick(60)
        pygame.display.flip()

    @staticmethod
    def draw_board(screen):
        screen.fill((0, 0, 0))

        # draw frame
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            (0, 0, Constants.BOARD_WIDTH * Block.BLOCK_WIDTH, Constants.SCREEN_HEIGHT),
            1,
        )

        # draw grid
        for x in range(0, Constants.BOARD_WIDTH):
            for y in range(0, Constants.BOARD_HEIGHT):
                pygame.draw.rect(
                    screen,
                    (100, 100, 100),
                    (
                        x * Block.BLOCK_WIDTH,
                        y * Block.BLOCK_HEIGHT,
                        Block.BLOCK_WIDTH,
                        Block.BLOCK_HEIGHT,
                    ),
                    1,
                )

    @staticmethod
    def stop_timer(event_id):
        pygame.time.set_timer(event_id, 0)


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
