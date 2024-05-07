import random

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '550')
from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")


def is_desktop():
    return platform in ('linux', 'win', 'macosxx')


class MainWidget(RelativeLayout):
    from Transformes import transforme, transforme_2d, transforme_perpective
    from action_utilisateur import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up

    menu_widget = ObjectProperty()
    perspectiv_px = NumericProperty(0)
    perspectiv_py = NumericProperty(0)

    V_NB_LINES = 10
    V_LINES_SPACING = .25  # pourcentage de la largeur de l'ecran
    vertical_lines = []

    H_NB_LINES = 8
    H_LINES_SPACING = .15  # pourcentage de la longueur de l'ecran
    horizontal_lines = []

    SPEED_Y = 0.8
    point_courant_y = 0
    courant_y_boucle = 0
    SPEED_X = 3.0
    current_speed_x = 0
    point_courant_x = 0

    NB_TUILES = 8
    NB_PRE_TUILE = 8
    tuile = []
    tuile_coord = []

    timee_acc = 1

    ship = None
    SHIP_WIDHT = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship_coord = [(0, 0), (0, 0), (0, 0)]

    etat_game_over = False
    etat_game_start = False

    menu_titre = StringProperty("G    A    L    A    X    Y")
    menu_bouton_titre = StringProperty("START")
    score_txt = StringProperty()

    son_debut = None
    son_galaxy = None
    son_game_over_instant = None
    son_game_over = None
    son_music1 = None
    son_reset = None

    acc = 0
    press_keyboard = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tuiles()
        self.init_ship()
        self.pre_tuile_coord()
        self.generate_tuiles_coord()

        if is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.son_galaxy.play()

    def init_audio(self):
        self.son_debut = SoundLoader.load("audio/begin.wav")
        self.son_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.son_game_over_instant = SoundLoader.load("audio/gameover_impact.wav")
        self.son_game_over = SoundLoader.load("audio/gameover_voice.wav")
        self.son_music1 = SoundLoader.load("audio/music1.wav")
        self.son_reset = SoundLoader.load("audio/restart.wav")

        self.son_music1.volume = 1
        self.son_debut.volume = .25
        self.son_galaxy.volume = .25
        self.son_game_over_instant.volume = .25
        self.son_game_over.volume = .25
        self.son_reset.volume = .25

    def reset_game(self):
        self.point_courant_y = 0
        self.courant_y_boucle = 0
        self.current_speed_x = 0
        self.point_courant_x = 0
        self.acc = 0
        self.tuile_coord = []
        self.score_txt = "SCORE: " + str(self.courant_y_boucle)
        self.pre_tuile_coord()
        self.generate_tuiles_coord()
        self.etat_game_over = False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.perspectiv_px
        base_y = self.SHIP_BASE_Y*self.height
        half_width = self.SHIP_WIDHT*center_x
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coord[0] = (center_x-half_width, base_y)
        self.ship_coord[1] = (center_x, base_y + ship_height)
        self.ship_coord[2] = (center_x+half_width, base_y)

        x1, y1 = self.transforme(*self.ship_coord[0])
        x2, y2 = self.transforme(*self.ship_coord[1])
        x3, y3 = self.transforme(*self.ship_coord[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def collision_ship(self):
        for i in range(0, len(self.tuile_coord)):
            tuile_x, tuile_y = self.tuile_coord[i]
            if tuile_y > self.courant_y_boucle + 1:
                return False
            if self.collision_ship_tuile(tuile_x, tuile_y):
                return True
        return False

    def collision_ship_tuile(self, tuile_x, tuile_y):
        xmin, ymin = self.get_tuile_coord(tuile_x, tuile_y)
        xmax, ymax = self.get_tuile_coord(tuile_x+1, tuile_y+1)

        for i in range(0, 3):
            px, py = self.ship_coord[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1,1,1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def init_tuiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TUILES):
                self.tuile.append(Quad())

    def pre_tuile_coord(self):
        for i in range(0, self.NB_PRE_TUILE):
            self.tuile_coord.append((0, i))

    def generate_tuiles_coord(self):
        last_y = 0
        last_x = 0

        for i in range(len(self.tuile_coord)-1, -1, -1):
            if self.tuile_coord[i][1] < self.courant_y_boucle:
                del self.tuile_coord[i]

        if len(self.tuile_coord) > 0:
            last_coord = self.tuile_coord[-1]
            last_x = last_coord[0]
            last_y = last_coord[1]+1

        for i in range(len(self.tuile_coord), self.NB_TUILES):
            r = random.randint(0, 2)
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1

            if last_x >= end_index-1:
                r = 2

            if last_x <= start_index:
                r = 1

            self.tuile_coord.append((last_x, last_y))

            if r == 1:
                last_x += 1
                self.tuile_coord.append((last_x, last_y))
                last_y += 1
                self.tuile_coord.append((last_x, last_y))
            elif r == 2:
                last_x -= 1
                self.tuile_coord.append((last_x, last_y))
                last_y += 1
                self.tuile_coord.append((last_x, last_y))
            last_y += 1

    def get_line_x_from_index(self, index):
        central_line_x = self.perspectiv_px
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.point_courant_x

        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.point_courant_y
        return line_y

    def get_tuile_coord(self, tuile_x, tuile_y):
        tuile_y = tuile_y - self.courant_y_boucle
        x = self.get_line_x_from_index(tuile_x)
        y = self.get_line_y_from_index(tuile_y)
        return x, y

    def update_tuiles(self):
        for i in range(0, self.NB_TUILES):
            tuile = self.tuile[i]
            tuile_coord = self.tuile_coord[i]
            xmin, ymin = self.get_tuile_coord(tuile_coord[0], tuile_coord[1])
            xmax, ymax = self.get_tuile_coord(tuile_coord[0] + 1, tuile_coord[1] + 1)

            x1, y1 = self.transforme(xmin, ymin)
            x2, y2 = self.transforme(xmin, ymax)
            x3, y3 = self.transforme(xmax, ymax)
            x4, y4 = self.transforme(xmax, ymin)
            tuile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transforme(line_x, 0)
            x2, y2 = self.transforme(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        end_index = start_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(start_index)  # + self.point_courant_x
        xmax = self.get_line_x_from_index(end_index)  # + self.point_courant_x
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transforme(xmin, line_y)
            x2, y2 = self.transforme(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        facteur_temps = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tuiles()
        self.update_ship()

        if not self.etat_game_over and self.etat_game_start:
            speed_y = self.SPEED_Y * self.height / 100
            self.point_courant_y += speed_y * facteur_temps
            speed_x = self.current_speed_x * self.width / 100
            self.point_courant_x += speed_x * facteur_temps

            spacing_y = self.H_LINES_SPACING * self.height
            while self.point_courant_y >= spacing_y:
                self.point_courant_y -= spacing_y
                self.courant_y_boucle += 1
                self.score_txt = "SCORE: " + str(self.courant_y_boucle)
                self.generate_tuiles_coord()

        if not self.collision_ship() and not self.etat_game_over:
            self.etat_game_over = True
            self.menu_titre = "G  A  M  E    O  V  E  R"
            self.menu_bouton_titre = "RESTART"
            self.menu_widget.opacity = 1
            self.son_music1.stop()
            self.son_game_over_instant.play()
            Clock.schedule_once(self.play_voice_game_over, 1)

    def play_voice_game_over(self, dt):
        if self.etat_game_over:
            self.son_game_over.play()

    def on_menu_press(self):
        if self.etat_game_over:
            self.son_reset.play()
        else:
            self.son_debut.play()
        self.son_music1.play()
        self.reset_game()
        self.etat_game_start = True
        self.menu_widget.opacity = 0


class GalaxyApp(App):
    pass


GalaxyApp().run()

