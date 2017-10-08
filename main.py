import sys, os
import pygame
import math
from pygame import Surface
from pygame.sprite import Sprite
from pygame.sprite import LayeredUpdates


# Constants
SCREEN_WIDTH = 256      # How wide the screen is in "virtual pixels"
SCREEN_HEIGHT = 240     # How tall the screen is in "virtual pixels"
SCREEN_ZOOM = 2         # Scale factor of the whole screen
FRAMES_PER_SECOND = 40  # How many frames to draw per second
CANVAS_ZOOM = 4         # Scale factor of the art canvas
DEBUG = False           # Whether debug information should show up

# Dimensions of the glyphs (in virtual pixels)
GLYPH_WIDTH = 20        # How wide a glyph 
GLYPH_HEIGHT = 20       # How tall a glyph is

# Dimensions of the art canvas (in virtual pixels)
CANVAS_WIDTH = GLYPH_WIDTH * CANVAS_ZOOM
CANVAS_HEIGHT = GLYPH_HEIGHT * CANVAS_ZOOM
CANVAS_X = SCREEN_WIDTH - 8 - CANVAS_WIDTH
CANVAS_Y = SCREEN_HEIGHT - 8 - CANVAS_HEIGHT


# Glyphs in the language
glyphs = {
    'fire':    None, 
    'water':   None,
    'house':   None,
    'person':  None,
    'earth':   None,
    'exclaim': pygame.image.load(os.path.join('data', 'exclaim.png')),
    'period': pygame.image.load(os.path.join('data', 'period.png')),
    'comma': pygame.image.load(os.path.join('data', 'comma.png'))
}

# Emblems (helpful indications of what is being named)
emblems = {
    'earth': pygame.image.load(os.path.join('data', 'earth0.png'))
}

# Object types
class Frame(Sprite):
    """
    A Frame is a stylish border around the screen.
    """
    def __init__(self):
        """Create a new frame."""
        Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'BronzeAgeFrame.png')).convert_alpha()
        self.rect = self.image.get_rect()


def color_code_to_color(code):
    if code == 0:
        # Transparent pixel
        color = (255, 0, 255)
    elif code == 1:
        # Black pixel
        color = (0, 0, 0)
    elif code == 2:
        # Red pixel
        color = (255, 0, 0)
    elif code == 3:
        # Green pixel
        color = (0, 255, 0)
    elif code == 4:
        # Brown pixel
        color = (125, 100, 0)
    return color

class OkayButton(Sprite):
    """
    An OkayButton accepts the current image.
    """
    def __init__(self, x, y, game):
        Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join('data', 'okay.png'))
        self.rect = (x, y)
        self.game = game

    def update(self):
        game = self.game
        if mouse_down:
            # activate the button if mouse is on button
            if mouse_x >= self.rect[0] \
               and mouse_x < self.rect[0] + self.image.get_width() \
               and mouse_y >= self.rect[1] \
               and mouse_y < self.rect[1] + self.image.get_height():
                glyphs[stories[game.story][game.index].glyph_name] = \
                  game.canvas.to_surface()
                game._jump(game.story, game.index + 1)

class EqualsSign(Sprite):
    def __init__(self, x, y):
        Sprite.__init__(self)
        self.rect = (x, y)
        self.image = Surface((40, 40))
        self.image.set_colorkey((255, 0, 255))
        self.image.fill((255, 0, 255))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, 40, 10))
        pygame.draw.rect(self.image, (0, 0, 0), (0, 30, 40, 10))

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

        # Helper variables for handling mouse lag
        self._was_drawing = False
        self._prev_sel = (0, 0)

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
                color = color_code_to_color(pixel)
                if color == (255, 0, 255):
                    color = (255, 255, 255)
                self.image.fill(color,
                                (x * CANVAS_ZOOM,
                                 y * CANVAS_ZOOM,
                                 CANVAS_ZOOM, CANVAS_ZOOM))

        # Draw the grid
        for y in range(len(self.pixels)):
            pygame.draw.line(self.image, (100, 100, 200), (0, y * CANVAS_ZOOM), (GLYPH_WIDTH * CANVAS_ZOOM, y * CANVAS_ZOOM))
        for x in range(len(self.pixels)):
            pygame.draw.line(self.image, (100, 100, 200), (x * CANVAS_ZOOM, 0), (x * CANVAS_ZOOM, GLYPH_HEIGHT * CANVAS_ZOOM))

    def to_surface(self):
        surf = pygame.Surface((GLYPH_WIDTH, GLYPH_HEIGHT))
        surf.set_colorkey((255, 0, 255))
        surf.fill((255, 0, 255))
        for y in range(0, GLYPH_HEIGHT):
            for x in range(0, GLYPH_WIDTH):
                pygame.draw.rect(surf, color_code_to_color(self.pixels[y][x]), (x, y, 1, 1))
        return surf

    def update(self):
        """Update the state of the canvas."""
        # If the user is painting, place a pixel.
        if self.is_selecting():
            self.pen_x = math.floor((mouse_x - self.rect[0]) / CANVAS_ZOOM)
            self.pen_y = math.floor((mouse_y - self.rect[1]) / CANVAS_ZOOM)

            if mouse_held:
                if self._was_drawing:
                    # Draw a line from the previous position
                    # to the current position
                    """
                    distance = math.sqrt(
                                 (self._prev_sel[0]
                                   - self.pen_x) ** 2
                                 + (self._prev_sel[1]
                                    - self.pen_y) ** 2)
                    angle = 
                    """
                else:
                    self._prev_sel = (self.pen_x, self.pen_y)
                    self._was_drawing = True

                self.pixels[self.pen_y][self.pen_x] = 1
                self._redraw_image()
            else:
                self._was_drawing = False
        else:
            self._was_drawing = False

    def clear(self):
        for y in range(0, CANVAS_HEIGHT):
            for x in range(0, CANVAS_WIDTH):
                self.pixels[y][x] = 0
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
                            % (self.canvas.pen_x, self.canvas.pen_y)]

        line_num = 0
        for line in debug_lines:
            line_img = debug_font.render(line, False, (255, 255, 255))
            self.image.blit(line_img, (0, line_num * 16))
            line_num += 1

class Dummy(Sprite):
    def __init__(self):
        Sprite.__init__(self)
        self.rect = (0, 0)
        self.image = pygame.image.load(os.path.join("data", "dummy.png"))


class AnimatedSprite(Sprite):
    def __init__(self, x, y, images):
        Sprite.__init__(self)
        frames = []
        for img in images:
            frames.append(pygame.image.load(os.path.join('data', img)).convert_alpha())
        self.image = Surface((frames[0].get_width(),
                              frames[0].get_height()))
        self.rect = self.image.get_rect().move((x, y))
        self.timer = 0
        self.frames = frames
        self.frame = 0

    def update(self):
        if hasattr(self, 'extra_update'):
            self.extra_update()

        self.timer += 1

        if self.timer == 20:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.frames)

        self.image = self.frames[self.frame]


class AnimatedDummy(AnimatedSprite):
    def __init__(self, frames):
        AnimatedSprite.__init__(self, images)
        self.rect = (40, 40)


class Stage(Sprite):
    """
    A Stage holds the sprites and backgrounds in the game world.
    """
    def __init__(self, bg_name, objects=[]):
        Sprite.__init__(self)
        self.image = Surface((224, 80))
        self.bg = pygame.image.load(os.path.join('data', bg_name)).convert()
        self.rect = (16, 16)

        # All objects on the stage
        self.object_space = LayeredUpdates()
        for i, o in enumerate(objects):
            self.object_space.add(o, layer=i)

    def update(self):
        self.object_space.update()
        pygame.transform.scale(self.bg, (224, 80), self.image)
        self.object_space.draw(self.image)

class TextSprite(Sprite):
    def __init__(self, message, x, y):
        Sprite.__init__(self)
        self.image = Surface((GLYPH_WIDTH * len(message), GLYPH_HEIGHT))

        # Make the message box white.
        self.image.fill((255, 255, 255))

        # Draw the outline of the message box.
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, GLYPH_WIDTH * len(message), GLYPH_HEIGHT), 1)

        # Draw each letter.
        for i in range(len(message)):
            self.image.blit(glyphs[message[i]], (GLYPH_WIDTH*i, 0))

        self.rect = self.image.get_rect().move((x, y))

class StoryAnimation(object):
    def __init__(self, delay, stage):
        self.delay = delay
        self.stage = stage

class StoryMessage(object):
    def __init__(self, message, x, y, stage):
        self.message = message
        self.x = x
        self.y = y
        self.stage = stage

class StoryChoice(object):
    def __init__(self, choices, stage):
        self.choices = choices
        self.stage = stage

class StoryDesignGlyph(object):
    def __init__(self, glyph_name, stage):
        self.glyph_name = glyph_name
        self.stage = stage

class ChoiceMatrix(Sprite):
    def __init__(self, game, choices):
        Sprite.__init__()

        self.game = game
        self.choices = choices

        # Draw the choice matrix

    def _redraw_image(self):
        for choice in self.choices:
            pass

    def update(self):
        # Update sprite if hovered over a choice

        # Activate choice if clicked
        pass

class Game(object):
    """
    A Game handles everything in the game.
    """
    def __init__(self):
        # In-game objects
        self.canvas        = Canvas()
        self.debug_readout = DebugReadout(self.canvas)
        self.frame         = Frame()
        self.okay_btn      = OkayButton(CANVAS_X, CANVAS_Y - 40, self)
        self.emblem        = Sprite()
        self.emblem.rect = (25, 150)
        self.equalssign    = EqualsSign(105, 180)

        # Collection of all objects (ensures correct drawing order)
        self.object_space = LayeredUpdates()

        # Starting mode
        self._jump('cave', 0)

    def _jump(self, story, index):
        self.story = story
        self.index = index
        
        self.object_space.empty()

        self.canvas.clear()
        st = stories[story][index]
        if type(st) is StoryAnimation:
            self.timer = st.delay
        elif type(st) is StoryDesignGlyph:
            if st.glyph_name in emblems:
                self.emblem.image = emblems[st.glyph_name]
            else:
                self.emblem.image = Surface((0, 0))
            self.object_space.add(self.emblem, layer=3)
            self.object_space.add(self.okay_btn, layer=3)
            self.object_space.add(self.canvas, layer=3)
            self.object_space.add(self.equalssign, layer=3)
        elif type(st) is StoryMessage:
            self.object_space.add(TextSprite(st.message, st.x, st.y), layer=3)
        elif type(st) is StoryChoice:
            self.object_space.add(ChoiceMatrix(self, st.choices))
        if DEBUG:
            self.object_space.add(self.debug_readout, layer=2)
        self.object_space.add(self.frame, layer=1)
        self.object_space.add(stories[self.story][self.index].stage, layer=0)

    def update(self):
        st = stories[self.story][self.index]
        if type(st) is StoryMessage:
            if pygame.K_SPACE in keys_just_pressed:
                self._jump(self.story, self.index + 1)
        elif type(st) is StoryAnimation:
            self.timer -= 1
            if self.timer <= 0:
                self._jump(self.story, self.index + 1)
        elif type(st) is StoryDesignGlyph:
            """
            if pygame.K_SPACE in keys_just_pressed:
                glyphs[st.glyph_name] = self.canvas.to_surface()
                self._jump(self.story, self.index + 1)
            """
            pass

        self.object_space.update()

    def draw(self, screen):
        self.object_space.draw(screen)

# Input handling
mouse_x = 0        # The x coordinate of the mouse (in virtual pixels)
mouse_y = 0        # The y coordinate of the mouse (in virtual pixels)
mouse_held = False # Whether the mouse button is being held down
mouse_down = False # Whether the mouse buttos was just now pressed
keys_just_pressed = []

# Initialize Pygame
pygame.init()
dimensions = (SCREEN_WIDTH * SCREEN_ZOOM,
              SCREEN_HEIGHT * SCREEN_ZOOM)
screen = pygame.display.set_mode(dimensions)
clock = pygame.time.Clock()
debug_font = pygame.font.Font(None, 20)
virtual_screen = Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
scaled_screen = Surface(dimensions, 0, virtual_screen)

# Story sequence

earth = AnimatedSprite(65, 5, ['earth0.png', 'earth1.png', 'earth2.png', 'earth3.png', 'earth4.png', 'earth5.png'])
campfire = AnimatedSprite(60, 41, ['fire1.png', 'fire2.png'])

stories = {
    'cave': [
        StoryAnimation(
            40,
            Stage('Space.png', [earth])
        ),
        StoryDesignGlyph(
            'earth',
            Stage('Space.png', [earth])
        ),
        StoryAnimation(
            40,
            Stage('First Zoom.png', [])
        ),
        StoryDesignGlyph(
            'country',
            Stage('First Zoom.png', [])
        ),
        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire])
        ),
        StoryMessage(
            ['country', 'exclaim', 'country', 'exclaim'],
            32, 19,
            Stage('First Scene.png', [campfire])
        ),
        StoryMessage(
            ['earth', 'period'],
            42, 29,
            Stage('First Scene.png', [campfire])
        ),
        #StoryChoice(
        #    [(['fight', 'evil', 'person'], 'cave_fight'),
        #     (['surrender', 'country'], 'cave_surrender')],
        #    Stage('First Scene.png', [campfire])
        #),
        StoryAnimation(
            40,
            Stage('primativeHomeIn.png', [])
        ),
        StoryAnimation(
            40,
            Stage('First Scene.png', [])
        ),
        StoryAnimation(
            40,
            Stage('Tents.png', [])
        ),
        StoryAnimation(
            40,
            Stage('Castle.png', [])
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', [])
        ),
        StoryAnimation(
            40,
            Stage('renaissanceFair.png', [])
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', [])
        ),
    ]
}


game = Game()

pygame.mixer.music.load(os.path.join('music', 'primitive.ogg'))
pygame.mixer.music.play(-1)

while True:

    keys_just_pressed = []
    mouse_down = False
    # Handle user input (mouse and quitting).
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            mouse_x = event.pos[0] / SCREEN_ZOOM
            mouse_y = event.pos[1] / SCREEN_ZOOM
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True
            mouse_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False
        elif event.type == pygame.KEYDOWN:
            keys_just_pressed.append(event.key)

    # If the user is painting, place a pixel.
    game.update()

    # Draw everything onto the virtual screen.
    virtual_screen.fill((0, 0, 0))
    game.draw(virtual_screen)

    # Scale and draw onto the real screen.
    pygame.transform.scale(virtual_screen, dimensions, scaled_screen)
    screen.blit(scaled_screen, (0, 0))
    pygame.display.flip()

    # Wait for the next frame.
    clock.tick(FRAMES_PER_SECOND)
