import pygame
from timer import Timer
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


class State(Enum):
    PLAYING = 1
    GAME_OVER = 2
    PAUSED = 3


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
        self.big_font = pygame.font.SysFont(pygame.font.get_default_font(), 64)
        self.clock = pygame.time.Clock()
        self.state = State.PLAYING
        self.init_game()

    def init_game(self):
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

        # timers

        self.fall_timer = Timer(Constants.FALL_EVENT)
        self.lockdown_timer = Timer(Constants.LOCKDOWN_EVENT)
        self.left_auto_timer = Timer(Constants.LEFT_AUTO_REPEAT_EVENT)
        self.right_auto_timer = Timer(Constants.RIGHT_AUTO_REPEAT_EVENT)

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
                    self.fall_timer.notify()
                case Constants.LOCKDOWN_EVENT:
                    locked = True
                case Constants.LEFT_AUTO_REPEAT_EVENT:
                    self.auto_repeat_left = True
                case Constants.RIGHT_AUTO_REPEAT_EVENT:
                    self.auto_repeat_right = True

        if self.state == State.PLAYING:
            if keys_down[pygame.K_DOWN]:
                self.fall_speed = Game.fallspeed_from_level(self.level) // 20
            if keys_up[pygame.K_DOWN]:
                self.fall_speed = Game.fallspeed_from_level(self.level)
            if keys_up[pygame.K_RIGHT]:
                self.right_auto_timer.stop()
                self.auto_repeat_right = False
            if keys_up[pygame.K_LEFT]:
                self.left_auto_timer.stop()
                self.auto_repeat_left = False

            if keys_down[pygame.K_p]:
                self.fall_timer.pause()
                self.lockdown_timer.pause()
                self.left_auto_timer.pause()
                self.right_auto_timer.pause()
                self.state = State.PAUSED
                return

            match self.phase:
                case Phase.GENERATION:
                    self.piece = self.piece_generator.next()
                    # check top out conditions
                    if not self.piece.can_fall(self.blocks) or self.piece.is_blocked(
                        self.blocks
                    ):
                        self.state = State.GAME_OVER
                    else:
                        self.piece.fall(self.blocks)
                        self.phase = Phase.FALLING
                        self.fall_timer.start(self.fall_speed)
                case Phase.FALLING | Phase.LOCK:
                    if keys_down[pygame.K_LEFT]:
                        self.piece.move_left(self.blocks)
                        self.left_auto_timer.start(Constants.AUTO_REPEAT_DELAY_MS, 1)

                        # cancel any pre-existing right auto repeat
                        self.right_auto_timer.stop()
                        self.auto_repeat_right = False
                    elif self.auto_repeat_left:
                        self.piece.move_left(self.blocks)

                    if keys_down[pygame.K_RIGHT]:
                        self.piece.move_right(self.blocks)
                        self.right_auto_timer.start(Constants.AUTO_REPEAT_DELAY_MS, 1)
                        # cancel any pre-existing left auto repeat
                        self.left_auto_timer.stop()
                        self.auto_repeat_left = False
                    elif self.auto_repeat_right:
                        self.piece.move_right(self.blocks)

                    if keys_down[pygame.K_UP]:
                        self.piece.rotate_cw(self.blocks)

                    if keys_down[pygame.K_DOWN] or keys_up[pygame.K_DOWN]:
                        self.fall_timer.start(self.fall_speed)

                    if keys_down[pygame.K_SPACE]:
                        while self.piece.fall(self.blocks):
                            pass
                        self.fall_timer.stop()
                        self.phase = Phase.PATTERN

                    if falling and not self.piece.fall(self.blocks):
                        self.fall_timer.stop()
                        if not self.under_lockdown:
                            self.lockdown_lowest_y = self.piece.y
                            self.lockdown_timer.start(Constants.LOCKDOWN_DELAY_MS, 1)
                        else:
                            self.lockdown_timer.resume()
                        self.phase = Phase.LOCK

                    if self.phase == Phase.LOCK:
                        # Movement or rotation can cause piece to continue falling
                        # if piece can fall, pause timer until piece lands on a surface
                        # if piece falls below lowest previously hit y coordinate, reset lockdown
                        if self.piece.can_fall(self.blocks):
                            if self.piece.y - 1 < self.lockdown_lowest_y:
                                self.under_lockdown = False
                                self.lockdown_timer.stop()
                            else:
                                self.lockdown_timer.pause()
                            self.fall_timer.start(self.fall_speed)
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

                    if (
                        self.level < Constants.MAX_LEVEL
                        and self.lines >= self.level * 10
                    ):
                        self.level += 1
                        self.fall_speed = Game.fallspeed_from_level(self.level)

                    self.scoring_action = None
                    self.phase = Phase.GENERATION

        elif self.state == State.PAUSED:
            if keys_down[pygame.K_RETURN] or keys_down[pygame.K_p]:
                self.fall_timer.resume()
                self.lockdown_timer.resume()
                self.left_auto_timer.resume()
                self.right_auto_timer.resume()
                self.state = State.PLAYING

        elif self.state == State.GAME_OVER:
            self.fall_timer.stop()
            self.lockdown_timer.stop()
            self.left_auto_timer.stop()
            self.right_auto_timer.stop()

            if keys_down[pygame.K_RETURN]:
                self.init_game()
                self.state = State.PLAYING
                return

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

        if self.state == State.GAME_OVER:
            Game.draw_game_over_overlay(self.screen, self.big_font, self.font)
        elif self.state == State.PAUSED:
            Game.draw_pause_overlay(self.screen, self.big_font)

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
    def draw_pause_overlay(screen, big_font):
        pause_overlay = pygame.surface.Surface(
            (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT),
            flags=pygame.SRCALPHA,
        )
        pause_overlay.fill((0, 0, 0, 128))
        pause = big_font.render("Paused (P to resume)", True, (255, 255, 255))
        pause_overlay.blit(
            pause,
            pause.get_rect(
                center=(Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2)
            ),
        )
        screen.blit(pause_overlay, (0, 0))

    @staticmethod
    def draw_game_over_overlay(screen, big_font, small_font):
        game_over_overlay = pygame.surface.Surface(
            (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT),
            flags=pygame.SRCALPHA,
        )
        game_over_overlay.fill((0, 0, 0, 128))
        game_over = big_font.render("Game Over", True, (255, 255, 255))
        enter_to_continue = small_font.render(
            "Press Enter to continue", True, (255, 255, 255)
        )
        game_over_overlay.blit(
            game_over,
            game_over.get_rect(
                center=(Constants.SCREEN_WIDTH // 2, Constants.SCREEN_HEIGHT // 2)
            ),
        )
        game_over_overlay.blit(
            enter_to_continue,
            enter_to_continue.get_rect(
                center=(
                    Constants.SCREEN_WIDTH // 2,
                    Constants.SCREEN_HEIGHT // 2 + 100,
                )
            ),
        )
        screen.blit(game_over_overlay, (0, 0))

    @staticmethod
    def fallspeed_from_level(level):
        return int((0.8 - (level - 1) * 0.007) ** (level - 1) * 1000)


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
