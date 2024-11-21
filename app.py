import pandas as pd
import numpy as np
import streamlit as st
import json
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns
import plotly.express as px
from vega_datasets import data


st.title('Chess: An Analytical Study')

st.header("Scope of Study")

st.write('The objective of this work is to perform a limited review of key game elements using sample data to observe how these elements interact.')

st.write('Key game elements include starting as white or black, the number of turns in matches, the first move, the opening sequence and the game timing to mention a few.')

st.write('The data used is open source but with limited meta data. A deep dive into the origin of the data suggests it was sourced from Chess.com and comprises match data of 20,058 games from between 2016 and 2017.')

# Loading chess data
df_chess = pd.read_csv('https://raw.githubusercontent.com/tjayolagz/instructionaldatasets/refs/heads/main/data/chess_games.csv')

# Printing descriptive text
st.subheader('1. White versus Black')

st.write('1.1 As mentioned in the opening of this review, the white pieces start each match and as such there is an assumption that this gives an advantage to the starting player. From the barchart below, we can see that a higher number of wins across different game outcomes have gone to the starting player. However, the ratio of wins by the white pieces is approximately 4.7% greater than wins by black pieces. This suggests that starting first does play a role, albeit not a very significant one, in determining a victory.')

# Plotting chart to show White versus Black starting players
# Filtering chess data to remove draws from both 'victory_status' and 'winner'
df_chess_filtered = df_chess[
    ~df_chess['victory_status'].isin(['Draw']) & 
    ~df_chess['winner'].isin(['Draw'])
]

# Creating a crosstab to map count the different game outcomes
df_vs_bw = pd.crosstab(
    index=df_chess_filtered['victory_status'], 
    columns=df_chess_filtered['winner'], 
    values=df_chess_filtered['victory_status'], 
    aggfunc='count'
).fillna(0)

# Resetting index and melting the eventual dataframe
df_vs_bw = df_vs_bw.reset_index()
df_vs_bw_melted = df_vs_bw.melt(id_vars='victory_status', var_name='winner', value_name='count')

# Checking melted dataframe before plotting
if not df_vs_bw_melted.empty:
    chart = alt.Chart(df_vs_bw_melted).mark_bar(size=70).encode(
        x=alt.X("victory_status", title="Game Outcome"),
        xOffset='winner',
        y=alt.Y("count", title="Frequency"),
        color=alt.Color("winner",title="Winner"), 
    ).configure_axisX(
        labelAngle=0 
    )
    # Displaying chart
    st.write("Fig. 1 Frequency of wins between White and Black pieces")
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No data available to plot.")

# Printing descriptive text
st.subheader("2. Total Number of Turns and Moves in Opening Sequence")

st.write("2.1 The scatter plots below show the total number of turns plotted against the number of moves in the opening sequence (also referred to as 'opening move') of each of the games played. Fig 2.1 does not show a clear relationship, however when the axes are switched (see Fig 2.2), it becomes clear that regardless of the number of moves in the opening sequence of a match, the total turns taken in any given match can fall within a wide range, generally reaching an approximate maximum between 200 and 260 turns.")

st.write('2.2 Another interesting visual observation is that a larger proportion of games with total turns between 0 and 150 appear to end by one player resigning or the game running out of time.')

#Plotting scatterplot for number of moves in opening sequence vs total turns taken
# Creating multiselect interactivity for the scatterplots
selected_category = st.multiselect(
    "Select Match Outcome", 
    options=['All', 'Mate', 'Draw', 'Resign', 'Out of Time'], 
    default=['All'], 
    label_visibility="visible"
)

# Filtering data based on selected categories
if 'All' in selected_category or not selected_category:
    filtered_data = df_chess
else:
    filtered_data = df_chess[df_chess['victory_status'].isin(selected_category)]

# Plotting scatter plot of number of moves in opening sequence vs total turns
st.write("Fig 2.1 Scatter Plot: Moves in Opening Sequence vs Total Turns")
st.scatter_chart(data=filtered_data, x= 'turns', y = 'opening_moves', x_label = 'Total Turns', y_label = 'No. of moves in Opening Sequence', color = 'victory_status')

# Plotting scatter plot of number of total turns vs number of moves in opening sequence
st.write("Fig 2.2 Scatter Plot: Total Turns vs Moves in Opening Sequence")
st.scatter_chart(data=filtered_data, x= 'opening_moves', y = 'turns', x_label = 'No. of moves in Opening Sequence', y_label = 'Total Turns', color = 'victory_status')

# Printing descriptive text
st.write('2.3 In a bid to further investigate the observations determined above, box plots detailing the distributions of total turns as well as the length of the opening moves as categorised by match outcome are shown below (hover over the chart for details)')

st.write('2.4 Contrary to 1.1 above, we can see that most of the lengthiest games involve total number of turns between 100 and 150. Games with more turns appear to likely end as a draw. Also, 1.2 is not accurate it is clear that games running to a maximum total of 150 turns can possible end in any outcome with resignation-ending games appearing to be less likely after 125 turns in total.')

# Creating box plots to show range of variation in opening moves and number of turns for each status category
# Creating and displaying first box plot
fig1 = px.box(df_chess, x="victory_status", y='turns', title='Fig 2.3 Box plots showing the distribution of game outcomes as a function of total turns',labels={"victory_status":"Game Outcome","turns":"Total turns"})
st.plotly_chart(fig1)

# Printing descriptive text
st.write('2.5 Also, the boxplot shows that most opening moves max out at 10 turns and do not appear to significantly affect the eventual outcome of the game.')

# Creating and displaying second box plot
fig2 = px.box(df_chess, x="victory_status", y='opening_moves',title='Fig 2.4 Box plots showing the distribution of game outcomes as a function of number of moves in opening sequence',labels={"victory_status":"Game Outcome","opening_moves":"No. of moves in Opening Sequence"})
st.plotly_chart(fig2)

# Printing descriptive text
st.write("2.6 The barchart below shows the first moves of each of the games in the study. It is clear that the overwhelming favorite is move 'e4' which involves the movement of a pawn to square e4. This along with movement of pawns to squares d4, c4 and b3 make up the majority of first moves.")

# Printing descriptive text
st.subheader("3. First Move")

st.write("3.1 The barchart below shows the first moves of each of the games in the study. It is clear that the overwhelming favorite is move 'e4' which involves the movement of a pawn to square e4. This along with movement of pawns to squares d4, c4 and b3 make up the majority of first moves.")

# Plotting barchart showing most made first move
# Extracting the first two elements which make the first move of the game
df_chess['first_two_elements'] = 0
df_chess['first_two_elements'] = df_chess['moves'].str[:2]

df_chess_lite=df_chess.drop(columns=['rated','victory_status','winner','opening_moves','time_increment','game_id','white_id','black_id','black_rating','white_rating','opening_code','opening_fullname','opening_response','opening_shortname','opening_variation'])

pivot_table_result = df_chess_lite.pivot_table(index='first_two_elements', aggfunc='count')

#Plotting and displaying bar chart 
st.write("Fig 3.1 Opening Move vs Total Turns")
st.bar_chart(data=pivot_table_result, y='turns', x=None, use_container_width=False, horizontal=True, x_label ='Frequency', y_label='First Move')

# Printing descriptive text
st.subheader('4. Rankings and Ratings')

st.write('4.1 Chess matches are either rated or unrated with rated matches falling into either competitive or casual. From the pie chart, we can see that a substantial proportion of games under review were unrated. This could be indicative of the fact that most of these games were casual given the online source of the data.')

# Plotting piechart showing proportion of rated games
# Dropping redundant columns and renaming column entries
df_chess_rated=df_chess.drop(columns=['first_two_elements','victory_status','winner','opening_moves','time_increment','game_id','white_id','black_id','black_rating','white_rating','opening_code','opening_fullname','opening_response','opening_shortname','opening_variation'])
df_chess_rated.info()

# Updating 'rated' column values
df_chess_rated.loc[df_chess_rated['rated'] == 'TRUE', 'rated'] = 'Rated'
df_chess_rated.loc[df_chess_rated['rated'] == 'FALSE', 'rated'] = 'Unrated'

# Creating pivot table
pivot_table_result2 = df_chess_rated.pivot_table(index='rated', aggfunc='count').reset_index()
pivot_table_result2.tail()

# Plotting and displaying the pie chart
fig1 = px.pie(pivot_table_result2, values='moves',names=['Rated','Unrated'],title='Fig 4.1 Proportion of Rated Games Played')
st.plotly_chart(fig1)

# Printing descriptive text
st.subheader('5. Game Timing')
st.write("5.1 There is a wide range of time controls with the shortest observed as '0+12' to much longer games with '180+180'. The most applied time control is the '10+0' which appears to to result in resignation game outcomes. Note that these timings (denoted in the form 'x+y') are defined by the starting time ('x') in seconds and time increments ('y') which is time added after each successive move. ")

# Loading ranking file
df_ranking = pd.read_csv('https://raw.githubusercontent.com/tjayolagz/Northeastern/refs/heads/main/time_increment_ranking.csv')
df_ranking.head()

# Merging data with ranking on the 'time_increment' column
df_chess = df_chess.merge(df_ranking, on='time_increment', how='left')

# Drop unnecessary columns
df_chess_time = df_chess.drop(columns=[
    'first_two_elements', 'turns', 'opening_moves', 'game_id', 'rated', 'moves',
    'white_id', 'black_id', 'black_rating', 'white_rating', 'opening_code',
    'opening_fullname', 'opening_response', 'opening_shortname', 'opening_variation'
])

# Creating crosstab to combine required data
df_timerankx = pd.crosstab(
    index=df_chess_time['time_rank_x'], 
    columns=df_chess_time['victory_status']
).fillna(0)

# Resetting index and merging with time_increment
df_timerankx = df_timerankx.reset_index()
df_timerankx = df_timerankx.merge(
    df_chess_time[['time_rank_x', 'time_increment']].drop_duplicates(),
    on='time_rank_x',
    how='left'
)

# Melting the DataFrame
df_timerankx_melted = df_timerankx.melt(
    id_vars=['time_rank_x', 'time_increment'], 
    var_name='victory_status', 
    value_name='count'
)

# Mapping game outcomes to colour code
victory_status_categories = df_timerankx_melted['victory_status'].unique()
color_map = {
    category: color for category, color in zip(
        victory_status_categories, 
        px.colors.qualitative.Set1[:len(victory_status_categories)]
    )
}

# Creating selectbox for filtering game outcomes
selected_category = st.selectbox(  
    "Select Game Outcome", 
    options=['All'] + victory_status_categories.tolist(),
    label_visibility="visible"
)

# Filtering data based on selected category
if selected_category == 'All':
    filtered_data = df_timerankx_melted
else:
    filtered_data = df_timerankx_melted[df_timerankx_melted['victory_status'] == selected_category]

# Plotting and displaying the filtered data
import plotly.express as px
fig1 = px.line(
    filtered_data, 
    x='time_increment', 
    y='count', 
    color='victory_status',
    title="Game Outcome vs Time Increment",
    labels={"victory_status":"Game Outcome","time_increment":"Game Timing","count":"Frequency"},
    color_discrete_map=color_map
)
st.plotly_chart(fig1)


# Printing descriptive text
st.subheader('6. Opening Sequence')
st.write('6.1 In the dataset analysed, a total of 128 different opening sequences (or moves) and their different variants were made. From the chart below, we are unable to identify a particular opening move or sequence which could be attributed to a particular game outcome. The exception to this are opening sequences that were employed in few games.')


# Grouping by 'opening_shortname' and aggregating game outcomes
openings_agg = df_chess.groupby('opening_shortname').agg(
    mates=('victory_status', lambda x: (x == 'Mate').sum()),
    resigns=('victory_status', lambda x: (x == 'Resign').sum()),
    draws=('victory_status', lambda x: (x == 'Draw').sum()),
    out_of_time=('victory_status', lambda x: (x == 'Out of Time').sum())
).reset_index()
openings_agg.sort_values(by='mates', ascending=False).head()

# Recreateing the opening sequences data
opening_outcomes = df_chess.groupby(['opening_shortname', 'victory_status']).size().unstack(fill_value=0)
opening_outcomes.rename(columns={
    'Mate': 'Mate',
    'Resign': 'Resign',
    'Draw': 'Draw',
    'Out of Time': 'Out of Time'
}, inplace=True)
opening_outcomes.reset_index(inplace=True)

# Normalizing the data to calculate proportions for each outcome
proportion_data = opening_outcomes.set_index('opening_shortname')
proportion_data = proportion_data.div(proportion_data.sum(axis=1), axis=0)

# Creating radio button to filter game outcomes
selected_category = st.radio(
    "Select Game Outcome", 
    options=['All'] + list(proportion_data.columns),
    index=0,
    horizontal=False,
    label_visibility="visible"
)

# Filtering data based on selected category
if selected_category == 'All':
    filtered_data = proportion_data
else:
    filtered_data = proportion_data[[selected_category]]  

# Displaying a component bar chart
st.write('Fig 6.1 Component Chart showing Opening Sequences and their proportion of use in games')
st.bar_chart(filtered_data)

# Printing descriptive text
st.subheader('7. Player Stats')
st.write("7.1 The dataset comprised of game data for more than 15,000 players. Using an average of each player's rankings (ie white and black rankings), an overall ranking has been established in the table below. The top 10 ranked players from the dataset are shown below.")

# Manipulating data to aggregate data required for player statistics table
# Combining white and black players into a single dataset
players_white = df_chess[['white_id', 'white_rating', 'time_increment', 'victory_status', 'rated', 'opening_shortname']]
players_white.rename(columns={
    'white_id': 'player_id',
    'white_rating': 'rating',
}, inplace=True)
players_white['color'] = 'white'

players_black = df_chess[['black_id', 'black_rating', 'time_increment', 'victory_status', 'rated', 'opening_shortname']]
players_black.rename(columns={
    'black_id': 'player_id',
    'black_rating': 'rating',
}, inplace=True)
players_black['color'] = 'black'

# Combining datasets
players = pd.concat([players_white, players_black], ignore_index=True)

# Computing the different player metrics for each player
player_summary = players.groupby('player_id').agg(
    games_played=('player_id', 'size'),
    checkmates=('victory_status', lambda x: (x == 'Mate').sum()),
    resignations=('victory_status', lambda x: (x == 'Resign').sum()),
    timeouts=('victory_status', lambda x: (x == 'Out of Time').sum()),
    most_played_time_increment=('time_increment', lambda x: x.mode()[0] if not x.mode().empty else None),
    most_common_opening_move=('opening_shortname', lambda x: x.mode()[0] if not x.mode().empty else None),
    highest_rating=('rating', 'max'),
    highest_avg_rating=('rating', lambda x: (x[x.idxmax()] + x[x.idxmin()]) / 2 if len(x) > 1 else x.max()),
    rated_games=('rated', lambda x: x.sum()),
    unrated_games=('rated', lambda x: (~x).sum())
).reset_index()

# Ranking players by revised measure
player_summary['rank_metric'] = player_summary[['highest_rating', 'highest_avg_rating']].max(axis=1)
player_summary.sort_values('rank_metric', ascending=False, inplace=True)
player_summary.reset_index(drop=True, inplace=True)

# Displaying the top 10 players in the resulting table
st.write('Table 1 Chess Data Player Rankings - Top 10 Players')
st.table(player_summary[:11])










