import sys
import pygame
from pygame import Surface


# Constants
SCREEN_WIDTH = 256      # How wide the screen is in "virtual pixels"
SCREEN_HEIGHT = 240     # How tall the screen is in "virtual pixels"
SCREEN_ZOOM = 2         # Scale factor of the whole screen
FRAMES_PER_SECOND = 40  # How many frames to draw per second
CANVAS_ZOOM = 4         # Scale factor of the art canvas

# Dimensions of the glyphs
GLYPH_WIDTH = 20        # How wide a glyph 
GLYPH_HEIGHT = 20       # How tall a glyph is

# Dimensions of the art canvas
CANVAS_WIDTH = GLYPH_WIDTH * CANVAS_ZOOM
CANVAS_HEIGHT = GLYPH_HEIGHT * CANVAS_ZOOM
CANVAS_X = SCREEN_WIDTH - 8 - CANVAS_WIDTH
CANVAS_Y = SCREEN_HEIGHT - 8 - CANVAS_HEIGHT


# Glyphs in the language
glyphs = {
    'fire':    None, 
    'water':   None,
    'house':   None,
    'person':  None
}


# Art canvas state
selection_active = False   # Whether a pixel is selected
selection_x = 0            # The x coordinate of the selected pixel
selection_y = 0            # The y coordinate of the selected pixel

canvas_pixels = []
for y in range(0, CANVAS_HEIGHT):
    canvas_pixels.append([])
    for x in range(0, CANVAS_WIDTH):
        canvas_pixels[y].append(0)


# Input handling
mouse_x = 0        # The x coordinate of the mouse (in virtual pixels)
mouse_y = 0        # The y coordinate of the mouse (in virtual pixels)
mouse_held = False # Whether the mouse button is being held down


# Initialize Pygame
pygame.init()
dimensions = (SCREEN_WIDTH * SCREEN_ZOOM,
              SCREEN_HEIGHT * SCREEN_ZOOM)
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()
debug_font = pygame.font.Font(None, 20)
virtual_screen = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
scaled_screen = Surface(dimensions, 0, virtual_screen)

while True:
    # Handle user input (mouse and quitting).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            mouse_x = event.pos[0] / SCREEN_ZOOM
            mouse_y = event.pos[1] / SCREEN_ZOOM

            if mouse_x >= CANVAS_X \
               and mouse_x < CANVAS_X + CANVAS_WIDTH \
               and mouse_y >= CANVAS_Y \
               and mouse_y < CANVAS_Y + CANVAS_HEIGHT:
                selection_active = True
                selection_x = (mouse_x - CANVAS_X) / CANVAS_ZOOM
                selection_y = (mouse_y - CANVAS_Y) / CANVAS_ZOOM
            else:
                selection_active = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False

    # If the user is painting, place a pixel.
    if selection_active and mouse_held:
        canvas_pixels[selection_y][selection_x] = 1

    # Draw the screen.
    virtual_screen.fill((0, 0, 0))

    # In glyph-drawing mode, draw the canvas.
    virtual_screen.fill((255, 255, 255),
                        (CANVAS_X, CANVAS_Y,
                         CANVAS_WIDTH, CANVAS_HEIGHT))

    for y in range(len(canvas_pixels)):
        for x in range(len(canvas_pixels[0])):
            pixel = canvas_pixels[y][x]

            if pixel == 0:
                # Transparent pixel
                color = None
            elif pixel == 1:
                # Black pixel
                color = (0, 0, 0)
            elif pixel == 2:
                # Red pixel
                color = (255, 0, 0)
            elif pixel == 3:
                # Green pixel
                color = (0, 255, 0)
            elif pixel == 4:
                # Brown pixel
                color = (125, 100, 0)

            if color is not None:
                virtual_screen.fill(color,
                                    (CANVAS_X
                                     + (x * CANVAS_ZOOM),
                                     CANVAS_Y
                                     + (y * CANVAS_ZOOM),
                                     CANVAS_ZOOM, CANVAS_ZOOM))

    # Draw debug messages at the top-left.
    debug_lines = [
        'cursor: (%d, %d)' % (mouse_x, mouse_y)
    ]

    if selection_active:
        debug_lines += ['selection: (%d, %d)'
                        % (selection_x, selection_y)]

    line_num = 0
    for line in debug_lines:
        line_img = debug_font.render(line, False, (255, 255, 255))
        virtual_screen.blit(line_img, (0, line_num * 16))
        line_num += 1

    # Scale and draw the screen.
    pygame.transform.scale(virtual_screen, dimensions, scaled_screen)
    screen.blit(scaled_screen, (0, 0))
    pygame.display.flip()

    # Wait for the next frame.
    clock.tick(FRAMES_PER_SECOND)
