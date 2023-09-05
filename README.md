# RecorderScraper

## Installing Python
1) Download and install Python<br/>
	32-bit Windows:<br/>
	https://www.python.org/ftp/python/3.11.0/python-3.11.0.exe<br/>
	
	64-bit Windows:<br/>
	https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe<br/>
	
	**Make sure to check the "Add python.exe to PATH" at the bottom of the installation window.**<br/>
	![image](https://drive.google.com/uc?export=view&id=1CqbfL0qezreCyh4GvQTOmwwILhPlwWnO)

## Installing the requirements
Open a command prompt and navigate to the scraper's directory.<br/> 
The easiest way is to open the scraper's folder and type cmd in the address bar.
![image](https://drive.google.com/uc?export=view&id=1MdOWMetTcP7cNo0YC9ZyLTFTU9fdEav1)
<br/>
Type the following command, you have to do this only once:<br/>
```
pip install -r requirements.txt
```

## Starting the scraper
You can start the scraper by typing the following command:<br/>
```
py main.py
```

## Input

I have pre-scraped the data from 01/01/2000 to 09/01/2023 <br/>

By default, the script will use the first date entered - in this case 09/01/2000 - 09/05/2023.<br/>
<br/>
You can either enter dates individually for each keyword, <br/>
or enter one start_date and one end_date, and it will be used for all keywords that don't have a date set.
<br/>
You have to input at least one start_date and end_date
<br/>
<br/>
**The scraper will "remember" which keywords and date ranges are scraped, so it won't repeat them, once they are completed**

## Output
The scraper will automatically create output.xlsx after it completes the scraping.<br/>
You can stop the scraper prematurely by pressing CTRL+C twice.<br/>
You can also create the output file by running the following command:<br/>
```
py export.py
```


## Multithreading

The scraper will run all counties in parallel. <br/>
However, in order to reduce the server load, each website will receive only one simultaneous request with 1 second cooldown.


