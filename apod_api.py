'''
Library for interacting with NASA's Astronomy Picture of the Day API.
'''
import requests
from colorama import Fore,Style
import json,os
from pytube import YouTube

def main():
    # TODO: Add code to test the functions in this module
    return

def get_apod_info(apod_date):
    """Gets information from the NASA API for the Astronomy
    Picture of the Day (APOD) from a specified date.

    Args:
        apod_date (str): APOD date in string format YYYY-MM-DD

    Returns:
        dict: Dictionary of APOD info, if successful. None if unsuccessful
    """
    # Please enter your API key
    api_key = 'ERSkm4RYVbPD7gBeMrZpWN1NTb71DFCup69M3vh1'

    # Getting data from NASA APOD API by given date
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}&date={apod_date}"

    try:
        r = requests.get(url)
        print(f'APOD date: {apod_date}')
        print(f'Getting {apod_date} APOD information from NASA...success')
    except:
        # print(" || please check your Internet connection, While try ||")
        print(Fore.RED + '|| please check your Internet connection, While try ||' + Style.RESET_ALL)
        exit()
    try:
        title = json.loads(r.text)["title"]
    except:
        print(
            Fore.GREEN + "|| Your Program Run successfully But Today,s APOD is Not uploaded in API, please try later ||" + Style.RESET_ALL)
        exit()
    print(f'APOD title: {title}')

    print("APOD date:", apod_date)
    print(f"Getting {apod_date} APOD information from NASA...success")
    print(f"APOD title: {title}")

    # when in API image type is video at that time image URL is video's thumbnail URL
    # when in api image type is video at that time image url is video,s thumbnail url
    if json.loads(r.text)["media_type"] == "video":
        yt = YouTube(json.loads(r.text)["url"])
        # get the URL of the video's thumbnail
        imageurl = yt.thumbnail_url
        ext = '.jpg'
    else:
        imageurl = json.loads(r.text)["hdurl"]
        ext = os.path.splitext(imageurl)[-1]  # Construct the file name from the image title and extension from the URL
    print(f'APOD url: {imageurl}')

    # Downloading image from imageurl and save with constucted name
    print(f'Downloading image from: {imageurl}')
    explanation = json.loads(r.text)["explanation"]

    return {"date": apod_date,"title": title, "url": imageurl, "explanation" : explanation ,"extension": ext}
def get_apod_image_url(apod_info_dict):
    """Gets the URL of the APOD image from the dictionary of APOD information.

    If the APOD is an image, gets the URL of the high definition image.
    If the APOD is a video, gets the URL of the video thumbnail.

    Args:
        apod_info_dict (dict): Dictionary of APOD info from API

    Returns:
        str: APOD image URL
    """
    image_url=apod_info_dict['url']
    return image_url

if __name__ == '__main__':
    main()