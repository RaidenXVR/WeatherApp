import json
import os
import time

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem,ImageRightWidget, ThreeLineRightIconListItem
from kivy.lang import Builder
from helpers import menu_helper
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.graphics import *



class WeatherApp(MDApp):
    def build(self):
        screen = Builder.load_string(menu_helper)

        self.theme_cls.primary_palette = "Blue"

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

            icn = ImageRightWidget(source="./images/few_cloud-day.png")
            # img = FitImage(source="./images/partly_cloudy.png")
            # icn.add_widget(img)
            city = ThreeLineRightIconListItem(text=f"{data['temp']}°C",
                                              secondary_text=key,
                                              tertiary_text=f"Humidity: {data['hum']}%",
                                              on_release=lambda x: self.change_screen("weather"), divider='Inset',
                                              divider_color=[244 / 255, 249 / 255, 249 / 255, 0.7])

            city.height = 250
            city.font_style = "H3"
            city.secondary_font_style = "H5"
            if self.theme_cls.theme_style == "Light":
                city.text_color = [10/255, 25/255, 49/255,0.8]
                city.secondary_text_color =[10/255, 25/255, 49/255,1]
                city.tertiary_text_color =[10/255, 25/255, 49/255,1]
            else:
                city.text_color = [244/255,249/255,249/255,0.7]
                city.secondary_text_color = [244/255,249/255,249/255,0.7]
                city.tertiary_text_color = [244/255,249/255,249/255,0.7]

            # icn.size = [150,105]
            city.add_widget(icn)

            city.children[0].size = [250,250]
            # city.add_widget()
            # print(city.children[0].children)


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
                Rectangle(pos=self.pos, size=self.size,
                          source="./images/home_bg_dm.png")

            self.ids.theme_button.icon = "weather-sunny"
        else:
            app_obj.theme_cls.theme_style = "Light"
            with self.canvas.before:
                Rectangle(pos=self.pos, size=self.size,
                          source="./images/home_bg_lm.png")

            self.ids.theme_button.icon = "moon-waxing-crescent"

        app_obj.update_items_list()
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
            item = OneLineListItem(text=city, on_release=lambda x, city_=city: self.add_city(
                city_, cities_json[city_]))
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

        self.search_event = Clock.schedule_once(
            lambda dt: self.search_city(instance.text), 0.2)

    def back_to_menu(self):
        self.manager.current = "home"
        app = MDApp.get_running_app()
        app.update_items_list()


if __name__ == "__main__":
    Window.size = (300, 500)

    sm = ScreenManager()
    sm.add_widget(HomeScreen(name='home'))
    sm.add_widget(WeatherScreen(name='weather'))
    sm.add_widget(CityListScreen(name='cities'))

    WeatherApp().run()
