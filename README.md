# winsight

## What it does

Winsight can connect to any external camera (webcam, integrated camera, etc.) and read the dealer's as well as your cards using OpenCV for image processing and a YOLOv8 pre-trained object detection model. Winsight will then algorithmically deduce the best course of action (hit or stand), the chance of winning or busting, how much you should increase or reduce your bet by based on said chances, all while keeping track of all cards that have been tabled to more accurately deduce moves for every subsequent hand.

## How we built it

We used **Flask** to create a web application in **Python**, which allowed us to connect our back-end to a **HTML/CSS/JavaScript** front-end and display everything going on behind the scenes. We used **OpenCV** to handle all of the live feed processing from our webcam (grayscaling, binary thresholding, contouring) to increase the accuracy of the object detection. Lastly, we used a pre-trained **YOLOv8** object detection model that had been trained with a dataset of playing cards so that it could recognize the user's and dealer's cards.
