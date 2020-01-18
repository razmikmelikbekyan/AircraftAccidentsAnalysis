# AircraftAccidentsAnalysis
The analysis of aircraft accidents since 1900.

## Scrapping database

The data is scrapped from "https://aviation-safety.net/database/" . 
For scrapping scrapy package is used. To run scrapping you should use 
`accidents_extraction/scrapping_app.py` script. It provides 2 possible ways of
 storing data: in `json` file or in `MySQL` database. 
 
 * For storing in `json` file you should provide the output json file path.
 
 * For storing in `MySQL` database first you should install it then provide the 
 config file in json format for the database. In config file you should specify the following
  items: `user, password, database`. 
  
For more details please see script help.