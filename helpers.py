username_helper = """
MDTextField:
    hint_text: "Username..."
    helper_text: "Forgot Username?"
    helper_text_mode: "on_focus"
    icon_right: "weather-cloudy"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {"center_x":0.5,"center_y":0.5}
    size_hint_x: None
    width: 300
"""

list_helper ="""
Screen:
    ScrollView:
        MDList:
            id: list_container
"""

screen_helper="""
#: import MDActionBottomAppBarButton kivymd.uix.toolbar.MDActionBottomAppBarButton
Screen:
    MDNavigationLayout:
        ScreenManager:
            Screen:
                BoxLayout:
                    orientation: 'vertical'
                    MDTopAppBar:
                        title: "Toolbar Demo"
                        anchor_title: 'left'
                        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]
                        right_action_items: [["help", lambda x: app.navigation_draw()]]
                        elevation: 5
                    MDLabel:
                        text: "Hello World!"
                        halign: 'center'    
        
                    MDBottomAppBar:
                        id: bottom_bar
                        action_items: [MDActionBottomAppBarButton(icon="language-python", pos_hint={"center_x":0.1, "center_y":0.5}),MDActionBottomAppBarButton(icon="coffee",pos_hint={"center_x":0.27, "center_y":0.5}) ]
                        size_hint_y: 0.15
                        allow_hidden: True
            
        MDNavigationDrawer:
            id: nav_drawer
            size_hint: (0.9,1)
            BoxLayout:
                MDIconButton:
                    icon: "close"
                    pos_hint: {"center_x":0.05,"center_y":0.95}
                    on_release: nav_drawer.set_state("close")
                    pos_hint: {"center_x": 1,"center_y":0.95}
                MDLabel:
                    text: "Fitran Alfian Nizar"
                    font_style: "Subtitle1"
                    pos_hint: {"center_x": 1,"center_y":0.95}       
"""

menu_helper="""
#: import MDTextField kivymd.uix.textfield.MDTextField
ScreenManager:
    HomeScreen:
    WeatherScreen:
    CityListScreen:
    
<HomeScreen>:
    id: home
    name: 'home'
    BoxLayout:
        id: box_layout
        size_hint: 1,1
        orientation: 'vertical'
        
        MDTopAppBar:
            id: home_top_bar
            title: "Weathers"
            left_action_items: [["moon-waxing-crescent", lambda x: home.change_theme(app)]]
            right_action_items: [["help"]]
            anchor_title: 'center'
            elevation: 5
        
        ScrollView:
            id: scroll_view
            size_hint: 1,0.5
            MDList:
                id: list_container
        
    MDFloatingActionButton:
        icon: "plus"
        pos_hint: {"center_x":0.8,"center_y":0.1}
        on_release: app.change_screen('cities')
            
            

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