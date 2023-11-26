"""
Originally designed by pasblo
GNU GENERAL PUBLIC LICENSE
"""

import math
import Vehicle
import Map
import pygame
import sys
import time
import AutonomusControl
import MapCreator

# Control variables
TIME_FACTOR = 1 # 1 second of simulation, equals TIME_FACTOR seconds
LIMIT_VEHICLES = 40

pygame.font.init()

# Create map from tiles
map_descriptor = [[{"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":4, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":5, "Rotation":0}, {"Tile":2, "Rotation":180}],
                  [{"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":4, "Rotation":90}, {"Tile":3, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}],
                  [{"Tile":2, "Rotation":270}, {"Tile":6, "Rotation":0}, {"Tile":4, "Rotation":0}, {"Tile":2, "Rotation":90}, {"Tile":1, "Rotation":90}],
                  [{"Tile":2, "Rotation":90, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":2, "Rotation":0}, {"Tile":3, "Rotation":0}, {"Tile":2, "Rotation":180}, {"Tile":1, "Rotation":90}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":2, "Rotation":0}, {"Tile":2, "Rotation":90}]]

"""map_descriptor = [[{"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":1, "Rotation":0}, {"Tile":4, "Rotation":0}, {"Tile":1, "Rotation":0}, {"Tile":1, "Rotation":0, "Spawn-speed":0.75, "Spawn-probability":1}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}],
                  [{"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}, {"Tile":1, "Rotation":90, "Spawn-speed":0.75, "Spawn-probability":1}, {"Tile":0, "Rotation":0}, {"Tile":0, "Rotation":0}]]"""

map_name = "TestMap"

map_size = MapCreator.create_map(map_descriptor, map_name)

screen = pygame.display.set_mode(map_size)
pygame.display.set_caption('Traffic System')

# Load map
test_map = Map.Map(map_name)

vehicles_list = []
latest_vehicle_id = 0

time_delta = 1
last_time = time.time_ns()
set_vehicle = -1
dynamic_multiplier = TIME_FACTOR
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
                dynamic_multiplier *= 0.8
            
            elif event.key == pygame.K_PLUS:
                dynamic_multiplier *= 1.2

    if len(vehicles_list) < LIMIT_VEHICLES:
        new_sapwns = AutonomusControl.spawn_vehicles(test_map, time_delta, latest_vehicle_id)
        vehicles_list.extend(new_sapwns["vehicles"])
        latest_vehicle_id = new_sapwns["new_id"]

    vehicles_list = AutonomusControl.despawn_vehicles(test_map, vehicles_list)

    AutonomusControl.move_vehicles(vehicles_list, test_map, time_delta, set_vehicle)
    AutonomusControl.check_collisions(vehicles_list)

    screen.fill((255, 255, 255))
    test_map.tick(time_delta)
    test_map.render(screen)
    AutonomusControl.render_vehicles(vehicles_list, screen, test_map, set_vehicle)
    pygame.display.flip()

    # Pump the event queue
    pygame.event.pump()

# NOTES:
# The function that calculates the distance between cars, it has to take into consideration
# the turning angles, and calculate the curved distance as well as the straight distance