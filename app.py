import pandas as pd
import geopandas as gpd
import numpy as np
import geoplot.crs as gcrs

import folium
from folium import Choropleth

from flask import Flask, render_template
from flask import request, jsonify, current_app, json

import logging

data_new_codes = pd.read_csv("./data/NEW_CODES.csv",sep=";")

data_geo = gpd.read_file("data/Departamentos.json")
data_geo = data_geo.drop(columns="id")
data_geo.index=map(lambda p : str(p),data_geo.index)
data_geo.crs = 'EPSG:4326'

data_dem = pd.read_csv("data/DPTO_INFORMATION_SD_VO.csv")

style_function = lambda x: {'fillColor': '#F27F0C', 
                            'color':'#F27F0C', 
                            'fillOpacity': 0.1, 
                            'weight': 0.1}
highlight_function = lambda x: {'fillColor': '#AAFF00', 
                                'color':'#AAFF00', 
                                'fillOpacity': 0.75, 
                                'weight': 0.1}

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
app.logger.addHandler(logging.StreamHandler())

@app.route('/')
def index():
    map1 = dptos_map()
    map2 = sandr_map()
    map3 = provd_map()
    data_dpto=dpto_data_map()

    #dpto_data = data_geo.drop(columns='geometry')
    return render_template('map.html',map1=map1,map2=map2,map3=map3,data_dpto=data_dpto)

@app.route('/dptos_map')
def dptos_map():
    
    dept_map = folium.Map(location=[4.4, -74.55], 
                tiles=None,
                zoom_start=6,
                zoom_control=False)

    dept_map.options['scrollWheelZoom'] = False
    dept_map.options['dragging'] = False

    choro = Choropleth(geo_data=data_geo.geometry.__geo_interface__,
            data=data_geo.STP27_PERS,
            key_on="feature.id", fill_color="RdBu")
    
    #choro.color_scale.width=0

    choro.add_to(dept_map)

    NIL = folium.features.GeoJson(
        data_geo,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['DPTO_CNMBR','STP27_PERS'],
            aliases=['Departamento: ','Población: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
        )
    )

    dept_map.add_child(NIL)
    dept_map.keep_in_front(NIL)

    return dept_map.get_root().render()


sayp_data = data_geo.loc[(data_geo['DPTO_CCDGO']=="88")]
sayp_data = sayp_data.assign(DPTO_CNMBR="SAN ANDRÉS Y PROVIDENCIA")
sayp_data.crs = 'EPSG:4326'

@app.route('/sandr_map')
def sandr_map():   
    sa_map = folium.Map(location=[12.52, -81.72], 
                tiles=None,
                zoom_start=10,
                zoom_control=False)

    sa_map.options['scrollWheelZoom'] = False
    sa_map.options['dragging'] = False

    choro = Choropleth(geo_data=data_geo.geometry.__geo_interface__,
            data=data_geo.STP27_PERS,
            key_on="feature.id", fill_color="RdBu")

    choro.color_scale.width=0
    
    choro.add_to(sa_map)

    NIL = folium.features.GeoJson(
        sayp_data,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['DPTO_CNMBR','STP27_PERS'],  # use fields from the json file
            aliases=['Departamento: ','Población: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
        )
    )

    sa_map.add_child(NIL)
    #sa_map.keep_in_front(NIL)

    sa_map.get_root().html.add_child(folium.Element("""
        <style>
            .folium-legend.leaflet-control {
                display: none !important;
            }
        </style>
    """))

    # folium.LayerControl().add_to(sa_map)
    
    return sa_map.get_root().render()

@app.route('/provd_map')
def provd_map():
    prov_map = folium.Map(location=[13.32, -81.36], 
                tiles=None,
                zoom_start=10,
                zoom_control=False)
                #color_scale = False

    prov_map.options['scrollWheelZoom'] = False
    prov_map.options['dragging'] = False

    choro = Choropleth(geo_data=data_geo.geometry.__geo_interface__,
            data=data_geo.STP27_PERS,
            key_on="feature.id", fill_color="RdBu")
    
    choro.color_scale.width=0

    choro.add_to(prov_map)

    NIL = folium.features.GeoJson(
        sayp_data,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['DPTO_CNMBR','STP27_PERS'],  # use fields from the json file
            aliases=['Departamento: ','Población: '],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
        )
    )

    prov_map.add_child(NIL)
    prov_map.keep_in_front(NIL)

    # Access the color scale and reduce its size
    prov_map.get_root().html.add_child(folium.Element("""
        <style>
            .folium-legend.leaflet-control {
                display: none !important;
            }
        </style>
    """))
    # folium.LayerControl().add_to(sa_map)
    
    return prov_map.get_root().render()

@app.route('/dpto_data_map')
def dpto_data_map():
    data_cod = data_geo.drop(columns='geometry')
    data_cod["DPTO_CCDGO"] = data_cod["DPTO_CCDGO"].astype('int')
    data_cod = pd.merge(data_cod,data_new_codes,on="DPTO_CCDGO")

    data_dem["DPTO_CCDGO"] = data_dem["DPTO_CCDGO"].astype('int')
    data_cod = pd.merge(data_cod,data_dem,on="DPTO_CCDGO")
    data_cod_json = data_cod.to_dict(orient="records")

    return json.dumps({"data_dpto": data_cod_json})

@app.route('/update_choropleth', methods=['POST'])
def update_choropleth():
    selected_option = request.form.get('selected_option')

    data_cod["DPTO_CCDGO"] = data_cod["DPTO_CCDGO"].astype('int')
    data_cod = pd.merge(data_cod,data_new_codes,on="DPTO_CCDGO")

    data_dem["DPTO_CCDGO"] = data_dem["DPTO_CCDGO"].astype('int')
    data_cod = pd.merge(data_cod,data_dem,on="DPTO_CCDGO")

    # Define a function to create the Choropleth based on the selected option
    def create_choropleth(selected_option):
        # Define your choropleth creation logic based on the selected option
        # For simplicity, I'm assuming you have separate code to create different Choropleths
        if selected_option == "poblacion":
            choro = Choropleth(geo_data=data_cod.geometry.__geo_interface__,
                               data=data_cod.Total_x,
                               key_on="feature.id", fill_color="Reds")
        elif selected_option == "total_votos":
            choro = Choropleth(geo_data=data_cod.geometry.__geo_interface__,
                               data=data_cod.Total_votos,  # Update this to match your data
                               key_on="feature.id", fill_color="Blues")
        # Add more cases as needed

        # Return the created Choropleth
        return choro

    # Create the Choropleth based on the selected option
    updated_choro = create_choropleth(selected_option)

    # Get the updated map HTML
    updated_map_html = updated_choro.add_to(folium.Map()).get_root().render()

    return jsonify(updated_map_html=updated_map_html)

if __name__ == '__main__':
    app.run(debug=True)