#!/usr/bin/env python3
"""Imports game data and executes it"""
import sys
from videogame import game

def main():
    """Main function to run the Pong game."""
    pong_game = game.PongGame()
    pong_game.run()
    sys.exit(0)

if __name__ == '__main__':
    main()
