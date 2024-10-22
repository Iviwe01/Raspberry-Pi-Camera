PiCam Studio
A sophisticated Raspberry Pi camera application with a modern graphical interface, providing advanced image capture and processing capabilities.
Features

Real-time camera preview
Image capture with visual feedback
Multiple image filters:

Grayscale
Sepia
Invert
Blur
Sharpen
Edge Detection


Firebase cloud storage integration
Customizable camera settings
Progress tracking for uploads
Comprehensive error logging
User-friendly interface

Prerequisites

Raspberry Pi (3 or newer recommended)
Raspberry Pi Camera Module
Python 3.7+
Required Python packages:

tkinter
picamera2
Pillow
firebase-admin
logging



Installation

Clone the repository:

bashCopygit clone https://github.com/yourusername/picam-studio.git
cd picam-studio

Install required packages:

bashCopypip install -r requirements.txt

Configure Firebase:


Create a Firebase project
Download your serviceAccountKey.json
Place it in the project root directory
Update the storage bucket in the code:

pythonCopy'storageBucket': 'your-bucket-name.appspot.com'
Usage

Start the application:

bashCopypython camera_app.py

Main functionalities:


Click "Start Preview" to view camera feed
Use "Capture Image" to take photos
Apply filters with the "Apply Filter" button
Adjust settings via the "Settings" menu
Monitor upload progress with the progress bar

Application Structure

camera_app.py: Main application file
serviceAccountKey.json: Firebase configuration
camera_app.log: Application logs
requirements.txt: Required dependencies

Class Overview
CameraApp
Main application class containing:

GUI initialization
Camera control methods
Image processing functions
Firebase integration
Error handling and logging

Key Methods

toggle_preview(): Controls camera preview
capture_image(): Handles image capture
apply_filter(): Processes image filters
upload_to_firebase(): Manages cloud storage
open_settings(): Controls camera parameters

Error Handling

Comprehensive error logging
User-friendly error messages
Robust exception handling
Detailed logging to camera_app.log

Contributing

Fork the repository
Create your feature branch
Commit your changes
Push to the branch
Submit a pull request

Future Enhancements

Additional image filters
Video recording capability
Time-lapse photography
Custom filter creation
Advanced camera settings
Multi-camera support

Known Issues

High CPU usage during preview
Memory usage with large images
Firebase upload delays on slow connections

License
This project is licensed under the MIT License - see the LICENSE file for details.
Contact
For support or queries:

Create an issue in the repository
Contact: your.email@example.com

Acknowledgments

Raspberry Pi Foundation
Firebase Team
PIL/Pillow Contributors
Tkinter Community

Developed by : Iviwe Mtambeka
