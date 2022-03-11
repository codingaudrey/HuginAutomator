# Hugin Automator
## About

This is a productivity tool for photographers who take too many large panoramas and whose computers cannot handle the workload. Photos added to specified Dropbox folders are automatically aligned and stitched in the cloud by dockerizing _Hugin_, an open-source panorama-creation application. 
 
This project also contains a tool for batch conversions of .RAW photos to .tiff in the cloud because converting thousands of images can be computationally expensive.

## Sections of the code:


* Automating aligning and stitching photos via _Hugin_.
  * Dockerfile-AlignAndStitch
  * HuginAutomator.py
  * main.py
* Automating converting .RAW photos to .tiff so they can be used by _Hugin_. 
  * Dockerfile-convert
  * converter/main.py
* Managing the connection to Dropbox / other cloud storage providers -- downloading raw photos from cloud storage and uploading final panoramas.
  * ConnectionHandler.py
    * ConnectionHandlerDropbox.py

## Usage
### Cloud Storage
#### Dropbox
To connect the application to your personal dropbox account, inside Dropbox/Apps, create a new folder called Hugin Automator and create a Dropbox API token for that folder. Put that token in this repository and name it token.txt. Inside Dropbox/Apps/Hugin Automator, create folders:
* stitch-new
* stitching
* stitched
* stitch-failed
* align-new
* aligning
* aligned
* align-failed
* convert-new
* converting
* converts-old


#### Other cloud storage
Create a class that inherits from ConnectionHandler.py. See ConnectionHandlerDropbox.py for an example.

### Cloud Run
Build the Docker images from Dockerfile-AlignAndStitch and Dockerfile-convert and put the images in GCP's Docker image repository. Then, set up two Cloud Run instances with these images and create the environment variables specified in main.py. To run the application, send an http request to the Cloud Run instance--from there it will automatically download and process your photos.


## Example
![Alt text](/Vine Street Cincinnati.jpg?raw=true "Title")
