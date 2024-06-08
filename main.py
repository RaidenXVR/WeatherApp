import asyncio
import json
import os

from datetime import datetime, timedelta

from kivy.animation import Animation
from kivy.metrics import sp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.list import ThreeLineRightIconListItem, OneLineListItem, ImageRightWidget, ILeftBody, IRightBodyTouch
from kivy.lang import Builder
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.swiper import MDSwiperItem
from kivymd.uix.selectioncontrol import MDCheckbox

from helpers import menu_helper
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.graphics import *
from functions import get_weather, get_location


class WeatherApp(MDApp):
    del_trig = False
    checked_cities = []

    def build(self):
        screen = Builder.load_string(menu_helper)
        self.theme_cls.primary_palette = "Blue"

        return screen

    async def show_details(self):
        app_path = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(app_path, "UserData.json"), "r") as d:
                datas = json.load(d)

        except FileNotFoundError:
            datas = {"saved_cities": {}, "last_update": datetime.now().isoformat()}
            try:
                city, lat, lon = await get_location()
                city_weather = await get_weather(lat, lon)
                datas["saved_cities"][city] = city_weather
            except Exception as e:
                dialog = MDDialog(text="Cannot Use GPS. Please Add City Manually.", buttons=[
                    MDFlatButton(
                        text="Cancel",
                        theme_text_color="Custom",
                        on_release=lambda x: self.stop()
                    ),
                    MDFlatButton(
                        text="Add City",
                        theme_text_color="Custom",

                    ),
                ])
                dialog.buttons[1].bind(on_release= lambda x: self.change_screen("cities"))
                dialog.buttons[1].bind(on_release=lambda x: dialog.dismiss())
                dialog.open()

                return
        saved_cities = datas["saved_cities"]

        screen = [obj for obj in self.root.screens if obj.__class__.__name__ == "WeatherScreen"][0]
        screen.ids.swiper_main.children[0].clear_widgets()

        for city in saved_cities.keys():
            city_datas = {"Now": saved_cities[city]["current"]}
            for time_forecast in saved_cities[city]["forecast"]:
                city_datas[time_forecast] = saved_cities[city]["forecast"][time_forecast]

            swiper = SwipeItem(city=city, city_data=city_datas)

            screen.ids.swiper_main.add_widget(swiper)

    def on_start(self):

        asyncio.run(self.show_details())
        pass

    def update_items_list(self):
        app_path = os.path.dirname(os.path.abspath(__file__))

        try:
            with open(os.path.join(app_path, "UserData.json"), "r") as j:
                datas = json.load(j)
        except FileNotFoundError as e:
            dialog = MDDialog(text="Please add a city from the list or search for a city.",
                              buttons=[MDFlatButton(text="Ok", on_release=lambda x: dialog.dismiss())])
            dialog.open()
            self.change_screen("cities")
            return
        screen = [obj for obj in self.root.screens if obj.__class__.__name__ == "HomeScreen"][0]
        screen.ids.list_container.clear_widgets()

        for key in datas["saved_cities"].keys():
            data = datas["saved_cities"][key]

            icn = ImageRightWidget(source=f"./images/{data['current']['icon']}.png", size=(200, 200),
                                   size_hint=[None, None], padding=[0, "20dp", 0, 0])
            city = ThreeLineRightIconListItem(text=f"{data['current']['temp']}°C",
                                              secondary_text=key,
                                              tertiary_text=f"Humidity: {data['current']['hum']}%",
                                              on_release=lambda x: self.change_screen("weather"), divider='Inset',
                                              divider_color=[244 / 255, 249 / 255, 249 / 255, 0.7])

            city.height = 250
            city.font_style = "H4"
            city.md_label.bold = True
            city.secondary_font_style = "H6"
            if self.theme_cls.theme_style == "Light":
                city.text_color = [10 / 255, 25 / 255, 49 / 255, 0.8]
                city.secondary_text_color = [10 / 255, 25 / 255, 49 / 255, 1]
                city.tertiary_text_color = [10 / 255, 25 / 255, 49 / 255, 1]
            else:
                city.text_color = [244 / 255, 249 / 255, 249 / 255, 0.7]
                city.secondary_text_color = [244 / 255, 249 / 255, 249 / 255, 0.7]
                city.tertiary_text_color = [244 / 255, 249 / 255, 249 / 255, 0.7]

            city.add_widget(icn)

            city.children[0].size_hint_x = 0.3

            screen.ids.list_container.add_widget(city)

    async def update_weather(self):

        app_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(app_path, "UserData.json"), "r") as n:
            user_data = json.load(n)

        names = list(user_data["saved_cities"].keys())
        last_up = user_data["last_update"]

        if last_up is not None:
            last_up = datetime.fromisoformat(last_up)
            now = datetime.now()
            delta = now - last_up

            if delta <= timedelta(minutes=10):
                return

        with open(os.path.join(app_path, "cities.json"), "r") as c:
            city_list = json.load(c)
        coor = []
        for name in names:
            coor.append(city_list[name])
        idx = 0
        new_datas = {}
        try:
            for c in coor:
                new_datas[names[idx]] = await get_weather(float(c["lat"]), float(c["long"]))
        except Exception as e:
            dialog = MDDialog(text="Cannot Retrieve Location.", buttons=[
                MDFlatButton(
                    text="Cancel",
                    theme_text_color="Custom",
                    on_release=lambda x: self.stop()
                ),
                MDFlatButton(
                    text="Retry",
                    theme_text_color="Custom",
                    on_release=lambda x: self.change_screen("cities")
                ),
            ])
            dialog.open()

            return
        with open(os.path.join(app_path, "UserData.json"), "r") as ds:
            datas = json.load(ds)

        datas["saved_cities"] = new_datas
        datas["last_update"] = datetime.now().isoformat()

        with open(os.path.join(app_path, "UserData.json"), "w") as dt:
            json.dump(datas, dt)

        self.update_items_list()

    def change_screen(self, destination):

        self.root.current = destination

    def reload(self, *args):
        asyncio.run(self.update_weather())
        self.update_items_list()

        def done(*args):
            screen.ids.scroll_view.refresh_done()

        screen = [obj for obj in self.root.screens if obj.__class__.__name__ == "HomeScreen"][0]
        Clock.schedule_once(done, 2)

    def del_trigger_off(self):
        screen = [obj for obj in self.root.screens if obj.__class__.__name__ == "HomeScreen"][0]

        hide_anim = Animation(opacity=0, duration=0.5)
        hide_anim.start(screen.ids.back_butt)

        show_anim = Animation(opacity=1, duration=0.5)
        show_anim.start(screen.ids.add_button)
        show_anim.start(screen.ids.theme_button)

        screen.ids.add_button.disabled = False
        screen.ids.tray_button.icon = "trash-can"
        screen.ids.theme_button.disabled = False
        screen.ids.back_butt.disabled = True
        self.del_trig = False
        self.checked_cities.clear()
        self.update_items_list()

    def del_trigger_on(self):
        app_path = os.path.dirname(os.path.abspath(__file__))
        screen = [obj for obj in self.root.screens if obj.__class__.__name__ == "HomeScreen"][0]
        if not self.del_trig:

            screen.ids.list_container.clear_widgets()
            screen.ids.add_button.disabled = True
            hide_anim = Animation(opacity=0, duration=0.5)
            hide_anim.start(screen.ids.add_button)
            hide_anim.start(screen.ids.theme_button)

            show_anim = Animation(opacity=1, duration=0.5)
            show_anim.start(screen.ids.back_butt)
            screen.ids.tray_button.icon = "delete-empty"
            screen.ids.theme_button.disabled = True

            screen.ids.back_butt.disabled = False

            with open(os.path.join(app_path, "UserData.json"), "r") as j:
                datas = json.load(j)
            for key in datas["saved_cities"].keys():
                checkbox = CheckboxLeftWidget(size=["48dp", "48dp"])
                checkbox.bind(active=self.on_box_checked)

                data = datas["saved_cities"][key]
                city = ThreeLineRightIconListItem(text=f"{data['current']['temp']}°C",
                                                  secondary_text=key,
                                                  tertiary_text=f"Humidity: {data['current']['hum']}%",
                                                  on_release=lambda x: self.change_screen("weather"), divider='Inset',
                                                  divider_color=[244 / 255, 249 / 255, 249 / 255, 0.7])
                city.add_widget(checkbox)
                city.height = 250
                city.font_style = "H4"
                city.md_label.bold = True
                city.secondary_font_style = "H6"

                city.children[0].size_hint_x = 0.3

                screen.ids.list_container.add_widget(city)

            self.del_trig = True
        else:
            if len(self.checked_cities) == 0:
                self.del_trigger_off()
                return
            with open(os.path.join(app_path, "UserData.json"), "r") as u:
                datas: dict = json.load(u)

            for boxes in self.checked_cities:
                text = boxes.parent.parent.secondary_text
                datas["saved_cities"].pop(text)

            with open(os.path.join(app_path, "UserData.json"), "w") as u:
                json.dump(datas, u)

            screen.ids.list_container.clear_widgets()

            for key in datas["saved_cities"].keys():
                checkbox = CheckboxLeftWidget(size=["48dp", "48dp"])
                checkbox.bind(active=self.on_box_checked)

                data = datas["saved_cities"][key]
                city = ThreeLineRightIconListItem(text=f"{data['current']['temp']}°C",
                                                  secondary_text=key,
                                                  tertiary_text=f"Humidity: {data['current']['hum']}%",
                                                  on_release=lambda x: self.change_screen("weather"), divider='Inset',
                                                  divider_color=[244 / 255, 249 / 255, 249 / 255, 0.7])
                city.add_widget(checkbox)
                city.height = 250
                city.font_style = "H4"
                city.md_label.bold = True
                city.secondary_font_style = "H6"

                city.children[0].size_hint_x = 0.3

                screen.ids.list_container.add_widget(city)
            self.checked_cities.clear()
            self.del_trig = False

    def on_box_checked(self, checkbox, value):
        if value:
            self.checked_cities.append(checkbox)
        else:
            self.checked_cities.remove(checkbox)


class HomeScreen(Screen):
    is_dark: bool = False
    app_obj = None

    def set_app(self, app):
        self.app_obj = app

    def reload(self, app):
        asyncio.run(app.update_weather())

    def change_theme(self, app_obj: WeatherApp = None):
        """
        Function to toggle change theme to dark or light.

        :param app_obj: The currently running WeatherApp instance.
        :return:
        """
        if app_obj is None:
            app_obj = self.app_obj
        self.is_dark = not self.is_dark

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

        # app_obj.update_items_list()


class WeatherScreen(Screen):
    bg_image = "./images/morning.png"
    images = ["./images/morning.png", "./images/noon.png", "./images/evening.png"]
    current_index = 0

    def reload(self, app):
        asyncio.run(app.update_weather())
        asyncio.run(app.show_details())
        pass

    def on_swipe(self, swiper):
        # print("swipe")
        index = swiper.get_current_index()
        # print(index)
        if self.current_index != index:
            self.bg_image = self.images[index if index < 3 else index % len(self.images)]
            with self.canvas.before:
                Rectangle(size=self.size, source=self.bg_image)
            self.current_index = index

    def back_to_menu(self):
        self.manager.current = "home"

    pass


class CityListScreen(Screen):
    search_event = None
    app_obj = None

    def set_app(self, app):
        self.app_obj = app

    def on_enter(self):
        """
        Function to update the List of City upon entering the search functionality. Called automatically on enter.
        :return:
        """
        app: WeatherApp = WeatherApp().get_running_app()

        app_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(app_path, "cities.json"), "r") as j:
            cities_json = json.load(j)

        cities = list(cities_json.keys())[:40]

        for city in cities:
            item = OneLineListItem(text=city, on_release=lambda x, city_=city: self.add_city(
                city_, cities_json[city_]))
            self.ids.city_list.add_widget(item)

    def add_city(self, city: str, city_value: dict):
        """
        Function to add city to Home and Weather, then saving it to a JSON file.

        :param city: The name of the city.
        :param city_value: The Latitude and Longitude coordinate of the city.
        :return:
        """

        self.app_obj.update_weather()

        app_path = os.path.dirname(os.path.abspath(__file__))
        # api implementation here...
        # city_value: {"lat": latitude, "long": longitude}
        lat = float(city_value["lat"])
        long = float(city_value["long"])
        try:

            city_weather = asyncio.run(get_weather(lat, long))
        except Exception as e:
            dialog = MDDialog(text="Cannot Use GPS. Please Add City Manually", buttons=[
                MDFlatButton(
                    text="Cancel",
                    theme_text_color="Custom",
                    on_release=lambda x: self.stop()
                ),
                MDFlatButton(
                    text="Retry",
                    theme_text_color="Custom",
                    on_release=lambda x: self.change_screen("cities")
                ),
            ])
            dialog.open()

            return
        try:
            with open(os.path.join(app_path, "UserData.json"), "r") as j:
                datas: dict = json.load(j)
        except FileNotFoundError:
            datas={"saved_cities":{}, "last_update": None}
        datas["saved_cities"][city] = city_weather
        datas["last_update"] = datetime.now().isoformat()

        with open(os.path.join(app_path, "UserData.json"), "w") as j:
            json.dump(datas, j, indent=4)

        self.back_to_menu(self.app_obj)

    async def on_gps_click(self):
        """
        Function to add city to Home and Weather, then saving it to a JSON file.
        :return:
        """
        app_path = os.path.dirname(os.path.abspath(__file__))
        # api implementation here...
        # city_value: {"lat": latitude, "long": longitude}

        try:
            city, lat, lon = await get_location()
            city_weather = await get_weather(lat, lon)
        except Exception as e:
            dialog = MDDialog(text="Cannot Use GPS. Please Add City Manually.", buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=lambda x: self.app_obj.stop()
                ),
                MDFlatButton(
                    text="Add City",
                ),
            ])
            dialog.buttons[1].bind(on_release=lambda x: self.app_obj.change_screen("cities"))
            dialog.buttons[1].bind(on_release=lambda x: dialog.dismiss())
            dialog.open()

            return
        with open(os.path.join(app_path, "UserData.json"), "r") as j:
            datas: dict = json.load(j)

        datas["saved_cities"][city] = city_weather
        datas["last_update"] = datetime.now().isoformat()

        with open(os.path.join(app_path, "UserData.json"), "w") as j:
            json.dump(datas, j, indent=4)

        self.back_to_menu(self.app_obj)

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

    def back_to_menu(self, app_obj: WeatherApp = None):

        # app = WeatherApp.get_running_app()
        self.manager.current = "home"
        if app_obj is not None:
            app_obj.update_items_list()
            asyncio.run(app_obj.show_details())
        else:
            self.app_obj.update_items_list()
        # self.manager.current_screen.reload()


class SwipeItem(MDSwiperItem):

    def __init__(self, city, city_data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.orientation = 'vertical'
        layout = MDRelativeLayout(size=self.size)

        city_label = MDLabel(text=city, pos_hint={"center_x": 0.5, "center_y": 0.92}, size_hint=[None, None],
                             font_style="H4", bold=True)
        city_label.adaptive_size = True
        city_label.adaptive_width = True

        temp = MDLabel(text=str(city_data["Now"]["temp"]), pos_hint={"center_x": 0.5, "center_y": 0.8},
                       font_style="H3", bold=True)
        temp_unit = MDLabel(text="°C", pos_hint={"right": 0.97, "center_y": 0.82}, bold=True, size_hint=(None, None),
                            size_hint_x=None)
        temp.adaptive_size = True
        temp.adaptive_width = True

        date = MDLabel(text=datetime.today().strftime("%d %B %Y"), pos_hint={"center_x": 0.5, "center_y": 0.7})
        date.adaptive_size = True
        date.adaptive_width = True

        app = WeatherApp.get_running_app()

        details = MDCard(pos_hint={"center_x": 0.5, "center_y": 0.5}, md_bg_color=[1, 1, 1, 1], size_hint=[1, 0.15])
        grid = MDGridLayout(cols=5, padding="10dp", spacing="2dp")

        # UV Index
        uv_box = MDBoxLayout(orientation='vertical', spacing='5dp')
        uv_heading = MDBoxLayout(orientation='horizontal', spacing='5dp')
        uv_icon = MDIcon(icon="weather-sunny", size_hint=(None, None), size=("8dp", "8dp"))
        uv_label = MDLabel(text="UV Index", halign="left", font_style="Caption", size_hint_x=None)
        uv_heading.add_widget(uv_icon)
        uv_heading.add_widget(uv_label)
        uv_value = MDLabel(text=city_data["Now"]["uv"], halign="center", font_style="Caption")
        uv_box.add_widget(uv_heading)
        uv_box.add_widget(uv_value)

        # Wind
        wind_box = MDBoxLayout(orientation='vertical', spacing='5dp')
        wind_heading = MDBoxLayout(orientation='horizontal', spacing='5dp')
        wind_icon = MDIcon(icon="weather-windy", size_hint=(None, None), size=("8dp", "8dp"))
        wind_label = MDLabel(text="Wind", halign="left", font_style="Caption", size_hint_x=None)
        wind_heading.add_widget(wind_icon)
        wind_heading.add_widget(wind_label)
        wind_value = MDLabel(text=f'{city_data["Now"]["wind"]} m/s', halign="center", font_style="Caption")
        wind_box.add_widget(wind_heading)
        wind_box.add_widget(wind_value)

        # Humidity
        humidity_box = MDBoxLayout(orientation='vertical', spacing='2dp')
        humidity_heading = MDBoxLayout(orientation='horizontal', spacing='2dp')
        humidity_icon = MDIcon(icon="water-percent", size_hint=(None, None), size=("8dp", "8dp"))
        humidity_label = MDLabel(text="Humidity", halign="left", font_style="Caption", size_hint_x=None)
        humidity_heading.add_widget(humidity_icon)
        humidity_heading.add_widget(humidity_label)
        humidity_value = MDLabel(text=f'{city_data["Now"]["hum"]}%', halign="center", font_style="Caption", )
        humidity_box.add_widget(humidity_heading)
        humidity_box.add_widget(humidity_value)

        # Add the boxes and separators to the grid
        grid.add_widget(uv_box)
        grid.add_widget(MDSeparator(orientation='vertical'))  # Separator between UV Index and Wind
        grid.add_widget(wind_box)
        grid.add_widget(MDSeparator(orientation='vertical'))  # Separator between Wind and Humidity
        grid.add_widget(humidity_box)

        # Add the grid to the card
        details.add_widget(grid)

        # Forecast
        forecast_card = MDCard(pos_hint={"center_x": 0.5, "center_y": 0.32}, md_bg_color=[1, 1, 1, 1],
                               size_hint=[1, 0.2])
        forecast_layout = MDGridLayout(cols=5, padding="10dp", spacing="5dp")

        for forecast in city_data:
            box = MDBoxLayout(orientation='vertical', spacing=5)
            time_label = MDLabel(text=forecast, font_style="Caption", halign="center", valign="top")
            forecast_temp = MDLabel(text=city_data[forecast]["temp"] + "°", font_style="Caption", halign="center",
                                    valign="center", bold=True)
            forecast_icon = MDIcon(size_hint=(None, None), size=("12dp", "12dp"), halign="center", valign="bottom",
                                   padding=["10dp", 0, 0, 0])
            match city_data[forecast]["weather"]:
                case "Clear":
                    forecast_icon.icon = "weather-sunny"
                case "Thunderstorm":
                    forecast_icon.icon = "weather-lightning"
                case "Drizzle":
                    forecast_icon.icon = "weather-pouring"
                case "Rain":
                    forecast_icon.icon = "weather-rainy"

                case "Snow":
                    forecast_icon.icon = "snowflake"
                case "Atmosphere":
                    forecast_icon.icon = "weather-hazy"
                case "Clouds":
                    if city_data[forecast]["weather_desc"] == "few clouds":
                        forecast_icon.icon = "weather-partly-cloudy"
                    elif city_data[forecast]["weather_desc"] == "scattered clouds":
                        forecast_icon.icon = "weather-cloudy"
                    else:
                        forecast_icon.icon = "clouds"

            box.add_widget(time_label)
            box.add_widget(forecast_temp)
            box.add_widget(forecast_icon)
            forecast_layout.add_widget(box)

        forecast_card.add_widget(forecast_layout)
        # Add all to the main frame
        layout.add_widget(city_label)
        layout.add_widget(temp)
        layout.add_widget(temp_unit)
        layout.add_widget(date)
        layout.add_widget(details)
        layout.add_widget(forecast_card)
        self.add_widget(layout)

    pass


class CheckboxLeftWidget(IRightBodyTouch, MDCheckbox):
    pass


if __name__ == "__main__":
    sm = ScreenManager()

    sm.add_widget(WeatherScreen(name='weather'))

    sm.add_widget(HomeScreen(name='home'))
    sm.add_widget(CityListScreen(name='cities'))

    WeatherApp().run()
