#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import random, time, copy, os, pickle
os.environ['KIVY_AUDIO'] = 'sdl2'

import kivy
kivy.require('1.0.7')

from kivy.config import Config

from kivy.core.window import Window
scale = kivy.metrics.sp(1)
def dp(v):  return (v * scale) / 2
Window.size = (800, 600)
Window.clearcolor = (0.3, 0.3, 0.1, 0.3)

from kivy.animation import Animation
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.core.window import Window, Keyboard
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.audio import SoundLoader
from kivy.uix.image import Image
from kivy.uix.stacklayout import StackLayout
from kivy.properties import NumericProperty

from modules import jpmap
jp_maps=(jpmap.jp_map_h, jpmap.jp_map_k, jpmap.jp_map_t)

title='Hiragana/Katakana Testing'
confs=(60, 0, 0, 1, 1, 30, 5, 6) # (time, character, mode, cheat, size, delay, flakes)

bt_img='sources/btn.png'
bg_img='sources/bg.jpg'
bg_sound='sources/bg.wav'
shot_sound='sources/sliencer.wav'
miss_sound='sources/reload.wav'
conf_path=os.getenv("HOME")+'/jptest.conf'
extmap_path=os.getenv("HOME")+'/jp_ext.map'

font_name='sources/DroidSansFallback'
help_font='sources/CourierNew'
flake_colors=((0.1,1,1,.7), (1,0.1,1,.7), (1,1,0.1,.7),
(0.5,1,0.5,.7), (0.5,0.5,1,.8), (1,0.5,0.5,.7))
bullet_color=(0,0,0,0)
size_hint=(None, None)

time_limit_mode=0
char_limit_mode=1
long_limit_mode=2

extmap_index=-1

help_info=\
"""
Help:
1. system commands: help, exit, setup, ...
   * help: it comes to this page
   * exit: close the window
   * setup: you would be able to see a textinput box:
         Time | Alphabet | Mode | Cheat | Speed | FontSize | Delay | Flakes:
           60,       0,      0,      1,      1,      30,       5,       6
       - Time: 1-n => the certain time, see Mode 0
       - Alphabet:  0 => hiragana   1 => katakana   2 => kanji
                   -1 => load the user-defined map from """+extmap_path+"""
       - Mode:  0 => count the character numbers in a certain time
                1 => count the time after you finish all characters
                2 => shot all before any flakes touch the buttom
       - Cheat: 0 => disable the prompt by clicking the flakes
                1 => enable the prompt by clicking the flakes
       - Speed: 1-n => flakes fall faster as the value gets bigger
       - FontSize: 1-n => the FontSize on each flake
       - Delay: 0 => no animation delay, shoot extremly fast
                1-n => the animation duration for shooting
       - Flakes:1-n => the numbers of the Flakes
    * ...: others would be matched with the flakes
2. clicks: on-flakes, on-bullet
     * on-flakes: show the prompt if Cheat is enable
     * on-bullet: it comes to this page, as help cmd does

Copyright:
  Powered By : Xin Long <lucein.xin@gmail.com>
  Source Code : https://github.com/lxin/jptest
"""
class JPTest(App, Widget):
    def get_conf_flakes(self):  return self.confs[7]
    def get_conf_delay(self):
         if self.get_conf_char() == 2: # important to author
             return random.randint(10, 20)
         return self.confs[6]

    def get_conf_fsize(self):   return self.confs[5]
    def get_conf_speed(self):   return self.confs[4]
    def get_conf_prompt(self):  return self.confs[3]
    def get_conf_mode(self):    return self.confs[2]
    def get_conf_char(self):    return self.confs[1]
    def get_conf_time(self):    return self.confs[0]

    def get_conf_all(self):
        return ',    '.join([str(i) for i in self.confs])

    def get_stat_stime(self):    return self.stats[0]
    def get_stat_pass(self):     return self.stats[1]
    def get_stat_fail(self):     return self.stats[2]
    def get_stat_ctime(self):    return self.stats[3]

    def set_stat_stime(self, val):    self.stats[0] = val
    def set_stat_pass(self, val):     self.stats[1] = val
    def set_stat_fail(self, val):     self.stats[2] = val
    def set_stat_ctime(self, val):    self.stats[3] = val

    def get_stat_all(self):
        return 'Time: {}, Pass: {}, Fail: {}'.format(self.get_stat_ctime(),
               self.get_stat_pass(), self.get_stat_fail())

    def keyboard_closed(self):
        pass

    def on_window_resize(self, window, width, height):
        self.reset_stats(True)

    def setup_press(self, instance):
        try:
            text = instance.setup_input.text
            newconfs = ()
            newconfs = tuple(int(i) for i in text.split(','))
        finally:
            if len(newconfs) != len(self.confs):
                instance.setup_input.text = self.get_conf_all()
                return

        self.confs=newconfs
        pickle.dump(self.confs, open(conf_path,'wb'))
        self.reset_stats(instance)

    def reset_widgets(self, instance = None):
        self.win_width  = Window.size[0]
        self.win_height = Window.size[1]

        self.popup_font_size=   self.win_width / 53
        self.flake_font_size=   self.win_width / 53  # not used
        self.label_font_size=   self.win_width / 80
        self.input_font_size=   self.win_width / 45
        self.help_font_size=    self.win_height/ 60
        self.box_padding=       self.win_width / 160
        self.box_input_padding= self.win_width / 80

        for widget in self.layout.walk(restrict=True):
            self.layout.remove_widget(widget)

        self.layout.add_widget(Image(source=bg_img, allow_stretch=True))
        self.buttons = []
        for i in range(self.get_conf_flakes()):
            bullet = self.create_bullet()
            button = self.create_flake(i, bullet)
            self.layout.add_widget(bullet)
            self.layout.add_widget(button)

        self.layout.add_widget(self.create_bullet(bt_img))
        self.layout.add_widget(self.create_cmdline())

    def reset_stats(self, instance = None):
        self.stats=[time.time(), 0, 0, self.get_conf_time()]
        try:
            if self.get_conf_char() == extmap_index:
                newmap = eval(open(extmap_path,'rb').read())
            else:
                newmap = jp_maps[self.get_conf_char()]
        except:
            newmap = jp_maps[0]
        self.jp_map=copy.deepcopy(newmap)

        self.no_keys=0
        if not instance:
            return True

        if self.popup:
            self.popup.dismiss()
            self.popup=None

        self.sounds[2].play()
        self.reset_widgets()


    def close_window(self, instance):
        self.stop()

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.popup:
            return True

        if (keycode[1] == 'enter'):
            if self.textinput.text == "exit":
                self.stop()
                return True
            if self.textinput.text == "help":
                self.help_press()
                return True
            if self.textinput.text == "setup":
                self.confs_press()
                return True

            for b in self.buttons:
                if self.textinput.text == b.kv_key:
                    if self.get_conf_delay():
                        b.bullet.background_color = b.background_color
                        b.bullet.text = self.textinput.text
                        self.animate_bullet(b.bullet)
                    else:
                        self.sounds[0].play()
                        b.opacity = 0

                    self.set_stat_pass(self.get_stat_pass() + 1)
                    self.textinput.text=""
                    return True

            self.set_stat_fail(self.get_stat_fail() + 1)
            self.sounds[1].play()
            self.textinput.text=""
            return True

        if not self.textinput.focus:
            self.textinput.focus=True
            self.textinput.text+=chr(keycode[0])
            return True

        return True

    def animate_flake_restart(self, animation, instance):
        if instance not in self.buttons:
            return True

        if instance.opacity == 0:
            instance.opacity = 1
            self.set_random_char(instance)

        instance.pos[1]=self.win_height  # width should be updated and size more !
        self.animate_flake(instance)

        if self.popup:
           return True

        time_gap = int(time.time() - self.get_stat_stime())
        if (self.get_conf_mode() == char_limit_mode and self.no_keys >= self.get_conf_flakes()) \
            or (self.get_conf_mode() == long_limit_mode and instance.opacity == 1) \
            or ( self.get_conf_mode() == time_limit_mode and time_gap >= self.get_stat_ctime()):
            self.set_stat_ctime(time_gap)
        else:
            if self.get_conf_char() == 2 and self.no_keys < self.get_conf_flakes():  # important to author
                for b in self.buttons:
                        if self.get_conf_delay():
                            b.bullet.background_color = b.background_color
                            b.bullet.text = "♥"
                            self.animate_bullet(b.bullet)

            return True

        box = BoxLayout(orientation = 'vertical', padding = (self.box_padding))
        box.add_widget(Label(text = self.get_stat_all(), size_hint=(1, 0.4)))
        box.add_widget(Button(text = "restart", size_hint=(1, 0.3), on_press=self.reset_stats))
        box.add_widget(Button(text = "exit", size_hint=(1, 0.3), on_press=self.close_window))
        self.popup = Popup(title='Result', title_size= self.popup_font_size, title_align = 'center', auto_dismiss = False,
                           content = box,  size_hint=size_hint, size=(self.win_width / 3, self.win_height / 3))
        self.popup.open()
        self.sounds[2].stop()

    def animate_flake_duration(self):
        if self.get_conf_mode() == long_limit_mode:
             return random.randint(12, 24) / self.get_conf_speed()

        return random.randint(6, 12) / self.get_conf_speed()

    def animate_flake(self, instance):
        instance.text=instance.kv_value # for prompt enabled
        animation =  Animation(pos=instance.pos)
        animation += Animation(pos=(instance.pos[0], 0 - instance.size[0]),
                               duration=self.animate_flake_duration())

        animation.bind(on_complete=self.animate_flake_restart)
        animation.start(instance)

    def animate_bullet_complete(self, animation, instance):
        instance.background_color=bullet_color
        instance.button.opacity = 0
        instance.pos=(self.win_width / 2 - self.win_width / 80,
                      self.win_height / 24)
        instance.text=""
        self.sounds[0].play()

    def animate_bullet(self, instance):
        animation =  Animation(pos=instance.pos)
        animation += Animation(pos=instance.button.pos,
                               duration=float(self.get_conf_delay()/10), t="in_circ")
        animation.bind(on_complete=self.animate_bullet_complete)
        animation.start(instance)

    def help_return(self, instance = None):
        self.popup.dismiss()
        self.popup=None

    def help_press(self, instance = None):
        self.textinput.text=""
        box = BoxLayout(orientation = 'vertical', padding = (self.box_padding))  # padding fix
        setup_label = Label(text = help_info, line_height = 1.2,
                            size_hint=(1, 0.9), font_size=self.help_font_size, font_name=help_font)
        setup_button = Button(text = "return", size_hint=(1, 0.1), on_press = self.help_return)
        box.add_widget(setup_label)
        box.add_widget(setup_button)
        self.popup = Popup(title='Information', title_size = self.popup_font_size,
                           title_align = 'center', content = box, auto_dismiss = False,
                           size_hint=size_hint, size=(self.win_width * 3 / 4, self.win_height * 9 / 10))
        self.popup.open()
        return True

    def confs_press(self, instance = None):
        self.textinput.text=""
        self.sounds[2].stop()

        box = BoxLayout(orientation = 'vertical', padding = (self.box_padding))
        setup_label = Label(text = "Time | Alphabet | Mode | Cheat | Speed | FontSize | Delay | Flakes:",
                            size_hint=(1, 0.4), font_size=self.label_font_size)
        setup_input = TextInput(text=self.get_conf_all(), multiline=False, padding = (self.box_input_padding),
                               size_hint=(1, 0.3), font_size=self.input_font_size)
        setup_button = Button(text = "setup", size_hint=(1, 0.3), on_press = self.setup_press)
        setup_button.setup_input = setup_input
        box.add_widget(setup_label)
        box.add_widget(setup_input)
        box.add_widget(setup_button)
        self.popup = Popup(title='Perference', title_size = self.popup_font_size,
                           title_align = 'center', content = box, auto_dismiss = False,
                           size_hint=size_hint, size=(self.win_width * 2 / 5, self.win_height * 2 / 5))
        self.popup.open()

        return True

    def button_press(self, instance):
        if not self.get_conf_prompt():
            return True

        if instance.text == instance.kv_value:
            if self.get_conf_char() == 2 and '_' in instance.kv_key: # important to author
                instance.text = instance.kv_key.split('_')[1]
            else:
                instance.text=instance.kv_key
        else:
            instance.text=instance.kv_value

    def set_random_char(self, button):
        keys=list(self.jp_map.keys())
        if not keys:
            if self.get_conf_char() == 2:  # important to author
                value = "❤"
                key=random.choice([":D", ";)", ":P", "O.o", "\o/"])
            else:
                value = "DONE"
                key= "NULL"
            self.no_keys += 1
            button.text = value
            button.kv_key = key
            button.kv_value = value
            return True

        if self.get_conf_char() == 2:  # important to author
            keys=list(sorted(self.jp_map.keys()))
            key=keys[0]
        else:
            key = random.choice(keys)
        val = self.jp_map[key]

        if self.get_conf_mode() == char_limit_mode or \
           self.get_conf_char() == 2:  # important to author
            self.jp_map.pop(key)

        button.text = val
        button.kv_key = key
        button.kv_value = val
        return True

    def create_flake(self, i, bullet):
        width = self.win_width / (3 * self.get_conf_flakes() - 2)
        button = Button(font_name=font_name, font_size=dp(self.get_conf_fsize()),
                        pos=(width * 3 * i, self.win_height), \
                        background_color=flake_colors[i%6], on_press=self.button_press,
                        size_hint=size_hint, size = (width, width))
        self.set_random_char(button)

        button.bullet = bullet
        bullet.button = button

        self.animate_flake(button)
        self.buttons.append(button)
        return button

    def create_bullet(self, bt_img = None):
        bullet = Button(size_hint=size_hint, size=(self.win_height / 24, self.win_height / 24),
                        font_name=font_name, pos=(self.win_width / 2 - self.win_width / 80,
                        self.win_height / 24), background_color=bullet_color)
        if not bt_img:
            return bullet

        bbl = StackLayout(size=bullet.size, pos=bullet.pos)
        img = Image(source=bt_img)
        bbl.add_widget(img)
        bullet.add_widget(bbl)

        bullet.bind(on_press=self.help_press)
        return bullet

    def create_cmdline(self):
        textinput = TextInput(pos=(self.win_width / 2 - self.win_width / 80, self.win_height / 120),
                              size_hint=size_hint, size=(self.win_width / 8, self.win_height / 24),
                              multiline=False, background_color=(0,0,0,0), foreground_color=(0,0,0,1))
        self.textinput = textinput

        return self.textinput

    def create_keyboard(self):
        self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)
        Window.bind(on_resize=self.on_window_resize)

    def create_sounds(self):
        self.sounds.append(SoundLoader.load(shot_sound))
        self.sounds.append(SoundLoader.load(miss_sound))
        self.sounds.append(SoundLoader.load(bg_sound))
        self.sounds[2].loop=True
        self.sounds[2].play()

    def init_window(self):
        self.title = title
        self.textinput=None
        self.sounds=[]
        self.popup=None
        self.reset_stats()

    def load_confs(self):
        self.confs=confs
        if os.path.exists(conf_path):
            newconfs = pickle.load(open(conf_path,'rb'))
            if len(newconfs) == len(self.confs):
                self.confs = newconfs

    def build(self):
        self.load_confs()
        self.init_window()
        self.create_sounds()
        self.create_keyboard()

        self.layout = FloatLayout()
        self.reset_widgets()

        return self.layout

if __name__ == '__main__': JPTest().run()
