import os
import sys
import asyncio
import aiohttp
import aiofiles
from bs4 import BeautifulSoup

DOWNLOAD_DIRECTORY = "images"
MAX_TASKS = 5

def print_usage():
    print("\nUSAGE: python earthview-dl id1[-id2]")

def get_location(locationRegion, locationCountry):
    if locationRegion == None:
        locationRegion = ""
    
    if locationCountry == None:
        locationCountry = ""
    
    location = f"{locationRegion}, {locationCountry}"\
                if locationRegion and locationCountry\
                else f"{locationRegion}{locationCountry}"
    return location
    
async def resolve_image_url(session, urlPrefix, id, foundImages):
    async with session.get(f"{urlPrefix}/{id}") as response:
        soup = BeautifulSoup(await response.text(), "html.parser")
        if soup.title.string == "Error 404 – Not found":
            print(f"Id {id} not found")
        else:
            locationRegion = soup.find("div", class_="location__region").string
            locationCountry = soup.find("div", class_="location__country").string
            location = get_location(locationRegion, locationCountry)
            filename = f"google-earth-view-{id} ({location}).jpg"
            href = soup.find("a", title="Download Wallpaper")["href"]
            downloadUrl = f"{urlPrefix}{href}"
            foundImages.append((downloadUrl, filename))

async def download_image(session, sem, downloadUrl, filename):
    if not os.path.exists(DOWNLOAD_DIRECTORY):
        os.mkdir(DOWNLOAD_DIRECTORY)
    
    path = os.path.join(DOWNLOAD_DIRECTORY, filename)
    if os.path.exists(path):
        print(f"{filename} already exists")
    else:
        async with sem, session.get(downloadUrl) as r:
            if r.status == 200:
                content = await r.read()
                async with aiofiles.open(path, "wb") as f:
                    await f.write(content)
                print(f"Downloaded {filename}")

async def download_images(ids):
    foundImages = []
    #Remove not found (404) images ids
    async with aiohttp.ClientSession() as session:
        tasks = []
        urlPrefix = "https://earthview.withgoogle.com"
        for id in ids:
            task = asyncio.ensure_future(\
                resolve_image_url(session, urlPrefix, id, foundImages))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
    #Download found images ids
    if foundImages: #if not empty list
        sem = asyncio.Semaphore(MAX_TASKS)
        async with aiohttp.ClientSession() as session:
            tasks = []
            for downloadUrl, filename in foundImages:
                task = asyncio.ensure_future(download_image(session, sem, downloadUrl, filename))
                tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    #Ensure user provided image id(s) to download
    try:
        ids = sys.argv[1]
    except IndexError:
        print_usage()
        sys.exit(1)


    try:
        ids = [int(num) for num in ids.split('-')]
    #If id(s) not numeric int(num) raises ValueError
    except ValueError:
        print_usage()
        print("\nPlease ensure both id1 & id2 are integers")
        sys.exit(1)
    #Ensure no more 2 ids
    assert len(ids)<=2, "Incorrect Range"
    #Rearrange ids in ascending order if needed
    if ids[0] > ids[-1]:
        ids[0], ids[-1] = ids[-1], ids[0]

    ids = range(ids[0], ids[-1]+1)
    asyncio.get_event_loop().run_until_complete(download_images(ids))

    sys.exit(0)
