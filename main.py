import sys
import pygame
from pygame import Surface
from pygame.sprite import Sprite
from pygame.sprite import LayeredUpdates


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


# Object types
class Frame(Sprite):
    """
    A Frame is a stylish border around the screen.
    """
    def __init__(self):
        """Create a new frame."""
        Sprite.__init__(self)
        self.image = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.image.set_colorkey((255, 0, 255))
        self.image.fill((200, 200, 200))
        pygame.draw.rect(self.image,
                         (255, 0, 255),
                         (8, 8,
                          SCREEN_WIDTH - 16,
                          SCREEN_HEIGHT - 24 - CANVAS_HEIGHT))
        self.rect = (0, 0)

class Canvas(Sprite):
    """
    A Canvas is what the player draws new glyphs onto.
    """
    def __init__(self):
        """Create a new art canvas."""
        Sprite.__init__(self)
        self.pen_x = 0      # X coordinate of the selected pixel
        self.pen_y = 0      # Y coordinate of the selected pixel
        self.image = Surface((GLYPH_WIDTH * CANVAS_ZOOM,
                              GLYPH_HEIGHT * CANVAS_ZOOM))
        self.rect = (CANVAS_X, CANVAS_Y)

        # Storage for the canvas' pixels
        self.pixels = []
        for y in range(0, CANVAS_HEIGHT):
            self.pixels.append([])
            for x in range(0, CANVAS_WIDTH):
                self.pixels[y].append(0)

        # Initialize the image
        self._redraw_image()

    def is_selecting(self):
        """Return whether the user is choosing a pixel of the canvas."""
        return mouse_x >= self.rect[0] \
               and mouse_x < self.rect[0] + CANVAS_WIDTH \
               and mouse_y >= self.rect[1] \
               and mouse_y < self.rect[1] + CANVAS_HEIGHT

    def _redraw_image(self):
        """Redraw the image of the canvas."""
        self.image.fill((255, 255, 255),
                        (0, 0,
                         CANVAS_WIDTH * CANVAS_ZOOM,
                         CANVAS_HEIGHT * CANVAS_ZOOM))

        for y in range(len(self.pixels)):
            for x in range(len(self.pixels[0])):
                pixel = self.pixels[y][x]

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
                    self.image.fill(color,
                                    (x * CANVAS_ZOOM,
                                     y * CANVAS_ZOOM,
                                     CANVAS_ZOOM, CANVAS_ZOOM))

    def update(self):
        """Update the state of the canvas."""
        # If the user is painting, place a pixel.
        if self.is_selecting():
            self.pen_x = (mouse_x - self.rect[0]) / CANVAS_ZOOM
            self.pen_y = (mouse_y - self.rect[1]) / CANVAS_ZOOM

            if mouse_held:
                self.pixels[self.pen_y][self.pen_x] = 1
                self._redraw_image()


class DebugReadout(Sprite):
    """
    A DebugReadout shows useful debugging information on-screen.

    It currently shows the cursor position and the coordinates of the
    selected pixel on the art canvas.
    """
    def __init__(self, canvas):
        """Create a new debug readout."""
        Sprite.__init__(self)
        self.image = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.image.set_colorkey((255, 0, 255))
        self.rect = (0, 0)
        self.canvas = canvas

    def update(self):
        """Update the readout using current information."""
        self.image.fill((255, 0, 255))

        debug_lines = [
            'cursor: (%d, %d)' % (mouse_x, mouse_y)
        ]

        if self.canvas.is_selecting():
            debug_lines += ['selection: (%d, %d)'
                            % (canvas.pen_x, canvas.pen_y)]

        line_num = 0
        for line in debug_lines:
            line_img = debug_font.render(line, False, (255, 255, 255))
            self.image.blit(line_img, (0, line_num * 16))
            line_num += 1


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

# In-game objects
canvas        = Canvas()
debug_readout = DebugReadout(canvas)
frame         = Frame()

# Collection of all objects (ensures correct drawing order)
world = LayeredUpdates()
world.add(canvas, layer=2)
world.add(debug_readout, layer=1)
world.add(frame, layer=0)

while True:
    # Handle user input (mouse and quitting).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            mouse_x = event.pos[0] / SCREEN_ZOOM
            mouse_y = event.pos[1] / SCREEN_ZOOM
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False

    # If the user is painting, place a pixel.
    world.update()

    # Draw everything onto the virtual screen.
    virtual_screen.fill((0, 0, 0))
    world.draw(virtual_screen)

    # Scale and draw onto the real screen.
    pygame.transform.scale(virtual_screen, dimensions, scaled_screen)
    screen.blit(scaled_screen, (0, 0))
    pygame.display.flip()

    # Wait for the next frame.
    clock.tick(FRAMES_PER_SECOND)
