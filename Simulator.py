"""
Originally designed by pasblo
GNU GENERAL PUBLIC LICENSE
"""

import pygame
import sys
import time
import src.Map as Map
import src.AutonomusControl as AutonomusControl
import src.MapCreator as MapCreator
import src.Vanet as Vanet

# Control variables
TIME_FACTOR = 1 # 1 second of simulation, equals TIME_FACTOR seconds
LIMIT_VEHICLES = 50

# Initialize pygame fonts
pygame.font.init()
font = pygame.font.Font(None, 36)

# Initialize pygame clock
clock = pygame.time.Clock()

# Create data for all transceivers
transceiver_descriptor = [{"tx_power": 0.2, "sensibility": -40, "frequency":4.9e9}, {"tx_power": 0.5, "sensibility": -40, "frequency":4.9e9}, {"tx_power": 0.5, "sensibility": -40, "frequency":4.9e9}, {"tx_power": 0.2, "sensibility": -40, "frequency":4.9e9}]

# Create vanet
vanet = Vanet.Vanet(transceiver_descriptor)

# Calculate the maximum distances for all transceivers
distances = vanet.calculate_max_distances()

"""map_descriptor = [[{"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":4, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":5, "Rotation":0}, {"Tile":2, "Rotation":180}],
                  [{"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":4, "Rotation":90}, {"Tile":3, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}],
                  [{"Tile":2, "Rotation":270}, {"Tile":6, "Rotation":0}, {"Tile":4, "Rotation":0}, {"Tile":2, "Rotation":90}, {"Tile":1, "Rotation":90}],
                  [{"Tile":2, "Rotation":90, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":2, "Rotation":0}, {"Tile":3, "Rotation":0}, {"Tile":2, "Rotation":180}, {"Tile":1, "Rotation":90}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":2, "Rotation":0}, {"Tile":2, "Rotation":90}]]"""

"""map_descriptor = [[{"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":1, "Rotation":0}, {"Tile":4, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}]]"""

# Create map from tiles
map_descriptor = [[{"Tile":1, "Rotation":0, "Spawn-speed":1, "Spawn-probability":5}, {"Tile":4, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0, "Spawn-speed":1, "Spawn-probability":5}],
                  [{"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":2, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":2, "Rotation":180}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":2, "Rotation":270}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":4, "Rotation":90}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":6, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":2, "Rotation":180}],
                  [{"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":2, "Rotation":180}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}],
                  [{"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":2, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":2, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":6, "Rotation":0}, {"Tile":2, "Rotation":180}, {"Tile":0, "Rotation":0}],
                  [{"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1.5}, {"Tile":3, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":2, "Rotation":90}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90, "Spawn-speed":0.5, "Spawn-probability":1}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90, "Spawn-speed":0.3, "Spawn-probability":2}, {"Tile":0, "Rotation":0}]]

# Create the map itself and get the size needed for the screen
map_name = "Map"
map_size = MapCreator.create_map(map_descriptor, map_name)

# Create the screen and name it
screen = pygame.display.set_mode(map_size, pygame.SRCALPHA)
pygame.display.set_caption('Traffic System')

# Load map
test_map = Map.Map(map_name)

# Load all variables needed
vehicles_list = []
latest_vehicle_id = 0
dynamic_multiplier = TIME_FACTOR
time_delta = 1
last_time = time.time_ns()
set_vehicle = -1

# Calculate error probability
total_number_of_collisions = 0
total_number_of_cars = 0
collision_rate = 0

"""
Probabilidades:
Sin nada: ~4%
Con frenado entre coches: ~0.1%
Con algoritmo: 
"""

while True:

    # Time delta calculations
    time_delta = (time.time_ns() - last_time) * dynamic_multiplier
    last_time = time.time_ns()

    # Avoid jumps when grabbing the window
    if time_delta > 10000000 * dynamic_multiplier:
        time_delta = 0

    # Detect pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()

            clicked_vehicle = False
            for vehicle in vehicles_list:
                if vehicle.rotated_rect.collidepoint(x, y):
                    set_vehicle = vehicle.id
                    clicked_vehicle = True

            if not clicked_vehicle:
                set_vehicle = -1
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_MINUS:
                dynamic_multiplier -= 0.1
            
            elif event.key == pygame.K_PLUS:
                dynamic_multiplier += 0.1

    # Making sure the we only have a certain amount of vehicles
    if len(vehicles_list) < LIMIT_VEHICLES:

        # Spawn vehicles on the spawn points
        new_sapwns = AutonomusControl.spawn_vehicles(test_map, time_delta, latest_vehicle_id, distances)
        total_number_of_cars += len(new_sapwns)
        vehicles_list.extend(new_sapwns["vehicles"])
        latest_vehicle_id = new_sapwns["new_id"]
    
    # Update all elements on the map
    test_map.tick(time_delta)

    # Despawn vehicles if needed
    vehicles_list = AutonomusControl.despawn_vehicles(test_map, vehicles_list, map_size)

    # Move all vehicles
    AutonomusControl.move_vehicles(vehicles_list, test_map, time_delta, set_vehicle)

    # Check the collisions between the vehicles
    total_number_of_collisions += AutonomusControl.check_collisions(vehicles_list)

    # Calculate the collision rate
    collision_rate = (total_number_of_collisions / total_number_of_cars) * 100

    # Fill the screen with black
    screen.fill((255, 255, 255))

    # Render all elements on the screen
    test_map.render(screen)
    AutonomusControl.render_vehicles(vehicles_list, screen, test_map, set_vehicle)

    # FPS counter
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {fps:.2f}", True, (255, 165, 0))
    screen.blit(fps_text, (10, 10))

    # Render the debug text on the screen
    text_1 = font.render(f"Speed: {dynamic_multiplier}", True, (0, 0, 0))  # Black color
    text_1_rect = text_1.get_rect()
    text_1_rect.topleft = (10, pygame.display.Info().current_h - text_1_rect.height - 10)  # Adjust the position here
    screen.blit(text_1, text_1_rect)

    text_1 = font.render(f"# Vehicles: {len(vehicles_list)}", True, (0, 0, 0))  # Black color
    text_1_rect = text_1.get_rect()
    text_1_rect.topleft = (10, pygame.display.Info().current_h - text_1_rect.height - 30)  # Adjust the position here
    screen.blit(text_1, text_1_rect)

    text_1 = font.render(f"Collision rate: {collision_rate}%", True, (0, 0, 0))  # Black color
    text_1_rect = text_1.get_rect()
    text_1_rect.topleft = (10, pygame.display.Info().current_h - text_1_rect.height - 50)  # Adjust the position here
    screen.blit(text_1, text_1_rect)

    # Update the screen
    pygame.display.flip()

    # Pump the event queue
    pygame.event.pump()

    # Tick the FPS clock
    clock.tick()  # Set the desired frame rate (e.g., 60 FPS)
