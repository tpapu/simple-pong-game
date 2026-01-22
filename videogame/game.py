"""Game objects to create PyGame based games."""

import warnings
import pygame
from .scene import *
from .scenemanager import *
from .pong_scene import *
from .sounds import *


def display_info():
    """Print out information about the display driver and video information."""
    print(f'The display is using the "{pygame.display.get_driver()}" driver.')
    print("Video Info:")
    print(pygame.display.Info())


# If you're interested in using abstract base classes, feel free to rewrite
# these classes.
# For more information about Python Abstract Base classes, see
# https://docs.python.org/3.8/library/abc.html


# pylint: disable=too-few-public-methods
class VideoGame:
    """Base class for creating PyGame games."""

    def __init__(
        self,
        window_width=800,
        window_height=800,
        window_title="Ponged",
    ):
        """Initialize a new game with the given window size and window title."""
        pygame.init()
        self._window_size = (window_width, window_height)
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self._window_size)
        self._title = window_title
        pygame.display.set_caption(self._title)
        self._game_is_over = False
        if not pygame.font:
            warnings.warn("Fonts disabled.", RuntimeWarning)
        if not pygame.mixer:
            warnings.warn("Sound disabled.", RuntimeWarning)
        else:
            pygame.mixer.init()
        self._scene_manager = None

    def run(self):
        """Run the game; the main game loop."""
        raise NotImplementedError


class PongGame(VideoGame):
    """Main pong gaame that controls scene flow."""

    def __init__(self):
        """Initialize the Pong game."""
        super().__init__(
            window_width=800, window_height=600, window_title="Ponged"
        )

        # Create scene manager
        title_scene = TitleScene(self._screen)
        game_scene = GameScene(self._screen)
        gameover_scene = GameOverScene(self._screen)

        self._scene_manager = None

        # load and start BGM
        self._load_bgm()

    def _create_scene(self):
        """Create all scenes for the game."""
        title_scene = TitleScene(self._screen)
        game_scene = GameScene(self._screen)
        gameover_scene = GameOverScene(self._screen)

        self._scene_manager = SceneManager(
            [title_scene, game_scene, gameover_scene]
        )

    def _load_bgm(self):
        """load and play BGM"""
        try:
            print("Loading background music...")
            bgm = generate_bgm()
            pygame.mixer.music.load(bgm)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(loops=-1)  # loop forever
            print("Background music started.")
        except Exception as e:
            print(f"Warning: Could not load background music: {e}")

    def run(self):
        """Run the main game loop, transition through scenes"""

        game_running = True
        while game_running:

            self._create_scene()
            GameOverScene.restart = False

            for scene in self._scene_manager:
                scene.start_scene()

                while scene.is_valid():
                    for event in pygame.event.get():
                        scene.process_event(event)

                    scene.update_scene()

                    scene.draw()
                    scene.render_updates()

                    pygame.display.flip()
                    self._clock.tick(scene.frame_rate()) #sets frame rate

                scene.end_scene()
            if GameOverScene.restart:
                print("Restarting game...")
            else:
                print("Exiting game...")
                game_running = False
        pygame.mixer.music.stop()
        pygame.quit()


# pylint: enable=too-few-public-methods
