from pandasql import sqldf
import pandas as pd
import streamlit as st
import plotly.express as px
from utils.courtCoordinates import CourtCoordinates
from utils.basketballShot import BasketballShot

# Global Variables


# Helper Functions
def saveShots():
    st.session_state["runShots"] = False


if __name__ == "__main__":
    # Data and Page Setup
    pysqldf = lambda q: sqldf(q, globals())
    if "setup" not in st.session_state:
        nbaData = pd.read_csv("NBA_Shot_Locations.csv")
        colorData = pd.read_csv("color.csv")
        print("Reading CSVs")
        st.session_state["setup"] = True
        st.session_state["nbaData"] = nbaData
        st.session_state["colorData"] = colorData
    else:
        nbaData = st.session_state["nbaData"]
        colorData = st.session_state["colorData"]

    st.set_page_config(layout="wide")
    st.title("NBA Interactive 3D Shot Visualizer")

    # Query Player Names
    nameQuery = """
    SELECT DISTINCT player_name
    FROM nbaData
    ORDER BY player_name
    """

    # Query and Save Player Names in session
    if "playerNames" not in st.session_state:
        playerNames = pysqldf(nameQuery)
        st.session_state["playerNames"] = playerNames
        print("Querying Names")
    else:
        playerNames = st.session_state["playerNames"]

    # Create selectbox for player selections
    playerSelection = st.sidebar.selectbox(
        "Select Player",
        playerNames["player_name"],
        # format_func=lambda x: playerNames[x],
    )

    playerSelection2 = st.sidebar.selectbox(
        "Select Player 2",
        playerNames["player_name"],
        # format_func=lambda x: playerNames[x],
    )

    # If player 1 is different, then rerun gameStartDate query
    if "selectedPlayer1" not in st.session_state:
        st.session_state["selectedPlayer1"] = playerSelection
    elif st.session_state["selectedPlayer1"] != playerSelection:
        st.session_state["selectedPlayer1"] = playerSelection
        del st.session_state["gameStartDate"]
        del st.session_state["color1"]
        # May delete gameEndDate

    if "selectedPlayer2" not in st.session_state:
        st.session_state["selectedPlayer2"] = playerSelection2
    elif st.session_state["selectedPlayer2"] != playerSelection2:
        st.session_state["selectedPlayer2"] = playerSelection2
        del st.session_state["color1"]

    if "runShots" not in st.session_state:
        st.session_state["runShots"] = True
    # Query team name
    if "color1" not in st.session_state:
        teamQuery1 = f"""
        SELECT DISTINCT team_name
        FROM nbaData
        WHERE player_name = "{playerSelection}"
        """
        colorDf1 = pysqldf(teamQuery1)
        print("Querying team name")
        teamName1 = colorDf1["team_name"][0]

        # Query team color
        colorQuery1 = f"""
        SELECT color
        FROM colorData
        WHERE team_name = "{teamName1}"
        """
        colorDf1 = pysqldf(colorQuery1)
        print("Querying team color")
        color1 = colorDf1["color"][0]

        # Query team2 name
        teamQuery2 = f"""
        SELECT DISTINCT team_name
        FROM nbaData
        WHERE player_name = "{playerSelection2}"
        """
        colorDf2 = pysqldf(teamQuery2)
        print("Querying team name")
        teamName2 = colorDf2["team_name"][0]

        # Query team2 color
        colorQuery2 = f"""
        SELECT color
        FROM colorData
        WHERE team_name = "{teamName2}"
        """
        colorDf2 = pysqldf(colorQuery2)
        print("Querying team color")
        color2 = colorDf2["color"][0]
        st.session_state["color1"] = color1
        st.session_state["color2"] = color2
    else:
        color1 = st.session_state["color1"]
        color2 = st.session_state["color2"]

    # Query game all dates for playerSelection
    startDateQuery = f"""
    SELECT DISTINCT parsed_game_date
    FROM nbaData
    WHERE player_name = "{playerSelection}"
    ORDER BY parsed_game_date
    """

    # Query and save gameStartDate
    if "gameStartDate" not in st.session_state:
        gameStartDate = pysqldf(startDateQuery)
        st.session_state["gameStartDate"] = gameStartDate
        print("Querying Dates")
    else:
        gameStartDate = st.session_state["gameStartDate"]
    
    # Create Start Date Selectbox
    gameStartSelection = st.sidebar.selectbox(
        "Select Start Date",
        options=gameStartDate["parsed_game_date"],
        index=0,
        placeholder="Select Game Date Start",
        # format_func=lambda x: playerNames[x],
    )

    # if selected start game changes delete end date (rerun end date)
    if "selectedStartDate" not in st.session_state:
        st.session_state["selectedStartDate"] = gameStartSelection
    elif st.session_state["selectedStartDate"] != gameStartSelection:
        del st.session_state["gameEndDate"]

    # Query dates later than start date
    endDatesQuery = f"""
    SELECT parsed_game_date
    FROM gameStartDate
    WHERE parsed_game_date >= '{gameStartSelection}'
    """

    # Query and save game end dates
    if "gameEndDate" not in st.session_state:
        gameEndDate = pysqldf(endDatesQuery)
        st.session_state["gameEndDate"] = gameEndDate
        print("Querying Dates 2")
    else:
        gameEndDate = st.session_state["gameEndDate"]

    # Create game end date selectbox
    gameEndSelection = st.sidebar.selectbox(
        "Select End Date",
        options=gameEndDate["parsed_game_date"],
        index=0,
        placeholder="Select Game Date Start",
        # format_func=lambda x: playerNames[x],
    )

    print("runShots in runtime: ", st.session_state["runShots"])
    if st.session_state["runShots"]:
        playerShotsQuery1 = f"""
        SELECT *
        FROM nbaData
        WHERE player_name = "{playerSelection}" AND parsed_game_date >= '{gameStartSelection}' AND parsed_game_date <= '{gameEndSelection}'
        """
        game_shots_df = pysqldf(playerShotsQuery1)
        print("Querying Shots")

        playerShotsQuery2 = f"""
        SELECT *
        FROM nbaData
        WHERE player_name = "{playerSelection2}" AND parsed_game_date >= '{gameStartSelection}' AND parsed_game_date <= '{gameEndSelection}'
        """
        game_shots_df2 = pysqldf(playerShotsQuery2)
        print("Querying Shots 2")

        st.session_state["playerShots1"] = game_shots_df
        st.session_state["playerShots2"] = game_shots_df2
    else:
        game_shots_df = st.session_state["playerShots1"]
        game_shots_df2 = st.session_state["playerShots2"]
        st.session_state["runShots"] = True
        
    # import streamlit as st
    # 
    # @st.cache_data(show_spinner=False)
    # def append_list(num_iterations):
    #     with st.spinner('This might take awhile...'):
    #         mylist = []
    #         with st.empty():
    #             for i in range(num_iterations):
    #                 st.write(f"Iteration number is {i}")
    #                 mylist.append(i)
    #     return mylist

    # output = append_list(1)
    # selection = st.selectbox('Make a selection', ['Good','Bad'])
    # if selection == 'Good':
    #     st.write('You selected Good')
    # else:
    #     st.write('You selected Bad')

    showShotArcs = st.sidebar.checkbox("Show shot arcs", on_change=saveShots, args=None)

    # draw court lines
    court = CourtCoordinates()
    court_lines_df = court.get_court_lines()

    fig = px.line_3d(
        data_frame=court_lines_df,
        x="x",
        y="y",
        z="z",
        line_group="line_group",
        color="color",
        color_discrete_map={"court": "#000000", "hoop": "#e47041"},
    )
    fig.update_traces(hovertemplate=None, hoverinfo="skip", showlegend=False)

    game_coords_df = pd.DataFrame()
    game_coords_df2 = pd.DataFrame()
    # generate coordinates for shot paths
    for index, row in game_shots_df.iterrows():
        scoring_team = "away"
        shot = BasketballShot(
            shot_start_x=row["norm_x_coor"],
            shot_start_y=row["norm_y_coor"],
            shot_id=index,
            play_description=row["text"],
            shot_made=row["shot_made_flag"],
            team=scoring_team,
        )
        shot_df = shot.get_shot_path_coordinates()
        game_coords_df = pd.concat([game_coords_df, shot_df])

    for index, row in game_shots_df2.iterrows():
        scoring_team = "home"
        shot = BasketballShot(
            shot_start_x=row["norm_x_coor"],
            shot_start_y=row["norm_y_coor"],
            shot_id=index,
            play_description=row["text"],
            shot_made=row["shot_made_flag"],
            team=scoring_team,
        )
        shot_df = shot.get_shot_path_coordinates()
        game_coords_df2 = pd.concat([game_coords_df2, shot_df])

    # print("GAME SHOTS")
    # print(game_shots_df.columns)
    # print(game_shots_df)

    # draw shot paths
    hovertemplate = "Description: %{customdata[0]}"
    if showShotArcs:
        shot_path_fig = px.line_3d(
            data_frame=game_coords_df,
            x="x",
            y="y",
            z="z",
            line_group="line_id",
            color=[color1] * len(game_coords_df),
            color_discrete_map="identity",
            custom_data=["description"],
        )

        # draw shot paths 2
        shot_path_fig2 = px.line_3d(
            data_frame=game_coords_df2,
            x="x",
            y="y",
            z="z",
            line_group="line_id",
            color=[color2] * len(game_coords_df2),
            color_discrete_map="identity",
            custom_data=["description"],
        )

        shot_path_fig.update_traces(
            opacity=0.55, hovertemplate=hovertemplate, showlegend=False
        )
        shot_path_fig2.update_traces(
            opacity=0.55, hovertemplate=hovertemplate, showlegend=False
        )

    # shot start scatter plots
    game_coords_start = game_coords_df[game_coords_df["shot_coord_index"] == 0]
    shot_start_fig = px.scatter_3d(
        data_frame=game_coords_start,
        x="x",
        y="y",
        z="z",
        custom_data=["description"],
        color=[color1] * len(game_coords_start),
        color_discrete_map="identity",
        symbol="shot_made",
        symbol_map={"made": "circle", "missed": "x"},
    )

    # shot start scatter plots
    game_coords_start2 = game_coords_df2[game_coords_df2["shot_coord_index"] == 0]
    shot_start_fig2 = px.scatter_3d(
        data_frame=game_coords_start2,
        x="x",
        y="y",
        z="z",
        custom_data=["description"],
        color=[color2] * len(game_coords_start2),
        color_discrete_map="identity",
        symbol="shot_made",
        symbol_map={"made": "circle", "missed": "x"},
    )

    shot_start_fig.update_traces(marker_size=4, hovertemplate=hovertemplate)
    shot_start_fig2.update_traces(marker_size=4, hovertemplate=hovertemplate)

    # add shot scatter plot to court plot
    for i in range(len(shot_start_fig.data)):
        fig.add_trace(shot_start_fig.data[i])

    # add shot scatter plot to court plot
    for i in range(len(shot_start_fig2.data)):
        fig.add_trace(shot_start_fig2.data[i])

    if showShotArcs:
        # add shot line plot to court plot
        for i in range(len(shot_path_fig.data)):
            fig.add_trace(shot_path_fig.data[i])

        # add shot line plot to court plot
        for i in range(len(shot_path_fig2.data)):
            fig.add_trace(shot_path_fig2.data[i])

    # graph styling
    fig.update_traces(line=dict(width=5))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        scene_aspectmode="data",
        height=600,
        scene_camera=dict(eye=dict(x=1.3, y=0, z=0.7)),
        scene=dict(
            xaxis=dict(title="", showticklabels=False, showgrid=False),
            yaxis=dict(title="", showticklabels=False, showgrid=False),
            zaxis=dict(
                title="",
                showticklabels=False,
                showgrid=False,
                showbackground=True,
                backgroundcolor="#f7f0e8",
            ),
        ),
        legend=dict(
            yanchor="bottom",
            y=0.05,
            x=0.2,
            xanchor="left",
            orientation="h",
            font=dict(size=15, color="black"),
            bgcolor="white",
            title="",
            itemsizing="constant",
        ),
        legend_traceorder="reversed",
    )

    st.plotly_chart(fig, use_container_width=True)
