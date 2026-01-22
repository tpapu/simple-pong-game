"""Pong game scenes: title, gameplay, and game over."""

import pygame
import numpy as np
from .scene import *
from videogame import rgbcolors
from .sounds import *


class TitleScene(PressAnyKeyToExitScene):
    """Shows the title and instructions."""

    def __init__(self, screen):
        """Initialize the title scene."""
        super().__init__(screen, rgbcolors.black)
        self._title_font = pygame.font.Font(None, 74)
        self._instruction_font = pygame.font.Font(None, 36)

    def draw(self):
        """Draw title text"""
        super().draw()  # Draw black background

        # Draw the title "PONG"
        title_text = self._title_font.render("PONG", True, rgbcolors.white)
        title_rect = title_text.get_rect(
            center=(self._screen.get_width() // 2, 150)
        )
        self._screen.blit(title_text, title_rect)

        # Draw instructions
        instruction_text = [
            "You are on the LEFT!",
            "W/S to move UP/DOWN",
            "",
            "First to 3 points wins!",
            "",
            "Press any key to start",
        ]
        y_position = 250
        for line in instruction_text:
            instructions = self._instruction_font.render(
                line, True, rgbcolors.white
            )
            instruction_rect = instructions.get_rect(
                center=(self._screen.get_width() // 2, y_position)
            )
            self._screen.blit(instructions, instruction_rect)
            y_position += 40


class GameScene(Scene):
    """The actual Pong gameplay scene."""

    def __init__(self, screen):
        """Creates all the objects for the gameplay scene."""
        super().__init__(screen, rgbcolors.black)

        # Score
        self.left_score = 0
        self.right_score = 0
        self._winning_score = 3

        # Left/Right paddle and ball (x,y, width, height)
        self.left_paddle = pygame.Rect(30, 260, 15, 80)
        self.right_paddle = pygame.Rect(755, 260, 15, 80)
        self.ball = pygame.Rect(392, 292, 15, 15)

        # Ball velocity
        self.ball_velocity_x = 5
        self.ball_velocity_y = 5

        # paddle speed
        self._paddle_speed = 7

        # score font
        self._score_font = pygame.font.Font(None, 74)

        # load sound effects
        self._load_sounds()

    def _load_sounds(self):
        """Load game sound effects (not BGM)."""
        try:
            game_sounds = load_game_sounds()
            self._paddle_sound = game_sounds["paddle_hit"]
            self._wall_sound = game_sounds["wall_hit"]
            self._score_sound = game_sounds["score"]
            print("Game sounds loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load sounds: {e}")
            self._paddle_sound = None
            self._wall_sound = None
            self._score_sound = None

    def _reset_ball(self):
        """Reset ball to center of screen."""
        self.ball.x = self._screen.get_width() // 2 - self.ball.width // 2
        self.ball.y = self._screen.get_height() // 2 - self.ball.height // 2
        # Reset ball velocity
        self.ball_velocity_x *= -1

    def process_event(self, event):
        """Process game events."""
        super().process_event(event)

    def update_scene(self):
        """Add movement to paddles and ball"""
        # Get key presses
        keys = pygame.key.get_pressed()

        # Player paddle
        if keys[pygame.K_w] and self.left_paddle.top > 0:
            self.left_paddle.y -= self._paddle_speed
        if (
            keys[pygame.K_s]
            and self.left_paddle.bottom < self._screen.get_height()
        ):
            self.left_paddle.y += self._paddle_speed

        # AI paddle, follows the ball
        halfway_point = self._screen.get_width() // 2

        if self.ball.x > halfway_point:
            if (
                self.right_paddle.centery < self.ball.centery
                and self.right_paddle.top < self._screen.get_height()
            ):
                self.right_paddle.y += self._paddle_speed - 3.7
            elif (
                self.ball.centery < self.right_paddle.centery
                and self.right_paddle.bottom > 0
            ):
                self.right_paddle.y -= self._paddle_speed - 3.7

        # Ball movement
        self.ball.x += self.ball_velocity_x
        self.ball.y += self.ball_velocity_y

        # Ball collision detection
        if self.ball.top <= 0 or self.ball.bottom >= self._screen.get_height():
            self.ball_velocity_y *= -1  # Bounce off top/bottom walls
            if self._wall_sound:
                self._wall_sound.play()

        if self.ball.colliderect(self.left_paddle) or self.ball.colliderect(
            self.right_paddle
        ):
            self.ball_velocity_x *= -1  # Bounce off paddles
            if self._paddle_sound:
                self._paddle_sound.play()

        # Check for scoring
        if self.ball.left <= 0:
            self._score_sound.play()
            self.right_score += 1
            self._reset_ball()
        elif self.ball.right >= self._screen.get_width():
            self._score_sound.play()
            self.left_score += 1
            self._reset_ball()

        # Check for game over
        if self.left_score >= self._winning_score:
            GameOverScene.winner = "Left Player"
            self._is_valid = False
        elif self.right_score >= self._winning_score:
            GameOverScene.winner = "Right Player"
            self._is_valid = False

    def draw(self):
        """Draw everything on screen."""
        # Draw black background
        super().draw()

        # Draw center line (dashed)
        center_x = self._screen.get_width() // 2
        for y in range(0, self._screen.get_height(), 20):
            pygame.draw.rect(
                self._screen,
                rgbcolors.white,
                pygame.Rect(center_x - 2, y, 4, 10),
            )

        # Drawing the object here, paddles and ball
        pygame.draw.rect(self._screen, rgbcolors.blue, self.left_paddle)
        pygame.draw.rect(self._screen, rgbcolors.red, self.right_paddle)
        pygame.draw.rect(self._screen, rgbcolors.purple, self.ball)

        # Draw scores
        left_score_text = self._score_font.render(
            str(self.left_score), True, rgbcolors.white
        )
        self._screen.blit(left_score_text, (self._screen.get_width() // 4, 30))

        right_score_text = self._score_font.render(
            str(self.right_score), True, rgbcolors.white
        )
        right_score_rect = right_score_text.get_rect()
        right_score_rect.topleft = (3 * self._screen.get_width() // 4, 30)
        self._screen.blit(right_score_text, right_score_rect)


class GameOverScene(PressAnyKeyToExitScene):
    """Shows who won."""

    winner = "Left Player"
    restart = False

    def __init__(self, screen):
        """Initialize the game over scene."""

        Scene.__init__(self, screen, rgbcolors.black)
        # Game over screen stuff
        self._title_font = pygame.font.Font(None, 74)
        self.winner_font = pygame.font.Font(None, 60)
        self._instruction_font = pygame.font.Font(None, 36)

    def process_event(self, event):
        """Process game over event."""
        super().process_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                GameOverScene.restart = True
                self._is_valid = False
            elif event.key == pygame.K_ESCAPE:
                GameOverScene.restart = False
                self._is_valid = False

    def draw(self):
        """Draw game over text"""
        super().draw()
        # Draw "Game Over!" title
        title_text = self._title_font.render(
            "Game Over!", True, rgbcolors.white
        )
        title_rect = title_text.get_rect(
            center=(self._screen.get_width() // 2, 150)
        )
        self._screen.blit(title_text, title_rect)

        # Draw winner text
        winner_text = self.winner_font.render(
            f"{GameOverScene.winner} Wins!", True, rgbcolors.white
        )
        winner_rect = winner_text.get_rect(
            center=(self._screen.get_width() // 2, 250)
        )
        self._screen.blit(winner_text, winner_rect)

        # Draw instructions
        instruction_text1 = self._instruction_font.render(
            "Press R to play again", True, rgbcolors.white
        )
        instruction_rect1 = instruction_text1.get_rect(
            center=(self._screen.get_width() // 2, 370)
        )
        self._screen.blit(instruction_text1, instruction_rect1)
        instruction_text2 = self._instruction_font.render(
            "Press ESC to quit", True, rgbcolors.white
        )
        instruction_rect2 = instruction_text2.get_rect(
            center=(self._screen.get_width() // 2, 410)
        )
        self._screen.blit(instruction_text2, instruction_rect2)
