menu_helper = """
#: import MDTextField kivymd.uix.textfield.MDTextField
#: import asyncio asyncio
# # : import functions.app_storage_path android.storage.functions.app_storage_path
#: import functions functions
#: import os os
ScreenManager:
    WeatherScreen:
    HomeScreen:
    CityListScreen:
    
<HomeScreen>:
    id: home
    name: 'home'
    on_enter: self.set_app(app)
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: os.path.join(functions.app_storage_path(),"images/home_bg_lm.png") if app.theme_cls.theme_style == "Light" else os.path.join(functions.app_storage_path(),"images/home_bg_dm.png")
    MDIconButton:
        id: back_butt
        md_bg_color: [244/255,249/255,249/255,0.7] if app.theme_cls.theme_style == "Light" else [7/255,37/255,65/255,0.7]
        size: "20sp", "20sp"
        icon_size: "16sp"
        icon: "arrow-left-thick" 
        disabled: True
        on_release: app.del_trigger_off()
        opacity: 0
        pos_hint: {"center_x":0.1, "center_y":0.94}
    MDIconButton:
        id: theme_button
        md_bg_color: [244/255,249/255,249/255,0.7] if app.theme_cls.theme_style == "Light" else [7/255,37/255,65/255,0.7]
        size: "20sp", "20sp"
        icon_size: "16sp"
        icon: "moon-waxing-crescent" 
        on_release: home.change_theme(app)
        pos_hint: {"center_x":0.1, "center_y":0.94}
        
    MDIconButton:
        id: tray_button
        md_bg_color: [244/255,249/255,249/255,0.7] if app.theme_cls.theme_style == "Light" else [7/255,37/255,65/255,0.7]
        size: "20sp", "20sp"
        icon_size: "16sp"
        icon: "trash-can"
        pos_hint: {"center_x":0.9, "center_y":0.94}
        on_release: app.del_trigger_on()
        
    MDFillRoundFlatButton:
        id: add_button
        icon: "plus"
        text: "Add other city..."
        text_color: [0,0,0,1] if app.theme_cls.theme_style == "Light" else [1,1,1,1]
        pos_hint: {"center_x":0.5,"center_y":0.94}
        on_release: app.change_screen('cities')
        md_bg_color: [244/255,249/255,249/255,0.7] if app.theme_cls.theme_style == "Light" else [7/255,37/255,65/255,0.7]
        
    BoxLayout:
        id: box_layout
        size_hint: 1,0.93
        orientation: 'vertical'
        padding: [0,50,0,0]     
        MDScrollViewRefreshLayout:
            root_layout: root
            id: scroll_view
            size_hint: 1,1
            pos_hint: {"center_x": 0.5, "center_y":0.8}
            refresh_callback: lambda :app.reload()
            MDList:
                id: list_container
        

<WeatherScreen>:
    id: weather 
    name: 'weather'
    canvas.before:
        Rectangle: 
            size:self.size
            source: self.bg_image
     
    MDIconButton:
        id: theme_button
        md_bg_color: [244/255,249/255,249/255,0.7] if app.theme_cls.theme_style == "Light" else [7/255,37/255,65/255,0.7]
        size: "20sp", "20sp"
        icon_size: "16sp"
        icon: "arrow-left-thick"
        on_release: weather.back_to_menu(); app.update_items_list();
        pos_hint: {"center_x":0.1, "center_y":0.94}
        
    MDIconButton:
        id: tray_button
        md_bg_color: [244/255,249/255,249/255,0.7] if app.theme_cls.theme_style == "Light" else [7/255,37/255,65/255,0.7]
        size: "20sp", "20sp"
        icon_size: "16sp"
        icon: "reload"
        pos_hint: {"center_x":0.9, "center_y":0.94}
        on_release: weather.reload(app)
        
        
    MDSwiper:
        id: swiper_main
        size_hint_y: None
        height: weather.height - dp(50)
        radius: [dp(20),]
        # padding: [20,20,20,20]
        width_mult: 1.001
        on_swipe: weather.on_swipe(swiper_main)
        

        
        
        
<CityListScreen>:
    id: cities
    name: 'cities'
    on_enter: self.on_enter();self.set_app(app)
    BoxLayout:
        canvas.before:
            Rectangle:
                pos: self.pos
                size: self.size
                source: os.path.join(functions.app_storage_path(),"images/home_bg_lm.png") if app.theme_cls.theme_style == "Light" else os.path.join(functions.app_storage_path(),"images/home_bg_dm.png")
                
        size_hint: 1,1
        orientation: 'vertical'
        BoxLayout:
            padding: [0,"20sp", 0,"20sp"]
            size_hint: 1,0.15
            adaptive_size: True
            adaptive_height: True
            
            
            MDIconButton:
                icon: "arrow-left-thick"
                pos_hint: {"center_x":0.2, "center_y":0.5}
                on_release: cities.back_to_menu()
            
            MDLabel:
                text: "Search for City"
                pos_hint: {"center_x":0.5, "center_y":0.5}
                # md_bg_color: [1,1,1,1]
                font_style: "H5"
                bold: True
            MDIconButton:
                icon: 'crosshairs-gps'
                pos_hint: {"center_x":0.8, "center_y":0.5}
                on_release: asyncio.run(cities.on_gps_click())
  
        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,0.1
            padding: [0,"10sp", 0,0]
            MDTextField:
                id: city_input
                hint_text: "Search City..."
                helper_text: "Minimal 3 Characters."
                helper_text_mode: 'persistent'
                # fill_color_normal: [244/255,249/255,249/255,1] if app.theme_cls.theme_style == "Dark" else [7/255,37/255,65/255,1]
                pos_hint: {"top":1, "center_x":0.5}
                size_hint_x: 0.9
                mode: "round"
                icon_left: 'map-search'
                on_text: cities.on_text(self)
                
        BoxLayout:
            padding: [10,"20sp",10,"10sp"]
            ScrollView:
                MDList:
                    id: city_list     

            
"""

get_saved_cities_current_data_query = """select * from SavedWeatherData;"""

get_saved_cities_forecast_data_query = """select swd.city_name, fw.* 
from SavedWeatherData as swd
inner join ForecastWeathers as fw on swd.city_name = fw.city_name;
"""

insert_current_data_query = """INSERT INTO SavedWeatherData (city_name, weather, weather_desc, temp, hum, icon, uv, wind)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(city_name) DO UPDATE SET
    weather = excluded.weather,
    weather_desc = excluded.weather_desc,
    temp = excluded.temp,
    hum = excluded.hum,
    icon = excluded.icon,
    uv = excluded.uv,
    wind = excluded.wind;
"""

delete_saved_city_queries = ["""Delete from SavedWeatherData where city_name = ?
""",
                             """Delete from ForecastWeathers where city_name = ?
                             """]

delete_forecast_query = """Delete from ForecastWeathers where city_name = ?
                     """

insert_forecast_query = """INSERT INTO ForecastWeathers (forecast_hour, weather, weather_desc, temp, icon, city_name)
    VALUES (?, ?, ?, ?, ?, ?) 
"""

delete_last_up="""delete from LastUpdate"""
update_last_up = """insert into LastUpdate (last_up) values ( ? )"""
get_last_up = """select * from LastUpdate"""