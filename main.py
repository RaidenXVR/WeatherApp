import json
import os
import time

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, ThreeLineIconListItem, IconLeftWidget
from kivymd.uix.textfield import MDTextField
from kivy.lang import Builder
from helpers import menu_helper
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.graphics import *

Window.size = (300, 500)


class WeatherApp(MDApp):
    def build(self):
        screen = Builder.load_string(menu_helper)

        self.theme_cls.primary_palette = "Blue"
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
        """
        Function to toggle change theme to dark or light.

        :param app_obj: The currently running WeatherApp instance.
        :return:
        """
        self.is_dark = not self.is_dark
        # app_obj.update_items_list()

        if self.is_dark:
            app_obj.theme_cls.theme_style = "Dark"
            with self.canvas.before:

                Rectangle(pos=self.pos, size=self.size, source="./images/home_bg_dm.png")
            self.ids.home_top_bar.left_action_items = [["weather-sunny", lambda x: self.change_theme(app_obj)]]
        else:
            app_obj.theme_cls.theme_style = "Light"
            with self.canvas.before:
                Rectangle(pos=self.pos, size=self.size, source="./images/home_bg_lm.png")

            self.ids.home_top_bar.left_action_items = [["moon-waxing-crescent", lambda x: self.change_theme(app_obj)]]


class WeatherScreen(Screen):
    def set_tables(self, city: str, lat: float, long: float):
        pass

    def back_to_menu(self):
        self.manager.current = "home"

    pass


class CityListScreen(Screen):
    search_event = None

    def on_enter(self):
        """
        Function to update the List of City upon entering the search functionality. Called automatically on enter.
        :return:
        """
        app_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(app_path, "cities.json"), "r") as j:
            cities_json = json.load(j)

        cities = list(cities_json.keys())[:40]

        for city in cities:
            item = OneLineListItem(text=city, on_release=lambda x, city_=city: self.add_city(city_, cities_json[city_]))
            self.ids.city_list.add_widget(item)

    def add_city(self, city, city_value):
        """
        Function to add city to Home and Weather, then saving it to a JSON file.

        :param city: The name of the city.
        :param city_value: The Latitude and Longitude coordinate of the city.
        :return:
        """
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
        """
        Function to search for the city in the list. It is limited to only Indonesia Cities.
        :param query: the search query.
        :return:
        """
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
        """
        Function to search for cities in real-time when the input is more than 2 character with a 0.2 seconds delay.
        :param instance: The search box that hold the search query.
        :return:
        """
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
