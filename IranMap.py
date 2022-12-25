#AI Path finding algorithm
#Mohammad Afshar 1399


import folium
import pandas as pd
import numpy as np
import heapq
import webbrowser
import csv
import geopy.distance
import collections
from folium.plugins import MarkerCluster, MeasureControl, AntPath
from folium_jsbutton import JsButton
from difflib import get_close_matches
from pathlib import Path
from haversine import haversine

import io
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets


#For save in current directory
current_path = Path(__file__).parent.absolute()

df = pd.read_csv(f"{str(current_path)}\ir.csv")

def A_star_map(_start = "Qazvīn", _end = "Tehran"):
    #Reading cities locations dataform
    def start_end_city():
        #Start = str(input("Please enter the name of the starting city like \"Orumiyeh\" : "))
        #End = str(input("Please enter the name of the destination city like \"Esfahan\": "))
        Start = _start
        End = _end

        names_cities = list()
        for city in range(len(df)):
            names_cities.append(df.iloc[city][0])

        cmStart = get_close_matches(Start, names_cities, n = 5, cutoff = 0)
        cmEnd = get_close_matches(End, names_cities, n = 5, cutoff = 0)

        cm_Start = [[n, c] for n, c in enumerate(cmStart)]
        cm_End = [[n, c] for n, c in enumerate(cmEnd)]
        #print("Start city -> Please enter the selected number : \n", cm_Start)
        start = 0 #int(input())
        #print("End city -> Please enter the selected number : \n", cm_End)
        end = 0 #int(input())

        start_end_list = list()
        for city in range(len(df)):
            if cm_Start[start][1] == df.iloc[city][0]:
                S_name = df.iloc[city][0]
                S_lat = df.iloc[city][1]
                S_lng = df.iloc[city][2]
            if cm_End[end][1] == df.iloc[city][0]:
                E_name = df.iloc[city][0]
                E_lat = df.iloc[city][1]
                E_lng = df.iloc[city][2]

        start_end_list.extend([S_lat, S_lng, E_lat, E_lng, S_name, E_name])
        return start_end_list


    start_end_list = start_end_city()
    #Sorted Cities DataFrame
    global cities
    cities = pd.DataFrame(columns=['city', 'lat', 'lng', 'kilometers'])


    def sort_city(init_lat:float, init_lng:float):
        distance = list()
        global cities
        global df
        for city in range(len(df)):
            # compare two locations for set color
            def cmopare_XY(lat1 = float(init_lat), lng1 = float(init_lng), lat2 = float(df.iloc[city][1]), lng2 = float(df.iloc[city][2])):
                global cities
                r = haversine([lat1, lng1], [lat2, lng2]) 
                distance.append(float(r)) #result in Kilometers
                cities = cities.append({'city':str(df.iloc[city][0]), 'lat':float(df.iloc[city][1]), 'lng':float(df.iloc[city][2]), 'kilometers':float(distance[city])}, ignore_index=True)
            
            cmopare_XY()


    # Sorted by input location by difault is tehran
    sort_city(float(start_end_list[0]), float(start_end_list[1]))
    sorted_cities = cities.sort_values(by = ['kilometers'])

    global conter
    conter = 0
    def set_color():
        global conter
        for n in range(conter, len(sorted_cities)):
            if (int(sorted_cities.iloc[n][3]) < 500):
                conter += 1
                return "green"
            elif (int(sorted_cities.iloc[n][3]) < 1200):
                conter += 1
                return "orange"
            else:
                return "red"


    #Create base map
    map = folium.Map(location = [32.4279, 53.6880], zoom_start = 6, tiles = "OpenStreetMap") #"CartoDB dark_matter"

    #Create Cluster
    marker_cluster = MarkerCluster(options={'maxClusterRadius':12}).add_to(map)

    #Create Drow tools
    draw = folium.plugins.Draw(export = True)
    draw.add_to(map)

    #showing location with click in any where in map
    map.add_child(folium.LatLngPopup()) #.setContent( "<br /><a href="+data+"> click </a>")

    #Map measure
    measure_control = MeasureControl(position = "topleft", active_color = "gold", completed_color = "gold", primary_length_unit="kilometers")
    map.add_child(measure_control)

    #map layer control
    map_layer = folium.raster_layers.TileLayer("Open Street Map").add_to(map)
    map_layer = folium.raster_layers.TileLayer("Stamen Terrain").add_to(map)
    map_layer = folium.raster_layers.TileLayer("Stamen Toner").add_to(map)
    map_layer = folium.raster_layers.TileLayer("Stamen Watercolor").add_to(map)
    map_layer = folium.raster_layers.TileLayer("CartoDB positron").add_to(map)
    map_layer = folium.raster_layers.TileLayer("CartoDB dark_matter").add_to(map)
    folium.LayerControl().add_to(map)


    #creating a specific copy dataFrame to csv file for A* search algorithm
    local_df = pd.DataFrame(columns = ["id", "name", "latitude", "longitude", "country"])
    local_df['id'] = np.arange(len(df))
    local_df['name'] = df[['city']].copy()
    local_df['latitude'] = df[['lat']].copy()
    local_df['longitude'] = df[['lng']].copy()
    local_df['country'] = df[['country']].copy()

    local_df.to_csv(str(current_path)+"\ir_.csv", sep=',', index = False, encoding='utf-8')

    ###################################################################################
    ############################## Start of Algorithm A* ##############################
    ###################################################################################

    Location = collections.namedtuple("Location", "ID name latitude longitude country".split())
    data = {}
    with open(str(current_path)+"\ir_.csv", encoding='UTF-8', newline='') as f:
        r = csv.DictReader(f)
        for d in r:
            i, n, x, y, c = int(d["id"]), d["name"], d["latitude"], d["longitude"], d["country"]
            if c == "Iran":
                data[i] = Location(i,n,x,y,c)

    def calcH(start, end):
        coords_1 = (data[start].latitude, data[start].longitude)
        coords_2 = (data[end].latitude, data[end].longitude)
        distance = (geopy.distance.geodesic(coords_1, coords_2)).km
        return distance

    def getneighbors(startlocation, n=10):
        return sorted(data.values(), key=lambda x: calcH(startlocation, x.ID))[1:n+1]

    def getParent(closedlist, index):
        path = []
        while index is not None:
            path.append(index)
            index = closedlist.get(index, None)
        return [data[i] for i in path[::-1]]

    s = list(local_df[(local_df.latitude == start_end_list[0]) & (local_df.longitude == start_end_list[1])].iloc[0])
    e = list(local_df[(local_df.latitude == start_end_list[2]) & (local_df.longitude == start_end_list[3])].iloc[0])

    startIndex = int(s[0])
    endIndex = int(e[0])
    finalpoints = list()

    Node = collections.namedtuple("Node", "ID F G H parentID".split())

    h = calcH(startIndex, endIndex)
    openlist = [(h, Node(startIndex, h, 0, h, None))] # heap
    closedlist = {} # map visited nodes to parent

    while len(openlist) >= 1:
        _, currentLocation = heapq.heappop(openlist)
        print(currentLocation)

        if currentLocation.ID in closedlist:
            continue
        closedlist[currentLocation.ID] = currentLocation.parentID

        if currentLocation.ID == endIndex:
            print("\nComplete\n")
            for p in getParent(closedlist, currentLocation.ID):
                print(p)
                finalpoints.append(p)
            break

        for other in getneighbors(currentLocation.ID):
            g = currentLocation.G + calcH(currentLocation.ID, other.ID)
            h = calcH(other.ID, endIndex)
            f = g + h
            heapq.heappush(openlist, (f, Node(other.ID, f, g, h, currentLocation.ID)))

    ###################################################################################
    ############################### End of Algorithm A* ###############################
    ###################################################################################

    #Add a button that executes JavaScript
    JsButton(
        title='<i onClick="window.location.reload()"><span class="glyphicon glyphicon-refresh"></span></i>',function="""
        function(btn, map)
        {
            map.setView([35.7000, 35.7000],5);
            btn.state('zoom-to-forest');
        }
        """).add_to(map)

    def set_marker():
        folium.Marker(location = [start_end_list[0], start_end_list[1]], tooltip = start_end_list[4], icon = folium.Icon(icon = "glyphicon-plane", color = "purple", prefix = "glyphicon")).add_to(map)
        folium.Marker(location = [start_end_list[2], start_end_list[3]], tooltip = start_end_list[5], icon = folium.Icon(icon = "glyphicon-plane", color = "purple", prefix = "glyphicon")).add_to(map)

    set_marker()

    def set_line():
        folium.PolyLine(locations = [[start_end_list[0], start_end_list[1]], [start_end_list[2], start_end_list[3]]], color="purple", weight=3, opacity=1).add_to(map)

    set_line()

    def show_path():
        final_path = list()
        for n in range(len(finalpoints)):
            final_path.append([float(finalpoints[n][2]), float(finalpoints[n][3])])
            
        folium.PolyLine(locations = [final_path]).add_to(map)
        AntPath(locations = [final_path]).add_to(map)

    show_path()

    def path_marker():
        for n in range(1, len(finalpoints)-1):
            folium.Marker(location = [finalpoints[n][2], finalpoints[n][3]], popup = finalpoints[n][1], tooltip = "click", icon = folium.Icon(icon = "glyphicon-road", prefix = "glyphicon")).add_to(map)

    path_marker()

    for city in range(len(sorted_cities)):
        folium.CircleMarker(location = [sorted_cities.iloc[city][1], sorted_cities.iloc[city][2]], radius = 6, popup = str(sorted_cities.iloc[city][0]), fill_color = "gray", tooltip = "click", color=set_color(), fill_opacity = 1.0).add_to(marker_cluster)

    map.save(outfile = f"{str(current_path)}\Iran map.html", close_file = False)
    #webbrowser.open(f"{str(current_path)}\Iran map.html")

    return map

#map = A_star_map()

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle(self.tr("MAP PROJECT"))
        #sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        #self.setFixedSize(sizeObject.width(), sizeObject.height())
        self.showMaximized()
        self.buttonUI()

    def buttonUI(self):
        shortPathButton = QtWidgets.QPushButton(self.tr("Find shortest path"))
        button2 = QtWidgets.QPushButton(self.tr("Start City"))
        button3 = QtWidgets.QPushButton(self.tr("End City"))

        combo = QtWidgets.QComboBox(self)
        for n in range(len(df)):
            combo.addItem(str(df.iloc[n][0]))

        shortPathButton.setFixedSize(120, 50)
        button2.setFixedSize(120, 50)
        button3.setFixedSize(120, 50)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(10, 10, 10, 10)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QHBoxLayout(central_widget)

        button_container = QtWidgets.QWidget()
        vlay = QtWidgets.QVBoxLayout(button_container)
        vlay.setSpacing(50)
        vlay.addStretch()
        vlay.addWidget(combo)
        vlay.addWidget(button2)
        vlay.addWidget(button3)
        vlay.addWidget(shortPathButton)
        vlay.addStretch()
        lay.addWidget(button_container)
        lay.addWidget(self.view, stretch=1)

        '''
        #get the current text contents of a ComboBox
        button_text = str(combo.currentText())
        button_text = unicode(combo.currentText())
        '''
        #Events & Signals
        start_city = [""]
        def button2_clicked():
            start_city[0] = (str(combo.currentText()))
            print(f"Start city : {start_city[0]}")
        button2.clicked.connect(button2_clicked)

        End_city = [""]
        def button3_clicked():
            End_city[0] = (str(combo.currentText()))
            print(f"End city : {End_city[0]}")
        button3.clicked.connect(button3_clicked)

        def show_path():
            map = A_star_map(start_city[0], End_city[0])
            print(f"\nBest path generated by A* Algorithm from {start_city[0]} to {End_city[0]}\n")
            data = io.BytesIO()
            map.save(data, close_file=False)
            self.view.setHtml(data.getvalue().decode())
        shortPathButton.clicked.connect(show_path)
'''
        data = io.BytesIO()
        map.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
'''
if __name__ == "__main__" :
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())