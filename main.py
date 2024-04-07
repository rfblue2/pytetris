import pygame
from collections import defaultdict
from enum import Enum
from piece import Block
from piece_generator import PieceGenerator


class Constants:
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    SCREEN_WIDTH = BOARD_WIDTH * Block.BLOCK_WIDTH + 400
    SCREEN_HEIGHT = BOARD_HEIGHT * Block.BLOCK_HEIGHT

    MAX_LEVEL = 15

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


class ScoringActions(Enum):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    TETRIS = 4


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(
            (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT)
        )
        self.board = pygame.Surface(
            (
                Constants.BOARD_WIDTH * Block.BLOCK_WIDTH,
                Constants.BOARD_HEIGHT * Block.BLOCK_HEIGHT,
            )
        )
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 24)
        self.clock = pygame.time.Clock()
        self.phase = Phase.GENERATION
        self.piece_generator = PieceGenerator()
        self.piece = None
        self.blocks = pygame.sprite.Group()
        self.running = True
        self.auto_repeat_left = False
        self.auto_repeat_right = False

        # scoring, levels, statistics
        self.level = 1
        self.score = 0
        self.lines = 0
        self.scoring_action = None

        self.fall_speed = Game.fallspeed_from_level(self.level)
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

        if keys_down[pygame.K_DOWN]:
            self.fall_speed = Game.fallspeed_from_level(self.level) // 20
        if keys_up[pygame.K_DOWN]:
            self.fall_speed = Game.fallspeed_from_level(self.level)
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

                if len(eliminated_rows) == 1:
                    self.scoring_action = ScoringActions.SINGLE
                elif len(eliminated_rows) == 2:
                    self.scoring_action = ScoringActions.DOUBLE
                elif len(eliminated_rows) == 3:
                    self.scoring_action = ScoringActions.TRIPLE
                elif len(eliminated_rows) == 4:
                    self.scoring_action = ScoringActions.TETRIS

                self.lines += len(eliminated_rows)

                self.phase = Phase.COMPLETION
            case Phase.COMPLETION:
                match self.scoring_action:
                    case ScoringActions.SINGLE:
                        self.score += 100
                    case ScoringActions.DOUBLE:
                        self.score += 300
                    case ScoringActions.TRIPLE:
                        self.score += 500
                    case ScoringActions.TETRIS:
                        self.score += 800

                if self.level < Constants.MAX_LEVEL and self.lines >= self.level * 10:
                    self.level += 1
                    self.fall_speed = Game.fallspeed_from_level(self.level)

                self.scoring_action = None
                self.phase = Phase.GENERATION

        self.screen.fill(pygame.Color("black"))
        Game.draw_board(self.board)
        self.piece.draw(self.board)
        [block.draw(self.board) for block in self.blocks.sprites()]

        self.screen.blit(self.board, (200, 0))
        level = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        score = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lines = self.font.render(f"Lines: {self.lines}", True, (255, 255, 255))
        self.screen.blit(level, (10, 10))
        self.screen.blit(score, (10, 30))
        self.screen.blit(lines, (10, 50))

        self.clock.tick(60)
        pygame.display.flip()

    @staticmethod
    def draw_board(board):
        board.fill((0, 0, 0))

        # draw frame
        pygame.draw.rect(
            board,
            (255, 255, 255),
            (0, 0, Constants.BOARD_WIDTH * Block.BLOCK_WIDTH, Constants.SCREEN_HEIGHT),
            1,
        )

        # draw grid
        for x in range(0, Constants.BOARD_WIDTH):
            for y in range(0, Constants.BOARD_HEIGHT):
                pygame.draw.rect(
                    board,
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

    @staticmethod
    def fallspeed_from_level(level):
        return int((0.8 - (level - 1) * 0.007) ** (level - 1) * 1000)


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
