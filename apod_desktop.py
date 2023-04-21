""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import date
import re
import apod_api
from image_lib import *
from apod_api import *
import image_lib
import inspect
import argparse
import datetime
import sqlite3
import requests
import hashlib



# Global variables
image_cache_dir = None  # Full path of image cache directory
image_cache_db = None   # Full path of image cache database

def main():
    # DO NOT CHANGE THIS FUNCTION ##
    # Get the APOD date from the command line
    apod_date = get_apod_date()

    # Get the path of the directory in which this script resides
    script_dir = get_script_dir()

    # Initialize the image cache
    init_apod_cache(script_dir)

    # Add the APOD for the specified date to the cache
    apod_id = add_apod_to_cache(apod_date)

    # Get the information for the APOD from the DB
    apod_info = get_apod_info(apod_id)

    # # Set the APOD as the desktop background image
    if apod_id != 0:
        # print(apod_info['file_path'])
        image_lib.set_desktop_background_image(apod_info['file_path'])


def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.


    Returns:
        date: APOD date
    """
    # TODO: Complete function body
    # this portion of code is create a CLI utility
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="Date in YYYY-MM-DD format", nargs='?')
    args = parser.parse_args()
    if args.date is None:
        args.date = str(datetime.date.today())
    else:
        args.date = args.date
    # date-validator function for date validation  Set minimum and maximum date limits
    MIN_DATE = datetime.datetime.strptime('1995-06-16', '%Y-%m-%d').date()
    MAX_DATE = datetime.date.today()
    # {{Date validator function start
    def datevalidator(user_input):
        try:
            # Convert the user input to a datetime object
            date_obj = datetime.datetime.strptime(user_input, '%Y-%m-%d').date()

            # Check if the date is within the allowed range
            if date_obj <= MIN_DATE:
                print("Not before the date of the first APOD")
                print("Script execution aborted")
                exit()
            elif date_obj > MAX_DATE:
                print("Error: APOD date is can not be the future")
                print("Script execution aborted")
                exit()
            else:
                return date_obj
        except ValueError as e:
            if "unconverted data remains" in str(e):
                print("Error: Invalid date; date is out of range for month")
            else:
                print(f"Error: Invalid date format;  Invalid isoformat string:{args.date}")
                print("Script execution aborted")
            exit()
    #}}
    apod_date = datevalidator(args.date)
    return apod_date

def get_script_dir():
    """Determines the path of the directory in which this script resides

    Returns:
        str: Full path of the directory in which this script resides
    """
    ## DO NOT CHANGE THIS FUNCTION ##
    script_path = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
    print(script_path)
    return os.path.dirname(script_path)

def init_apod_cache(parent_dir):
    """Initializes the image cache by:
    - Determining the paths of the image cache directory and database,
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    
    The image cache directory is a subdirectory of the specified parent directory.
    The image cache database is a sqlite database located in the image cache directory.

    Args:
        parent_dir (str): Full path of parent directory    
    """
    # TODO: Determine the path of the image cache directory
    # TODO: Create the image cache directory if it does not already exist
    # TODO: Determine the path of image cache DB
    # TODO: Create the DB if it does not already exist
    # if it does not exist 'image' directory when create images directory
    if parent_dir:
        dir = parent_dir
    else:
        dir = os.getcwd()
    print(f'Image cache directory: {dir}\images')
    if not os.path.exists(f'{os.getcwd()}\images'):
        print("image Cached directory is Created")
        os.mkdir("images")
    else:
        print("Image Cached directory is exists")

    # if it does not exist 'image_cache.db' directory when create this DB file
    db_path = os.path.join(os.getcwd(), 'images', 'image_cache.db')
    print(f'Image cache DB:{db_path}')
    # Connect to database
    if not os.path.exists(f'{db_path}'):
        conn = sqlite3.connect(f'{db_path}')
        print("image Cache DB is Created")
        # Create a new table
        conn.execute(
            '''CREATE TABLE users (
            apod_id INTEGER  PRIMARY KEY AUTOINCREMENT,
            apoddate DATE,title TEXT,
            explanation TEXT,
            image_path TEXT,
            image_hash TEXT)''')
    else:
        print("Image Cached DB is exists")
        conn = sqlite3.connect(f'{db_path}')
    global image_cache_dir
    image_cache_dir = f'{os.getcwd()}\images'
    global image_cache_db
    image_cache_db = db_path
def add_apod_to_cache(apod_date):
    # TODO: Download the APOD information from the NASA API
    apod_info_dict = apod_api.get_apod_info(apod_date)
    # TODO: Download the APOD image
    download_image(apod_info_dict['url'])
    # TODO: Check whether the APOD already exists in the image cache
    id=get_apod_id_from_db(hashlib.sha256(requests.get(apod_info_dict['url']).content).hexdigest())
    if id==0:
        # TODO: Save the APOD file to the image cache directory
        save_image_file(download_image(apod_info_dict['url']),determine_apod_file_path(apod_info_dict['title'],apod_info_dict['url']))
        # TODO: Add the APOD information to the DB
        id=add_apod_to_db(apod_info_dict['title'],apod_info_dict['explanation'],determine_apod_file_path(apod_info_dict['title'],apod_info_dict['url']),hashlib.sha256(requests.get(apod_info_dict['url']).content).hexdigest())
    return id

def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful.  Zero, if unsuccessful       
    """
    # TODO: Complete function body
    conn = sqlite3.connect(f'{image_cache_db}')
    # check image in already in cached or not by image_hash
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE image_hash=?", (sha256,))
    result = c.fetchone()
    if result:
        print(f"APOD image is already in cache DB.")
        id = result[0]
    else:
        print(f"APOD image is not already in cache DB.")
        # Insert some data
        conn.execute("INSERT INTO users (apoddate, title, explanation, image_path, image_hash) VALUES (?, ?, ?, ?, ?)",
                     (date.isoformat(datetime.date.today()), title, explanation, file_path, sha256))
        conn.commit()  # Commit the changes
        conn.close()  # Close the connection
       
        result = c.fetchone()
        id = result[0]
    return id

def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    This function can be used to determine whether a specific image exists in the cache.
    Args:
        image_sha256 (str): SHA-256 hash value of APOD image
    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    # TODO: Complete function body
    conn = sqlite3.connect(f'{image_cache_db}')
    # check image in already in cached or not by image_hash
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE image_hash=?", (image_sha256,))
    result = c.fetchone()
    if result:
        print(f"APOD image is already in cache DB.")
        id = result[0]
    else:
        print(f"APOD image is already does not exists in cache DB.")
        id = 0
    return id

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache.
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    extension = '.jpg'
    ftitle = re.sub(r'[^\w\s]', '', image_title.strip())
    fname = re.sub(r'\s+', '_', ftitle)
    filename = f"{fname}{extension}"
    filepath = os.path.join('images', filename)  # Construct the full path to the image file
    # TODO: Save the APOD file to the image cache directory

    file_path = os.getcwd() + f'\{filepath}'
    if os.path.exists(file_path):
        print(file_path)
    else:
        with open(filepath, 'wb') as f:  # Save the image file to the cache directory
            f.write(requests.get(image_url).content)
            print(file_path)
    # TODO: Complete function body
    return file_path

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB
        
    Returns:
        dict: Dictionary of APOD information
    """
    # TODO: Query DB for image info
    # TODO: Put information into a dictionary
    image_cache_db = os.path.join(os.getcwd(), 'images', 'image_cache.db')
    # print(image_cache_db)
    conn = sqlite3.connect(f'{image_cache_db}')
    # check image in already in cached or not by image_hash
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE apod_id=?", (image_id,))
    result = c.fetchone()
    if result:
        apod_info = {
            # # 'title': ,
            # # 'explanation': ,
            # 'file_path': 'TBD',
            'date' : result[1],
            'title' : result[2],
            'explanation' : result[3],
            'file_path' : result[4],
            'image_hash' : result[5]
        }
    return apod_info

def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache
    Returns:
        list: Titles of all images in the cache
    """
    # TODO: Complete
    #  function body
    # NOTE: This function is only needed to support the APOD viewer GUI
    return

if __name__ == '__main__':
    main()