# Google Earth View Downloader
[Earth View](https://earthview.withgoogle.com/) is a collection of the most beautiful and striking landscapes found in Google Earth. Every landscape image has a unique id. For example, the id of the image on ```https://earthview.withgoogle.com/antarctica-6488``` is ```6488```. This script makes it easier to download the images using their ids as it allows specifying a range of ids and automatically skips not found ones.

## Installation
```
$ git clone https://github.com/Sohairu/earthview-dl.git
$ cd earthview-dl
$ pip install -r requirements.txt
```

## Usage
```
$ python earthview-dl.py id1[-id2]
```
### Examples
Download single image of id 1301
```
$ python earthview-dl.py 1301
```
Download multiple images from id 1301 to id 1500
```
$ python earthview-dl.py 1301-1500
```