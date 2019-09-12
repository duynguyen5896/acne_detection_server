# acne_detection_server
a nodejs server include python module

-User request API:
-NodeJS: (I/O: JSON ----> JSON)
	+ Process JSON
	+ Decode Base64 to Image and save to /images/userID/sessionID/
	+ Create results folder in above directory
	+ Call Python file
	+ Encode images from results folder to Base64 and return to Client
-Python: (I/O: Images --> Processed Images)
	+ Read all images from /images/userID/sessionID/
	+ Process images
	+ Save images to results folder