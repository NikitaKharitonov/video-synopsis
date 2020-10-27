# video-synopsis 
## About
This is a simple implementation of the Video Synopsis technology for my research work at Samara University
https://en.wikipedia.org/wiki/Video_synopsis

The program takes the input video of moving people on a static background, tracks and indexes each person on the video, then analyzes the tracked data and creates a video summary of the original video

## Features
* Object detection and tracking 
* Object indexing 
* Creating a video summary 

## Requirements
* python 3.8.5
* numpy 1.19.2
* opencv-python 4.4.0.44
* scipy 1.5.3

## How to use 
Add the file named 'original.avi' in the root directory and run main.py. The result video will be saved in the 'results' folder with the corresponding timestamp

## To-do
* Add user interface 
* Optimize
* Deploy on a server (maybe)
* Track not only people but other objects as well: cars, bikes...
* Display labels and time references for each object on the result video
* Come up with more features 
* Test

