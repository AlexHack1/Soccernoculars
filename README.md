# Soccernoculars
This program scrapes FBREF with BS4 in Python to create a dataset of players for scouting and data analysis.
The script lets you select a year, league, and position and it will put together a generous set of stats based on position from which you can conduct further data analysis.
The stats 
It works with 10 major leagues, going back at least as far as 2017-2018.

*** picture of spreadsheet

## 1) Install Python Packages
Open your windows command window and type the following to pip install the necessary packages to run the script. Do one at a time.

```
pip install requests
pip install beautifulsoup4
pip install pandas
pip install numpy
pip intall lmxl
pip install html5lib
```
Pip should be installed with python, but if it isn't, follow instructions at [pip.pypa.io](https://pip.pypa.io/en/stable/installation/) to install.

## 2) Create a CSV File
Create a csv file to save the dataset to. Copy the file path for the next step

** image 

## 3) Run the Script
Run the script in the command window or an IDE and follow the prompts. Make sure the csv file that you created is not open while the script is running

** image

If you are not looking at data from the past 365 days, the script will collect player data from all of the competitions in the year that you selected. For the example shown above, Bukayo Saka competed in the Premier League AND the Europa League in the 2020-2021 season. The stats from these seasons will be weighted by their minutes and added to form one vector for the player in the final spreadsheet.

After following the prompts, player names should start appearing in the command window every few seconds. Multiple seconds elapse between player names because FBREF's webscraping policy is that requests cannot be made more frequently than every four seconds. DO NOT change this duration in the script.

Player data will be read in to the csv file one team at a time since the script can take quite a while to get through all of the teams in a league. If you would like to create multi-league datasets, you can run the script with the same file path as new players will be appended to the file and not overwritten. 
After all players have been added, you will be prompted to transpose the dataset.

That's it!
