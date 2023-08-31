def get_bounding_box_direction(frame_shape, box_center, name, threshold=150):
    height, width, _ = frame_shape
    center_x, center_y = box_center
#Threshold is the distance from the center at which it detect center
#otherwise it will detect right or left


    # Calculate the horizontal direction
    if center_x < width // 2 - threshold:
        #to the left
        horizontal_direction = "sort"   
    else:
        #to the right
        horizontal_direction = "rentre"


    # Calculate the vertical direction, not used in the current situation
    if center_y < height // 2 - threshold:
        vertical_direction = "Up"
    elif center_y > height // 2 + threshold:
        vertical_direction = "Down"
    else:
        vertical_direction = "Center"

    
    return f"{horizontal_direction}"