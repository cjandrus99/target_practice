# Import pygame and math libraries
import pygame
import math

# Initialize pygame
pygame.init()

# Set frames per second
fps = 60

# Initialize clock for timing
timer = pygame.time.Clock()

# Load fonts for text rendering
font = pygame.font.Font('assets/font/joystix monospace.otf', 16)
big_font = pygame.font.Font('assets/font/joystix monospace.otf', 60)

# Set screen dimensions
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# Create empty lists to hold images and coordinates
bgs = []
banners = []
guns = []
target_images = [[], [], []]

# Define target counts for each level
targets = {
    1: [10, 5, 3],
    2: [12, 8, 5],
    3: [15, 12, 8, 3]
}

# Initialize game variables
level = 0
points = 0
total_shots = 0
mode = 0  # 0 = freeplay, 1 = accuracy, 2 = timed
ammo = 0
time_passed = 0
time_remaining = 0
counter = 1
best_freeplay = 0
best_ammo = 0
best_timed = 0
shot = False
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
one_coords = [[], [], []]
two_coords = [[], [], []]
three_coords = [[], [], [], []]

# Load images for menus, backgrounds, banners, guns, and targets
menu_img = pygame.image.load(f'assets/menus/mainMenu.png')
game_over_img = pygame.image.load(f'assets/menus/gameOver.png')
pause_img = pygame.image.load(f'assets/menus/pauseMenu.png')

for i in range(1, 4):
    bgs.append(pygame.image.load(f'assets/backgrounds/{i}.png'))
    banners.append(pygame.image.load(f'assets/banners/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (100, 100)))
    if i < 3:
        for j in range(1, 4):
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))
    else:
        for j in range(1, 5):
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))

# Read high scores from file
file = open('high_scores.txt', 'r')
read_file = file.readlines()
file.close()
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_timed = int(read_file[2])

# Initialize and load sounds
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/bg_music.mp3')
plate_sound = pygame.mixer.Sound('assets/sounds/Broken plates.wav')
plate_sound.set_volume(.2)
bird_sound = pygame.mixer.Sound('assets/sounds/Drill Gear.mp3')
bird_sound.set_volume(.2)
laser_sound = pygame.mixer.Sound('assets/sounds/Laser Gun.wav')
laser_sound.set_volume(.3)
pygame.mixer.music.play()

# Function to draw the score on the screen
def draw_score():
    # Render and display points text
    points_text = font.render(f'Points: {points}', True, 'black')
    screen.blit(points_text, (330, 675))
    
    # Render and display total shots text
    shots_text = font.render(f'Total Shots: {total_shots}', True, 'black')
    screen.blit(shots_text, (330, 695))
    
    # Render and display time elapsed text
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'black')
    screen.blit(time_text, (330, 715))
    
    # Render and display mode-specific text
    if mode == 0:
        mode_text = font.render(f'Freeplay!', True, 'black')
    elif mode == 1:
        mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'black')
    elif mode == 2:
        mode_text = font.render(f'Time Remaining {time_remaining}', True, 'black')
    screen.blit(mode_text, (330, 735))

# Function to draw the gun on the screen
def draw_gun():
    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Define the point where the gun is positioned
    gun_point = (WIDTH / 2, HEIGHT - 200)
    
    # Define colors for lasers
    lasers = ['red', 'purple', 'green']
    
    # Get mouse click events
    clicks = pygame.mouse.get_pressed()
    
    # Calculate angle of rotation for gun based on mouse position
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
    else:
        slope = -100000
    angle = math.atan(slope)
    rotation = math.degrees(angle)
    
    # Determine gun orientation based on mouse position
    if mouse_pos[0] < WIDTH / 2:
        # Flip gun image horizontally if mouse is left of gun point
        gun = pygame.transform.flip(guns[level - 1], True, False)
        
        # Draw gun and laser if mouse is within shooting range
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
    else:
        # Draw gun and laser if mouse is within shooting range
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)



# Function to move the targets on the screen
def move_level(coords):
    # Determine maximum value for range based on current level
    if level == 1 or level == 2:
        max_val = 3
    else:
        max_val = 4
    
    # Iterate through each target's coordinates
    for i in range(max_val):
        for j in range(len(coords[i])):
            # Get current coordinates
            my_coords = coords[i][j]
            
            # Check if target has moved off screen, if so, reset its position
            if my_coords[0] < -150:
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                # Move target to the left based on the level
                coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1])
    return coords

# Function to draw the targets on the screen
def draw_level(coords):
    # Initialize list to hold target rectangles for collision detection
    if level == 1 or level == 2:
        target_rects = [[], [], []]
    else:
        target_rects = [[], [], [], []]
    
    # Iterate through each set of target coordinates
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            # Create rectangle for collision detection
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]),
                                                    (60 - i * 12, 60 - i * 12)))
            # Draw target image on screen at specified coordinates
            screen.blit(target_images[level - 1][i], coords[i][j])
    return target_rects

# Function to check if a shot hits any targets
def check_shot(targets, coords):
    # Access global variable for points
    global points
    
    # Get current mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Iterate through each target
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            # Check if the mouse position collides with any target
            if targets[i][j].collidepoint(mouse_pos):
                # Remove the target from its coordinates
                coords[i].pop(j)
                
                # Update points based on target hit and level
                points += 10 + 10 * (i ** 2)
                
                # Play sound effect based on level
                if level == 1:
                    bird_sound.play()
                elif level == 2:
                    plate_sound.play()
                elif level == 3:
                    laser_sound.play()
    
    # Return updated coordinates after checking shot
    return coords

# Function to draw the main menu
def draw_menu():
    # Access global variables for game state and scores
    global game_over, pause, mode, level, menu, time_passed, total_shots, points, ammo
    global time_remaining, best_freeplay, best_ammo, best_timed, write_values, clicked, new_coords
    
    # Reset game state flags
    game_over = False
    pause = False
    
    # Draw menu background image
    screen.blit(menu_img, (0, 0))
    
    # Get mouse position and mouse click events
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    
    # Define menu buttons and their positions
    freeplay_button = pygame.rect.Rect((170, 524), (260, 100))
    ammo_button = pygame.rect.Rect((475, 524), (260, 100))
    timed_button = pygame.rect.Rect((170, 661), (260, 100))
    reset_button = pygame.rect.Rect((475, 661), (260, 100))
    
    # Render and display high scores on menu buttons
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (360, 583.5))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (680, 583.5))
    screen.blit(font.render(f'{best_timed}', True, 'black'), (360, 720))
    
    # Check for button clicks and update game state accordingly
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        ammo = 81
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_remaining = 30
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_timed = 0
        clicked = True
        write_values = True

# Function to draw the game over screen
def draw_game_over():
    # Access global variables and flags
    global clicked, level, pause, game_over, menu, points, total_shots, time_passed, time_remaining
    
    # Determine which score to display based on game mode
    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    
    # Draw game over background image
    screen.blit(game_over_img, (0, 0))
    
    # Get mouse position and mouse click events
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    
    # Define exit and menu buttons and their positions
    exit_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    
    # Render and display final score on the screen
    screen.blit(big_font.render(f'{display_score}', True, 'white'), (650, 570))
    
    # Check for button clicks and update game state accordingly
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False

# Function to draw the pause screen
def draw_pause():
    # Access global variables and flags
    global level, pause, menu, points, total_shots, time_passed, time_remaining, clicked, new_coords
    
    # Draw pause screen background image
    screen.blit(pause_img, (0, 0))
    
    # Get mouse position and mouse click events
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    
    # Define resume and menu buttons and their positions
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    
    # Check for button clicks and update game state accordingly
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
        clicked = True
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        pygame.mixer.music.play()
        level = 0
        pause = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        clicked = True
        new_coords = True

# Main game loop
run = True
while run:
    # Limit frame rate
    timer.tick(fps)
    
    # Update time elapsed and remaining time based on game mode
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:
                time_remaining -= 1
    
    # Initialize enemy coordinates if new game starts
    if new_coords:
        # Initialize coordinates for each level of targets
        one_coords = [[], [], []]
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]
        # Generate coordinates for each target based on level and type
        for i in range(3):
            my_list = targets[1]
            for j in range(my_list[i]):
                one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(3):
            my_list = targets[2]
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
        for i in range(4):
            my_list = targets[3]
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
        new_coords = False
    
    # Clear the screen
    screen.fill('black')
    
    # Draw background and banner
    screen.blit(bgs[level - 1], (0, 0))
    screen.blit(banners[level - 1], (0, HEIGHT - 200))
    
    # Check game state and draw corresponding screens
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()
    
    # Draw targets, gun, and score if the game is running
    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False
    if level > 0:
        draw_gun()
        draw_score()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pygame.mouse.get_pos()
            # Check if the mouse click was within the game screen
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                shot = True
                total_shots += 1
                if mode == 1:
                    ammo -= 1
            # Check if the mouse click was on the pause button
            if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715):
                resume_level = level
                pause = True
                clicked = True
            # Check if the mouse click was on the menu button
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):
                menu = True
                pygame.mixer.music.play()
                clicked = True
                new_coords = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False
    
    # Check if level should be incremented or game should end
    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level += 1
        if (level == 3 and target_boxes == [[], [], [], []]) or (mode == 1 and ammo == 0) or (
                mode == 2 and time_remaining == 0):
            new_coords = True
            pygame.mixer.music.play()
            # Update high scores if necessary based on game mode
            if mode == 0:
                if time_passed < best_freeplay or best_freeplay == 0:
                    best_freeplay = time_passed
                    write_values = True
            if mode == 1:
                if points > best_ammo:
                    best_ammo = points
                    write_values = True
            if mode == 2:
                if points > best_timed:
                    best_timed = points
                    write_values = True
            game_over = True
    
    # Write high scores to file if necessary
    if write_values:
        file = open('high_scores.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')
        file.close()
        write_values = False
    
    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
