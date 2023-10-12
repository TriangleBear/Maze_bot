import pygame
from pygame.locals import *
import sys
from config import config
from collections import deque
from bfs import bfs
from dfs import dfs
from a_star import a_star

def drawer():
    pygame.init()
    # Fetch 'w' and 'h' from the config dictionary
    board_width = config['board']['w']
    board_height = config['board']['h']
    win = pygame.display.set_mode((board_width, board_height))
    pygame.draw.rect(win, (255, 255, 255), (0, 0, win.get_width(), win.get_height()))  # Fill the entire window with white
    drag = False
    startEnd = []

    font = pygame.font.Font(None, 36)

    while len(startEnd) < 2:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                coordinate = event.pos
                pygame.draw.rect(win, (0, 0, 0), (*coordinate, 1, 1))  # Draw a black pixel at the coordinate
                startEnd.append(coordinate)

    walls = set()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                drag = True
            elif event.type == pygame.MOUSEBUTTONUP:
                drag = False
            elif event.type == pygame.MOUSEMOTION:
                if drag:
                    coordinate = event.pos
                    pygame.draw.rect(win, (0, 0, 0), (*coordinate, 1, 1))  # Draw a black pixel at the coordinate
                    walls.add(coordinate)
            elif event.type == pygame.KEYDOWN:
                if config['algo'] == 'bfs':
                    bfs(win, startEnd, walls)
                if config['algo'] == 'dfs':
                    dfs(win, startEnd, walls)
                if config['algo'] == 'astar':
                    a_star(win, startEnd, walls)

if __name__ == "__main__":
    drawer()
