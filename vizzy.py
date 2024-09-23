import streamlit as st
import plotly.express as px
import pandas as pd
from utils.courtCoordinates import CourtCoordinates
from utils.basketballShot import BasketballShot

st.set_page_config(layout="wide")
st.title("NBA Interactive 3D Shot Visualizer")

schedule_df = pd.read_csv("sample_schedule.csv")
play_by_play_df = pd.read_csv("example.csv")

print(schedule_df)
print(play_by_play_df)
print(play_by_play_df.columns)

# create single selection option
schedule_options = schedule_df[['notes_headline','game_id']].set_index('game_id')['notes_headline'].to_dict()
game_selection = st.sidebar.selectbox('Select Game', schedule_options.keys(), format_func=lambda x:schedule_options[x])

# filter game specific values
game_shots_df = play_by_play_df[(play_by_play_df['game_id'] == game_selection)]
home_color = schedule_df.loc[schedule_df['game_id'] == game_selection]['home_color'].item()
away_color = schedule_df.loc[schedule_df['game_id'] == game_selection]['away_color'].item()
game_text = schedule_options[game_selection]
st.title(game_text)

color_mapping = {
    'home': home_color,
    'away': away_color
}

# draw court lines
court = CourtCoordinates()
court_lines_df = court.get_court_lines()

fig = px.line_3d(
    data_frame=court_lines_df,
    x='x',
    y='y',
    z='z',
    line_group='line_group',
    color='color',
    color_discrete_map={
        'court': '#000000',
        'hoop': '#e47041'
    }
)
fig.update_traces(hovertemplate=None, hoverinfo='skip', showlegend=False)

game_coords_df = pd.DataFrame()
# generate coordinates for shot paths
for index, row in game_shots_df.iterrows():
    scoring_team = ''
    if row['team_id'] == row['home_team_id']:
        scoring_team = 'home'
    else:
        scoring_team = 'away'
    shot = BasketballShot(
        shot_start_x=row['coordinate_x'], 
        shot_start_y=row['coordinate_y'], 
        shot_id=index,
        play_description=row['text'],
        shot_made=row['scoring_play'],
        team=scoring_team)
    shot_df = shot.get_shot_path_coordinates()
    game_coords_df = pd.concat([game_coords_df, shot_df])

print("GAME SHOTS")
print(game_shots_df.columns)
print(game_shots_df)

# draw shot paths
shot_path_fig = px.line_3d(
    data_frame=game_coords_df,
    x='x',
    y='y',
    z='z',
    line_group='line_id',
    # color='team',
    # color_discrete_map=color_mapping,
    custom_data=['description']
)

hovertemplate='Description: %{customdata[0]}'
shot_path_fig.update_traces(opacity=0.55, hovertemplate=hovertemplate, showlegend=False)

# shot start scatter plots
game_coords_start = game_coords_df[game_coords_df['shot_coord_index'] == 0]
shot_start_fig = px.scatter_3d(
    data_frame=game_coords_start,
    x='x',
    y='y',
    z='z',
    custom_data=['description'],
    # color='team',
    # color_discrete_map=color_mapping,
    symbol='shot_made',
    symbol_map={'made': 'circle', 'missed': 'x'}
)

shot_start_fig.update_traces(marker_size=4, hovertemplate=hovertemplate)

# add shot scatter plot to court plot
for i in range(len(shot_start_fig.data)):
    fig.add_trace(shot_start_fig.data[i])

# add shot line plot to court plot
for i in range(len(shot_path_fig.data)):
    fig.add_trace(shot_path_fig.data[i])

# graph styling
fig.update_traces(line=dict(width=5))
fig.update_layout(    
    margin=dict(l=20, r=20, t=20, b=20),
    scene_aspectmode="data",
    height=600,
    scene_camera=dict(
        eye=dict(x=1.3, y=0, z=0.7)
    ),
    scene=dict(
        xaxis=dict(title='', showticklabels=False, showgrid=False),
        yaxis=dict(title='', showticklabels=False, showgrid=False),
        zaxis=dict(title='',  showticklabels=False, showgrid=False, showbackground=True, backgroundcolor='#f7f0e8'),
    ),
    legend=dict(
        yanchor='bottom',
        y=0.05,
        x=0.2,
        xanchor='left',
        orientation='h',
        font=dict(size=15, color='black'),
        bgcolor='white',
        title='',
        itemsizing='constant'
    ),
    legend_traceorder="reversed"
)

st.plotly_chart(fig, use_container_width=True)