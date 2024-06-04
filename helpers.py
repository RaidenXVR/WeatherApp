menu_helper="""
#: import MDTextField kivymd.uix.textfield.MDTextField
ScreenManager:
    HomeScreen:
    WeatherScreen:
    CityListScreen:
    
<HomeScreen>:
    id: home
    name: 'home'
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: "./images/home_bg_lm.png"
    
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
        icon: "rhombus-split"
        pos_hint: {"center_x":0.9, "center_y":0.94}
        
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
        ScrollView:
            id: scroll_view
            size_hint: 1,1
            pos_hint: {"center_x": 0.5, "center_y":0.8}
            MDList:
                id: list_container
        


            
            

<WeatherScreen>:
    id: weather 
    name: 'weather'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            id: weather_top_bar
            left_action_items: [["arrow-left", lambda x: weather.back_to_menu()]]
            title: "Weather Details"
        MDLabel:
            text: "Weather Details Table Here"
            halign: 'center'
            valign: 'center'
            
        
        
<CityListScreen>:
    id: cities
    name: 'cities'
    BoxLayout:
        # pos_hint: {"center_x":0.5, "center_y": 1}
        size_hint: 1,1
        orientation: 'vertical'
        MDTopAppBar:
            id: search_top_bar
            size_hint: 1,0.1
            left_action_items: [["arrow-left", lambda x: cities.back_to_menu()]]
            # right_action_items: [[]]
            elevation: 5
            
        
        MDTextField:
            id: city_input
            hint_text: "Search City..."
            helper_text: "Minimal 3 Characters."
            helper_text_mode: 'persistent'
            pos_hint: {"top":1}
            # size_hint: 0.8,1
            color_mode: "custom"
            mode: "line"
            line_color_focus: 0,0,0,0.7
            text_color_focus: 0,0,0,0.7
            hint_text_color_focus: 0,0,0,0.7
            icon_left: 'map-search'
            color_active: 0,0,0,0.7
            on_text: cities.on_text(self)

        
        ScrollView:
            size_hint: 1,0.5
            MDList:
                id: city_list
            
"""