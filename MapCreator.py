"""
Originally designed by pasblo
MIT License
"""

import MapTile
import math_utils
import pygame
import math
import json

TILE_SIZE = 21 # In meters, cannot be changed (Fixed to tile and vehicle image design)

def create_map(map_descriptor, map_name):

    # Size on pixels of each tile
    tile_pixel_size = TILE_SIZE * math_utils.MAP_SCALE

    # Size of the screen needed to create this map
    screen_width = len(map_descriptor[0]) * tile_pixel_size
    screen_heigth = len(map_descriptor) * tile_pixel_size

    # Creating the final map
    map_image = pygame.Surface((screen_width, screen_heigth))
    map_data = {"stops":[], "turns":[], "traffic-lights":[], "spawn-points":[], "despawn-points":[]}

    # Id incrementer
    spawn_point_id = 0
    despawn_point_id = 0
    elements_ids = {"stops-ids":0, "turns-ids":0, "traffic-lights-ids":0}
    
    # Going over each row
    y = 0
    for tile_descriptor_row in map_descriptor:
        
        # Going over each tile
        x = 0
        for tile_descriptor in tile_descriptor_row:
            
            # Instance of new tile
            new_tile = MapTile.MapTile(MapTile.TILES[tile_descriptor["Tile"]]) # To-do, fix ids like spawn and despawn was done

            # Calculate new position of the tile
            tile_x = x * tile_pixel_size
            tile_y = y * tile_pixel_size

            # Modify the tile
            tile_data = new_tile.update_tile(tile_pixel_size, math.radians(tile_descriptor["Rotation"]), tile_x, tile_y, elements_ids)

            # Update elements ids
            elements_ids = tile_data["elements-ids"]

            # Connection angles for the tile
            road_connections_angles = [road_connection.angle for road_connection in tile_data["road-connections"]]

            # Define where are the roads with respect to the tile
            road_start_tile = tile_pixel_size / 3 # The road starts at 7m from the edge of the tile
            road_middle_tile = tile_pixel_size / 2 # The road is always exacly in the middle of the tile
            road_end_tile = 2 * tile_pixel_size / 3 # The road is always 7m in length

            # Get the spawn base speed of the tile
            try:
                spawn_speed = tile_descriptor["Spawn-speed"]
            
            except Exception as e:
                spawn_speed = 0.5 # Default spawn speed if none is defined
            
            # Get the spawn probability of the tile
            try:
                spawn_probability = tile_descriptor["Spawn-probability"]
            
            except Exception as e:
                spawn_probability = 0.1 # Default spawn probability if none is defined

            # Check if this tile has a connection on the top edge of the map
            if y == 0 and math.radians(90) in road_connections_angles:

                # Left most lane is spawn, on the pixel more separated from the center, that's why floor
                x_spawn_point = tile_x + road_start_tile + math.floor((road_middle_tile - road_start_tile) / 2)
                new_spawn_point = {"id":spawn_point_id, "x":x_spawn_point, "y":0, "direction":270, "speed":spawn_speed, "probability-per-second":spawn_probability}
                map_data["spawn-points"].append(new_spawn_point)
                spawn_point_id += 1

                # Right most lane is despawn
                start_x_despawn_line = tile_x + road_middle_tile
                end_x_despawn_line = tile_x + road_end_tile
                new_despawn_point = {"id":despawn_point_id, "start-x":start_x_despawn_line, "start-y":0, "end-x":end_x_despawn_line, "end-y":0}
                map_data["despawn-points"].append(new_despawn_point)
                despawn_point_id += 1
            
            # Check if this tile has a connection on the left side of the map
            if x == 0 and math.radians(180) in road_connections_angles:

                # Top most lane is despawn
                start_y_despawn_line = tile_y + road_start_tile
                end_y_despawn_line = tile_y + road_middle_tile
                new_despawn_point = {"id":despawn_point_id, "start-x":0, "start-y":start_y_despawn_line, "end-x":0, "end-y":end_y_despawn_line}
                map_data["despawn-points"].append(new_despawn_point)
                despawn_point_id += 1

                # Bottom most lane is spawn
                y_spawn_point = tile_y + road_middle_tile + math.floor((road_end_tile - road_middle_tile) / 2)
                new_spawn_point = {"id":spawn_point_id, "x":0, "y":y_spawn_point, "direction":0, "speed":spawn_speed, "probability-per-second":spawn_probability}
                map_data["spawn-points"].append(new_spawn_point)
                spawn_point_id += 1
            
            # Check if this tile has a connection on the bottom side of the map
            if y == len(map_descriptor[0]) - 1 and math.radians(270) in road_connections_angles:

                # Left most lane is despawn
                start_x_spawn_line = tile_x + road_start_tile
                end_x_spawn_line = tile_x + road_middle_tile
                y_spawn_line = tile_y + tile_pixel_size
                new_despawn_point = {"id":despawn_point_id, "start-x":start_x_spawn_line, "start-y":y_spawn_line, "end-x":end_x_spawn_line, "end-y":y_spawn_line}
                map_data["despawn-points"].append(new_despawn_point)
                despawn_point_id += 1

                # Right most lane is spawn
                x_spawn_point = tile_x + road_middle_tile + math.floor((road_end_tile - road_middle_tile) / 2)
                y_spawn_point = tile_y + tile_pixel_size
                new_spawn_point = {"id":spawn_point_id, "x":x_spawn_point, "y":y_spawn_point, "direction":90, "speed":spawn_speed, "probability-per-second":spawn_probability}
                map_data["spawn-points"].append(new_spawn_point)
                spawn_point_id += 1

            # Check if this tile has a connection on the right side of the map
            if x == len(map_descriptor) - 1 and math.radians(0) in road_connections_angles:

                # Top most lane is spawn
                y_spawn_point = tile_y + road_start_tile + math.floor((road_middle_tile - road_start_tile) / 2)
                x_spawn_point = tile_x + tile_pixel_size
                new_spawn_point = {"id":spawn_point_id, "x":x_spawn_point, "y":y_spawn_point, "direction":180, "speed":spawn_speed, "probability-per-second":spawn_probability}
                map_data["spawn-points"].append(new_spawn_point)
                spawn_point_id += 1

                # Bottom most lane is despawn
                start_y_despawn_line = tile_y + road_middle_tile
                end_y_despawn_line = tile_y + road_end_tile
                x_spawn_line = tile_x + tile_pixel_size
                new_despawn_point = {"id":despawn_point_id, "start-x":x_spawn_line, "start-y":start_y_despawn_line, "end-x":x_spawn_line, "end-y":end_y_despawn_line}
                map_data["despawn-points"].append(new_despawn_point)
                despawn_point_id += 1

            # Add the tile image to the map
            map_image.blit(tile_data["surface"], (tile_x, tile_y))  # Blit onto the final surface at (0, 0)

            # Add the dictionary entries
            map_data["stops"].extend(tile_data["data"]["stops"])
            map_data["turns"].extend(tile_data["data"]["turns"])
            map_data["traffic-lights"].extend(tile_data["data"]["traffic-lights"])

            # Increase x coordinate
            x += 1
        
        # Increase y coordinate
        y += 1
    
    # Save the map as png
    pygame.image.save(map_image, "images/maps/" + map_name + ".png")

    # Save the map info as json
    with open("maps/" + map_name + ".json", "w") as json_file:
        json.dump(map_data, json_file)
    
    # Return screen size
    return (screen_width, screen_heigth)
