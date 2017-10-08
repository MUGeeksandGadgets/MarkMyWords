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
#START_STORY = 'cave'
START_STORY = 'bronze_agree'

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
    'team':    None,
    'exclaim': pygame.image.load(os.path.join('data', 'exclaim.png')),
    'question': pygame.image.load(os.path.join('data', 'question.png')),
    'period': pygame.image.load(os.path.join('data', 'period.png')),
    'comma': pygame.image.load(os.path.join('data', 'comma.png'))
}

# Emblems (helpful indications of what is being named)
emblems = {
    'earth': pygame.image.load(os.path.join('data', 'earth0.png')),
    'person': pygame.image.load(os.path.join('data', 'Drawable Images', 'person.png')),
    'club': pygame.image.load(os.path.join('data', 'Drawable Images', 'weapon.png')),
    'surrender': pygame.image.load(os.path.join('data', 'bigFlag.png'))
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
    def __init__(self):
        Sprite.__init__(self)

    def setup(self, x, y, images):
        frames = []
        for img in images:
            frames.append(pygame.image.load(os.path.join('data', img)).convert_alpha())
        self.image = frames[0]
        self.rect = self.image.get_rect().move((x, y))
        self.timer = 0
        self.frames = frames
        self.frame = 0

    def clone(self, x, y):
        spr = AnimatedSprite()
        spr.frames = self.frames
        spr.timer = 0
        spr.image = spr.frames[0]
        spr.rect = spr.image.get_rect().move((x, y))
        spr.frame = 0
        return spr

    def update(self):
        if hasattr(self, 'extra_update'):
            self.extra_update()

        self.timer += 1

        if self.timer == 20:
            self.timer = 0
            self.frame = (self.frame + 1) % len(self.frames)

        self.image = self.frames[self.frame]

class AnimatedSheet(Sprite):
    '''Animated sprite using a spritesheet.'''
    def __init__(self):
        Sprite.__init__(self)

    def setup(self, x, y, sheet_name, ncols, nrows, clip_region):
        sheet = pygame.image.load(os.path.join('data', sheet_name)).convert_alpha()

        # The region inside a frame to use as the sprite
        clip_region = pygame.Rect(clip_region)

        # The size of a single frame
        frame_width = sheet.get_width() / ncols
        frame_height = sheet.get_height() / nrows
        
        frames = []
        for col in range(ncols):
            for row in range(nrows):
                frame_region = pygame.Rect(col * frame_width,
                                           row * frame_height,
                                           frame_width,
                                           frame_height)
                frame_region = frame_region.clip(clip_region.move(col*frame_width,
                                                                  row*frame_height))
                
                surf = pygame.Surface((frame_region.width, frame_region.height), pygame.SRCALPHA)
                surf.blit(sheet, (0, 0), frame_region)

                frames.append(surf)

        self.image = frames[0]
        self.rect = self.image.get_rect().move((x, y))
        self.frames = frames
        self.flipped_frames = [pygame.transform.flip(f, True, False) for f in self.frames]
        self.timer = 0
        self.frame = 0

    def clone(self, x, y, flip=False):
        spr = AnimatedSheet()
        spr.image = self.frames[0]
        spr.rect = self.image.get_rect().move((x, y))
        if flip:
            spr.frames = self.flipped_frames
        else:
            spr.frames = self.frames
        spr.timer = 0
        spr.frame = 0
        return spr

    def update(self):
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

def render_text(surf, message, x, y):
    for i in range(len(message)):
        if message[i] in glyphs and glyphs[message[i]] is not None:
            surf.blit(glyphs[message[i]], (x + GLYPH_WIDTH*i, y))

class TextSprite(Sprite):
    def __init__(self, message, x, y):
        Sprite.__init__(self)
        self.image = Surface((GLYPH_WIDTH * len(message), GLYPH_HEIGHT))

        # Make the message box white.
        self.image.fill((255, 255, 255))

        # Draw the outline of the message box.
        pygame.draw.rect(self.image, (0, 0, 0), (0, 0, GLYPH_WIDTH * len(message), GLYPH_HEIGHT), 1)

        # Draw each letter.
        render_text(self.image, message, 0, 0)

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

class StoryMusic(object):
    def __init__(self, song):
        self.song = song

    def activate(self):
        pygame.mixer.music.load(os.path.join('music', self.song))
        pygame.mixer.music.play(-1)

class ChoiceMatrix(Sprite):
    def __init__(self, game, choices):
        Sprite.__init__(self)

        self.game = game
        self.choices = choices

        # Draw the choice matrix
        self._redraw_image()

    def _redraw_image(self):
        mat_width = max([GLYPH_WIDTH * len(ch[0]) for ch in self.choices])
        self.image = pygame.Surface((mat_width, GLYPH_HEIGHT * len(self.choices)))
        self.image.fill((0, 0, 255))
        for i, ch in enumerate(self.choices):
            self.image.fill((200, 200, 255), pygame.Rect(0, i*GLYPH_HEIGHT, mat_width - 1, GLYPH_HEIGHT - 1))
            render_text(self.image, ch[0], 0, i*GLYPH_HEIGHT)
        self.rect = self.image.get_rect().move((20, 120))

    def update(self):
        # Update sprite if hovered over a choice
        if self.rect.collidepoint(mouse_x, mouse_y):
            if mouse_down:
                choice_index = int(math.floor((mouse_y - self.rect.y) / GLYPH_HEIGHT))
                self.game._jump(self.choices[choice_index][1], 0)

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
        self._jump(START_STORY, 0)

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
            self.object_space.add(ChoiceMatrix(self, st.choices), layer=3)
        elif type(st) is StoryMusic:
            st.activate()
            self._jump(self.story, self.index + 1)
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

earth = AnimatedSprite()
earth.setup(65, 5, ['earth0.png', 'earth1.png', 'earth2.png', 'earth3.png', 'earth4.png', 'earth5.png'])
campfire = AnimatedSprite()
campfire.setup(60, 41, ['fire1.png', 'fire2.png'])

# arguments so you dont forget: setup(self, x, y, sheet_name, ncols, nrows, clip_region)
cavepig = AnimatedSheet()
cavepig.setup(0, 0, 'Main Cavemen.png', 1, 2, (97, 16, 31, 41))
cavepig2 = AnimatedSheet()
cavepig2.setup(0, 0, 'Main Cavemen 2.png', 1, 2, (97, 16, 31, 41))

cavepig_group = [cavepig2.clone(100, 27), cavepig.clone(160, 27, False)]

lizard = AnimatedSheet()
lizard.setup(0, 0, 'Lizard Caveman.png', 1, 2, (97, 16, 31, 41))
lizard_group = [lizard.clone(16, 27, True)]

lizard_still = AnimatedSheet()
lizard_still.setup(0, 0, 'Lizard Caveman.png', 1, 1, (97, 16, 31, 41))
lizard_still_group = [lizard_still.clone(16, 27, True)]

club = AnimatedSheet()
club.setup(0, 0, 'Wooden Club_00_00.png', 1, 1, (0, 0, 32, 32))

surrender_flag = AnimatedSheet()
surrender_flag.setup(0, 0, 'surrenderFlag.png', 1, 1, (0, 0, 16, 16))
bronze_pig_group = []
cavepig2 = AnimatedSheet()
cavepig2.setup(0, 0, 'Main Cavemen 2.png', 1, 2, (97, 16, 31, 41))

big_flag = AnimatedSheet()
big_flag.setup(0, 0, 'bigFlag.png', 1, 1, (0, 0, 32, 32))

bronze_pig_1 = AnimatedSheet()
bronze_pig_1.setup(0, 0, 'Main Bronze.png', 1, 2, (97, 16, 31, 41))
bronze_pig_2 = AnimatedSheet()
bronze_pig_2.setup(0, 0, 'Main Bronze 2.png', 1, 2, (97, 16, 31, 41))
spear = AnimatedSheet()
spear.setup(0, 0, 'Wooden Spear_00_00.png', 1, 1, (0, 0, 32, 32))

bronze_pig_group = [bronze_pig_1.clone(25, 27, True), bronze_pig_2.clone(45, 27)]
bronze_pig_alert_group = [bronze_pig_1.clone(25, 27, True), bronze_pig_2.clone(45, 27, True)]
bronze_pig_warrior = [bronze_pig_1.clone(25, 40, True), spear.clone(35, 50)]

bird = AnimatedSheet()
bird.setup(0, 0, 'Bird Warrior 1 animation.png', 1, 2, (97, 16, 31, 41))
bird_far = [bird.clone(170, 27)]
bird_far_other_direction = [bird.clone(170, 27, True)]
bird_close = [bird.clone(100, 27)]

lone_pig_on_road_1 = [bronze_pig_1.clone(10, 27, True)]
lone_pig_on_road_2 = [bronze_pig_1.clone(50, 27, True)]
lone_pig_on_road_3 = [bronze_pig_1.clone(100, 27, True)]
lone_pig_on_road_4 = [bronze_pig_1.clone(150, 27, True)]

cat = AnimatedSheet()
cat.setup(0, 0, 'Cat Warrior 1 animation.png', 1, 2, (72, 16, 45, 41))
cat_guard_group = [cat.clone(65, 40, False),
                   cat.clone(85, 40, False)]

stories = {
    'cave': [
        StoryMusic('Intro.ogg'),
        
        # Showing the planet
        StoryAnimation(
            40,
            Stage('Space.png', [earth])
        ),
        StoryDesignGlyph(
            'earth',
            Stage('Space.png', [earth])
        ),
        
        # Showing the country
        StoryAnimation(
            40,
            Stage('First Zoom.png', [])
        ),
        StoryDesignGlyph(
            'country',
            Stage('First Zoom.png', [])
        ),

        # Showing the village with pigs in it
        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire] + cavepig_group)
        ),
        StoryDesignGlyph(
            'person',
            Stage('First Scene.png', [campfire] + cavepig_group)
        ),
        StoryMessage(
            ['person', 'person', 'exclaim'],
            64, 19,
            Stage('First Scene.png', [campfire] + cavepig_group)
        ),

        # The lizard arrives!
        StoryMusic('primitive.ogg'),

        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire]  + cavepig_group + lizard_group)
        ),

        # Asking, "is it a person"?
        StoryMessage(
            ['person', 'question'],
            94, 19,
            Stage('First Scene.png', [campfire] + cavepig_group + lizard_group)
        ),

        # Lizard gets out the club
        StoryMusic('primitive.ogg'),
        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire]  + cavepig_group + lizard_still_group + [club.clone(44, 29)])
        ),
        StoryDesignGlyph(
            'club',
            Stage('First Scene.png', [campfire] + cavepig_group + lizard_still_group + [club.clone(44, 29)])
        ),

        # "Person club!"
        StoryMessage(
            ['person', 'club', 'exclaim'],
            92, 19,
            Stage('First Scene.png', [campfire]  + cavepig_group + lizard_still_group + [club.clone(44, 29)])
        ),
        StoryMessage(
            ['person', 'club', 'person', 'question', 'exclaim'],
            92, 19,
            Stage('First Scene.png', [campfire]  + cavepig_group + lizard_still_group + [club.clone(44, 29)])
        ),

        # Pig 1 gets out a club
        # Pig 2 gets out a surrender flag
        StoryMessage(
            ['country', 'exclaim', 'country', 'exclaim'],
            32, 19,
            Stage('First Scene.png', [campfire] + cavepig_group + lizard_still_group + [club.clone(44, 29), club.clone(90, 31, True)])
        ),
        StoryDesignGlyph(
            'surrender',
            Stage('First Scene.png', [campfire] + cavepig_group + lizard_still_group + [club.clone(44, 29), club.clone(90, 31, True), surrender_flag.clone(165, 34)])
        ),
        StoryChoice(
            [(['person', 'club', 'person', 'period'], 'cave_fight'),
             (['surrender', 'period'], 'cave_surrender')],
            Stage('First Scene.png', [campfire] + cavepig_group + lizard_still_group + [club.clone(44, 29), club.clone(90, 31, True), surrender_flag.clone(165, 34)])
        ),
    ],
    'cave_fight': [
        StoryMessage(
            ['person', 'club', 'person', 'exclaim'],
            100, 19,
            Stage('First Scene.png', [campfire] + lizard_still_group + cavepig_group + [club.clone(44, 29), club.clone(90, 31, True), surrender_flag.clone(165, 34)])
        ),
        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire, lizard_still.clone(29, 27, True), club.clone(34, 27), cavepig2.clone(70, 29), club.clone(60, 29, True), cavepig.clone(160, 27)])
        ),
        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire, lizard_still.clone(31, 27, True), club.clone(36, 27), cavepig2.clone(68, 29), club.clone(58, 29, True), cavepig.clone(160, 27)])
        ),
        StoryAnimation(
            80,
            Stage('First Scene.png', [campfire, lizard_still.clone(29, 27, True), club.clone(34, 27), cavepig2.clone(70, 29), club.clone(60, 29, True), cavepig.clone(160, 27)])
        ),
        StoryAnimation(
            40,
            Stage('First Scene.png', [campfire, lizard_still.clone(29, 27, True), campfire.clone(29, 27), cavepig2.clone(70, 29), club.clone(60, 29, True), cavepig.clone(160, 27)])
        ),
        StoryMessage(
            ['club', 'club', 'club', 'exclaim'],
            20, 19,
            Stage('First Scene.png', [campfire, lizard_still.clone(29, 27, True), campfire.clone(29, 27), cavepig2.clone(70, 29, True), club.clone(40, 29, True), cavepig.clone(160, 27)])
        ),


        # Bronze Age

        # 3000 BC

        # Pigs are alone
        StoryAnimation(
            40,
            Stage('Tents.png', bronze_pig_group)
        ),

        # Birds appear
        StoryAnimation(
            40,
            Stage('Tents.png', bronze_pig_group + bird_far)
        ),

        # learn "team/friendship" symbol
        StoryDesignGlyph(
            'team',
            Stage('Tents.png', bronze_pig_alert_group + bird_close)
        ),

        # "person team person ?"
        StoryMessage(
            ['person', 'team', 'person', 'question'],
            50, 19,
            Stage('Tents.png', bronze_pig_alert_group + bird_close)
        ),

        # choice - team up with birds or not?
        StoryChoice(
            [(['person', 'team', 'person'], 'bronze_agree'),
             (['surrender', 'period'], 'bronze_refuse')],
            Stage('Tents.png', bronze_pig_alert_group + bird_close)
        ),
    ],

    'bronze_agree': [
        # bird and pig on path (roadToFair)
        StoryMessage(
            ['person', 'team', 'person', 'period'],
            50, 19,
            Stage('Tents.png', bronze_pig_group + bird_close)
        ),
        StoryMessage(
            ['team', 'period'],
            60, 19,
            Stage('Tents.png', bronze_pig_group + bird_close)
        ),

        StoryAnimation(
            40,
            Stage('roadToFair.png', [bronze_pig_1.clone(40, 27, True), bird.clone(80, 27, True)])
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', [bronze_pig_1.clone(60, 27, True), bird.clone(100, 27, True)])
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', [bronze_pig_1.clone(80, 27, True), bird.clone(120, 27, True)])
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', [bronze_pig_1.clone(100, 27, True), bird.clone(140, 27, True)])
        ),

        # castle of the cats - bird and pig fight the cats
        StoryAnimation(
            40,
            Stage('Castle.png', bronze_pig_warrior + cat_guard_group + [bird.clone(45, 40)])
        ),
        StoryAnimation(
            40,
            Stage('Castle.png', bronze_pig_warrior + cat_guard_group + [bird.clone(45, 40)])
        ),
        # win, pig and cat look at each other and say "team team team !"
    ],

    'bronze_refuse': [
        StoryMessage(
            ['period', 'period', 'period', 'club', 'question'],
            50, 19,
            Stage('Tents.png', bronze_pig_alert_group + bird_close)
        ),
        StoryAnimation(
            40,
            Stage('Tents.png', bronze_pig_alert_group + bird_close)
        ),
        StoryAnimation(
            40,
            Stage('Tents.png', bronze_pig_alert_group + bird_far_other_direction)
        ),
        StoryAnimation(
            80,
            Stage('Tents.png', bronze_pig_alert_group)
        ),
        # lone pig on the road
        StoryAnimation(
            40,
            Stage('roadToFair.png', lone_pig_on_road_1)
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', lone_pig_on_road_2)
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', lone_pig_on_road_3)
        ),
        StoryAnimation(
            40,
            Stage('roadToFair.png', lone_pig_on_road_4)
        ),
        # castle of the cats - pig defeats cats
        StoryAnimation(
            40,
            Stage('Castle.png', cat_guard_group)
        ),
        StoryAnimation(
            160,
            Stage('Castle.png', bronze_pig_warrior + cat_guard_group)
        ),
        StoryMessage(
            ['club', 'club', 'club', 'exclaim'],
            10, 10,
            Stage('Castle.png', bronze_pig_warrior + cat_guard_group + [campfire.clone(65, 40), campfire.clone(85, 40), campfire.clone(30, 18), campfire.clone(100, 30)])
        ),
        # lone pig on the road
        StoryAnimation(
            120,
            Stage('roadToFair.png', [bronze_pig_1.clone(50, 27)])
        ),
        # castle of the birds - pig defeats birds
        StoryAnimation(80, Stage('Castle.png', [bronze_pig_1.clone(100, 40), bird.clone(50, 40, True)])),
        StoryAnimation(80, Stage('Castle.png', [bronze_pig_1.clone(100, 40), bird.clone(50, 40, True), campfire.clone(50, 40)])),
        # win, pig says "weapon weapon weapon !"
        StoryMessage(
            ['club', 'club', 'club', 'exclaim'],
            60, 10,
            Stage('Castle.png', [bronze_pig_1.clone(100, 40), big_flag.clone(90, 30)]))
    ],

    'cave_surrender': [
        StoryMessage(['person', 'surrender', 'exclaim'],
                     165, 19,
                     Stage('First Scene.png', [campfire] + lizard_still_group + [cavepig2.clone(100, 27, True), cavepig.clone(160, 27), club.clone(44, 29), club.clone(90, 31, True), surrender_flag.clone(165, 34)]))
    ]
}


game = Game()

pygame.mixer.music.load(os.path.join('music', 'Intro.ogg'))
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

