import numpy as np
import cv2

# Create a blank image for the victory screen
victory_width = 800
victory_height = 600
victory_img = np.zeros((victory_height, victory_width, 3), dtype=np.uint8)

# Add a gradient background
for i in range(victory_height):
    color = int(255 * (i / victory_height))
    cv2.line(victory_img, (0, i), (victory_width, i), (color, color, 255))

# Add gold sparkles effect
for i in range(30):
    center_x = np.random.randint(30, victory_width)
    center_y = np.random.randint(30, victory_height)
    radius = np.random.randint(2, 6)
    color = (255, 215, 0)
    cv2.circle(victory_img, (center_x, center_y), radius, color, -1)

# Add a big trophy icon (simple yellow cup)
trophy_center = (victory_width // 2 + 10, 35)
cv2.ellipse(victory_img, trophy_center, (30, 18), 0, 0, 180, (255, 215, 0), -1)
cv2.rectangle(victory_img, (trophy_center[0] - 15, trophy_center[1]), (trophy_center[0] + 15, trophy_center[1] + 18), (255, 215, 0), -1)
cv2.rectangle(victory_img, (trophy_center[0] - 7, trophy_center[1] + 18), (trophy_center[0] + 7, trophy_center[1] + 28), (255, 215, 0), -1)
cv2.line(victory_img, (trophy_center[0] - 15, trophy_center[1] + 18), (trophy_center[0] - 15, trophy_center[1] + 10), (255, 215, 0), 2)
cv2.line(victory_img, (trophy_center[0] + 15, trophy_center[1] + 18), (trophy_center[0] + 15, trophy_center[1] + 10), (255, 215, 0), 2)

# Add congratulation message
congrats_text = "Congratulations!"
congrats_size = cv2.getTextSize(congrats_text, cv2.FONT_HERSHEY_DUPLEX, 1.2, 2)[0]
congrats_x = (victory_width - congrats_size[0]) // 2 + 10
congrats_y = 35
cv2.putText(victory_img, congrats_text, (congrats_x, congrats_y), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)

# Display the victory image
cv2.imshow("Victory", victory_img)
cv2.waitKey(0)
cv2.destroyAllWindows()