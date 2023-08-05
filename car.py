import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()  # Initialize the mixer module for sound

# Constants
WIDTH, HEIGHT = 800, 600
CAR_WIDTH, CAR_HEIGHT = 50, 100
LINE_HEIGHT = 2  # Height of the dotted line
FPS = 60

# Colors
BLACK = (0, 0, 0)
BACKGROUND_LINE_COLOR = (51, 51, 51)  # RGB value for #333
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Create the window (fullscreen)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_width(), screen.get_height()
pygame.display.set_caption("Car Game")

# Load car image
car_image = pygame.image.load('car.png')  # You can replace 'car.png' with your car image file
car_image_flipped = pygame.transform.flip(car_image, True, False)

# Load beep sound
beep_sound = pygame.mixer.Sound('beep.wav')  # Replace 'beep.wav' with the path to your beep sound file
horn_sound = pygame.mixer.Sound('horn.wav')  # Replace 'horn.wav' with the path to your horn sound file

# Starting position of the car
car_x, car_y = (WIDTH - CAR_WIDTH) // 2, HEIGHT - CAR_HEIGHT

# Initialize time variable and blinking variables
time = 0
show_game_name = True
last_blink_time = pygame.time.get_ticks()
last_color_change_time = pygame.time.get_ticks()
background_color = BLACK

# Calculate the font size for the game name to have a width of 200 pixels
desired_width = 200
font_size = 1
font = pygame.font.Font(None, font_size)
while font.size("Colored Car Game")[0] < desired_width:
    font_size += 1
    font = pygame.font.Font(None, font_size)
font_size -= 1  # Go back one step as the previous size was greater than the desired width
font = pygame.font.Font(None, font_size)
game_name_text = font.render("Colored Car Game", True, (255, 255, 255))

# Class representing the balls
class Ball:
    def __init__(self):
        self.radius = 10
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(-HEIGHT, HEIGHT - self.radius)  # Start from random positions above the screen
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.visible = True

    def draw(self):
        if self.visible:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move_down(self):
        self.y += 2  # Adjust the speed of the balls (increase this value for faster motion)

# Function to check collision between the car and balls
def check_collision(ball):
    distance = math.sqrt((ball.x - car_x) ** 2 + (ball.y - car_y) ** 2)
    if distance < ball.radius + CAR_HEIGHT // 2:
        ball.visible = False
        return True
    return False

# Initialize balls list and score
balls = [Ball() for _ in range(50)]
score = 0

# Initialize joystick
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get the joystick input
    pygame.event.pump()  # Process the joystick events
    x_axis = joystick.get_axis(0)
    y_axis = joystick.get_axis(1)

    # Control the car using the joystick input
    car_x += int(x_axis * 5)
    car_y += int(y_axis * 5)

    # Boundary checking for car position
    car_x = max(0, min(WIDTH - CAR_WIDTH, car_x))
    car_y = max(0, min(HEIGHT - CAR_HEIGHT, car_y))

    # Fill the background with blinking color
    current_time = pygame.time.get_ticks()
    if current_time - last_color_change_time >= 10000:  # Change color every 10 seconds (10000 milliseconds)
        last_color_change_time = current_time
        if background_color == BLACK:
            background_color = YELLOW
        elif background_color == YELLOW:
            background_color = RED
        elif background_color == RED:
            background_color = GREEN
        elif background_color == GREEN:
            background_color = BLACK

    screen.fill(background_color)

    # Draw the game name in the top left corner (blinking effect)
    if current_time - last_blink_time >= 500:  # Blink every half a second (500 milliseconds)
        last_blink_time = current_time
        show_game_name = not show_game_name

    if show_game_name:
        screen.blit(game_name_text, (10, 10))

    # Draw the street (dotted line) continuously moving from top to bottom
    for y in range(time, HEIGHT, 20):  # Increase the last parameter for larger gaps between dots
        pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - LINE_HEIGHT // 2, y, LINE_HEIGHT, 10))

    # Draw the car on the screen
    screen.blit(car_image, (car_x, car_y))

    # Check if X button is pressed and if there is a ball above the car
    x_button_pressed = joystick.get_button(0)  # X button on PS4 controller is button 0
    ball_above_car = any(ball.visible and abs(ball.x - car_x) < ball.radius and ball.y < car_y for ball in balls)

    # Draw the balls and check for collisions
    for ball in balls:
        ball.move_down()
        if ball.y > HEIGHT + ball.radius:  # Reset the ball when it goes beyond the screen
            ball.x = random.randint(ball.radius, WIDTH - ball.radius)
            ball.y = random.randint(-HEIGHT, -ball.radius)
            ball.visible = True
        if ball.visible and check_collision(ball):
            score += 1
            beep_sound.play()  # Play the beep sound when a ball is collected

        # If X button is pressed and a ball is above the car, play the horn sound
        if x_button_pressed and ball_above_car:
            horn_sound.play()

        ball.draw()

    # Display the score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 60))

    # Increment time variable for motion movement
    time = (time + 2) % 20  # Adjust the value (2) for the desired motion speed

    # Update the display
    pygame.display.flip()

    # Limit frames per second
    clock.tick(FPS)
