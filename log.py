

#importing the module 
import logging 
import time
import cv2

pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)

# Initialize previous_directions dictionary to store the previous direction for each person
previous_directions = {}

#now we will Create and configure logger 
def logging_function(top, right, bottom, left, person_folder, direction):
    global previous_directions
    
    # Set up the basic configuration for the logging module
    logging.basicConfig(filename="std.txt", format='%(asctime)s %(message)s', filemode='a')
    
    # Create a logger object
    logger = logging.getLogger()
    
    # Set the threshold of the logger to DEBUG
    logger.setLevel(logging.DEBUG)
    
    # Get the previous direction for the person from the dictionary
    prev_direction = previous_directions.get(person_folder)
    

    if prev_direction is None or prev_direction != direction:
        # Log the entry/exit only when direction changes or for the first entry
        logger.info('%s est %s', person_folder, "entrée" if "rentre" in direction else "sorti")
        
        # Update the previous direction for the person
        previous_directions[person_folder] = direction


if __name__ == "__main__":
    # Call the logging function with example data
    logging_function()



