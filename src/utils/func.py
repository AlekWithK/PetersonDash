import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math
from utils.const import *

def importData(path: str) -> pd.DataFrame:
    """Import app dataset from either parquet, csv, or xlsx"""
    if path.endswith('.parquet'):
        return pd.read_parquet(path)

    elif path.endswith('.csv'):
        return pd.read_csv(path)
    
    elif path.endswith('.xlsx'):
        return pd.read_excel(path)
    
    else:
        raise Exception("FileError: No suitable dataset found")
    

def createSpatialVis(dfg, stations, refline, param, mapTile, station_t, ref_t, coerce_t) -> go.Figure:

    fig = px.scatter_mapbox(dfg, lat='lat', lon='lon', hover_name=dfg.datetime.dt.date, hover_data={param, 'file', 'dataset'}, color=param,
                            zoom=3, color_continuous_scale=px.colors.sequential.Viridis, opacity=0.75)
    
    fig = fig.update_layout(
        mapbox_style=mapTile,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox={'center': {'lat': 37.82, 'lon': -121.75}, 'zoom': 9},
        autosize=True,
        paper_bgcolor='#999',
        coloraxis=dict(
            colorbar=dict(thickness=20, len=0.60, x=0.01, y=0.32,
                title=f'{PARAM_NAME_UNIT_DICT[param][0]} ({PARAM_NAME_UNIT_DICT[param][1]})',
                outlinecolor='black', outlinewidth=1.5, title_side='bottom')),
        font=dict(size=14, weight='bold', family='Segoe UI'))
    
    # Update
    if mapTile == 'carto-darkmatter':
        fig = fig.update_layout(
            font=dict(size=14, weight='bold', color='lightgrey'))

    # Toggle refline
    if ref_t == [0, 1]:
        fig3 = px.scatter_mapbox(refline, lat='lat', lon='lon', hover_name=refline.name, color_discrete_sequence=['fuchsia'])
        fig3 = fig3.update_traces(marker={'size': 4})
        fig = fig.add_trace(fig3.data[0])

        # Toggle stations
    if station_t == [0, 1]:
        fig2 = px.scatter_mapbox(stations, lat='lat', lon='lon', hover_name=stations.Station_Number, color_discrete_sequence=['fuchsia'])
        fig2 = fig2.update_traces(marker={'size': 15})
        fig = fig.add_trace(fig2.data[0])

    return fig

def createMetadataTables(dfmd: pd.DataFrame) -> pd.DataFrame:
    keepcol = ['datetime', 'chlor', 'salinity', 'turbidity', 'depth', 'water_temp']
    dfmd = dfmd[keepcol]
    dfmd = dfmd.describe().transpose()[['count', 'min', 'max', '50%']].reset_index(names='Parameter')
    dfmd.columns = [col.title() for col in dfmd.columns]
    dfmd['Parameter'] = dfmd['Parameter'].replace('_', ' ').str.title()
    dfmd = dfmd.round(3)
    dfmd.Count = dfmd.Count.astype(int)
    dfmd.at[0, 'Min'] = dfmd.at[0, 'Min'].date()
    dfmd.at[0, 'Max'] = dfmd.at[0, 'Max'].date()
    dfmd.at[0, '50%'] = dfmd.at[0, '50%'].date()
    return dfmd