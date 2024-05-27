import json
import os
import time

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.list import OneLineListItem, MDList, TwoLineListItem, ThreeLineListItem, ThreeLineIconListItem, \
    IconLeftWidget, ThreeLineAvatarListItem, ImageLeftWidget, OneLineIconListItem
from kivymd.uix.navigationdrawer import MDNavigationDrawer
# from kivymd.uix.screen import Screen
from kivymd.uix.textfield import MDTextField
from kivy.lang import Builder
from helpers import username_helper, list_helper, screen_helper, menu_helper
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivymd.uix.toolbar import MDTopAppBar, MDBottomAppBar, MDActionBottomAppBarButton, MDFabBottomAppBarButton
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.storage.dictstore import DictStore
from kivy.core.window.window_sdl2 import WindowSDL
from kivy.clock import Clock

Window.size = (300, 500)


class WeatherApp(MDApp):
    def build(self):
        screen = Builder.load_string(menu_helper)
        self.theme_cls.primary_palette = "Green"
        ipt = MDTextField()

        return screen

    def on_start(self):
        self.update_items_list()

    def update_items_list(self):
        app_path = os.path.dirname(os.path.abspath(__file__))

        try:
            with open(os.path.join(app_path, "UserData.json"), "r") as j:
                datas = json.load(j)
        except FileNotFoundError:
            with open(os.path.join(app_path, "UserData.json"), "w") as j:
                datas = {}
                json.dump(datas, j)

        self.root.screens[0].ids.list_container.clear_widgets()
        for key in datas.keys():
            data = datas[key]
            icn = IconLeftWidget(icon="weather-sunny")
            city = ThreeLineIconListItem(text=key,
                                         secondary_text=f"Temperature: {data['temp']}",
                                         tertiary_text=f"Humidity: {data['hum']}",
                                         on_release=lambda x: self.change_screen("weather"))
            city.add_widget(icn)

            self.root.current_screen.ids.list_container.add_widget(city)

    def change_screen(self, destination):

        self.root.current = destination


class HomeScreen(Screen):
    is_dark: bool = False

    def change_theme(self, app_obj: WeatherApp):
        self.is_dark = not self.is_dark
        # app_obj.update_items_list()

        if self.is_dark:
            app_obj.theme_cls.theme_style = "Dark"
            self.ids.home_top_bar.left_action_items = [["weather-sunny", lambda x: self.change_theme(app_obj)]]
        else:
            app_obj.theme_cls.theme_style = "Light"
            self.ids.home_top_bar.left_action_items = [["moon-waxing-crescent", lambda x: self.change_theme(app_obj)]]


class WeatherScreen(Screen):
    def set_tables(self, city, lat: float, long: float):
        pass

    def back_to_menu(self):
        self.manager.current = "home"

    pass


class CityListScreen(Screen):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.search_event = None

    def on_enter(self, *args):
        app_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(app_path, "cities.json"), "r") as j:
            cities_json = json.load(j)

        cities = list(cities_json.keys())[:40]

        for city in cities:
            item = OneLineListItem(text=city, on_release=lambda x, city_=city: self.add_city(city_, cities_json[city_]))
            self.ids.city_list.add_widget(item)

    def add_city(self, city, city_value):
        app_path = os.path.dirname(os.path.abspath(__file__))
        # api implementation here...
        # city_value: {"lat": latitude, "long": longitude}
        with open(os.path.join(app_path, "UserData.json"), "r") as j:
            datas: dict = json.load(j)
            # dummy data for now...
        datas[city] = {"temp": 10, "hum": 80}
        with open(os.path.join(app_path, "UserData.json"), "w") as j:
            json.dump(datas, j, indent=4)
        self.back_to_menu()

    def search_city(self, query):
        app_path = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(app_path, "cities.json"), "r") as j:
            cities_json = json.load(j)

        if len(query) >= 3:
            cities_ = list(cities_json.keys())
            cities = [city for city in cities_ if query in city.lower()]
            self.ids.city_list.clear_widgets()
            for city in cities:
                item = OneLineListItem(text=city,
                                       on_release=lambda x, city_=city: self.add_city(city_, cities_json[city_]))
                self.ids.city_list.add_widget(item)
        else:
            self.ids.city_list.clear_widgets()

            cities = list(cities_json.keys())[:40]

            for city in cities:
                item = OneLineListItem(text=city,
                                       on_release=lambda x, city_=city: self.add_city(city_, cities_json[city_]))
                self.ids.city_list.add_widget(item)

    def on_text(self, instance):
        if self.search_event:
            self.search_event.cancel()

        self.search_event = Clock.schedule_once(lambda dt: self.search_city(instance.text), 0.2)

    def back_to_menu(self):
        self.manager.current = "home"
        app = MDApp.get_running_app()
        app.update_items_list()


if __name__ == "__main__":
    sm = ScreenManager()
    sm.add_widget(HomeScreen(name='home'))
    sm.add_widget(WeatherScreen(name='weather'))
    sm.add_widget(CityListScreen(name='cities'))

    WeatherApp().run()
