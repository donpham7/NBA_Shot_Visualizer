# NBA_Shot_Visualizer
Link to blog post: https://www.phdata.io/blog/how-to-create-3d-basketball-shot-charts-with-streamlit-and-snowflake/
Link to GitHub code: https://github.com/LwrncLiu/march_madness/blob/main/main.py

Might need to install Git LFS (Large File Storage) - Used for the shot data as it is above 100 MB
  * https://git-lfs.com/

unzip NBA_Shot_Location.zip for csv file of shot data.

exp.py is the python file to run
streamlit run exp.py to run

Things to fix and Possible fixes:
  * Long load times
    * Seperating the CSV's based on names (ie. CSV1 for A-C, CSV2 for D-F, etc.)
  * Some shot makes not showing up, looks like made shots under the basket (x=25, y=0)
    * No solution
