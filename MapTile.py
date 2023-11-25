"""
Originally designed by pasblo
MIT License
"""

import pygame
import json
import Map
import math
import math_utils

# Before doing any change put coordinates with respect to the center of the tile, remember -y

# The tile needs to be square

GRASS = {"Name":"Grass", "id":0}
STRAIGHT = {"Name":"Straight", "id":1}
TURN = {"Name":"Turn", "id":2}
UNCONTROLLED_CROSSROAD = {"Name":"Uncontrolled_crossroad", "id":3}
CONTROLLED_T_INTERSECTION = {"Name":"Controlled_T_intersection", "id":4}
CONTROLLED_CROSSROAD = {"Name":"Controlled_crossroad", "id":5}
TRAFFIC_LIGHT_CONTROLLED_CROSSROAD = {"Name":"Traffic_light_controlled_crossroad", "id":6}

TILES = ["Grass", "Straight", "Turn", "Uncontrolled_crossroad",
         "Controlled_T_intersection", "Controlled_crossroad",
         "Traffic_light_controlled_crossroad"]

class Road_Connection():

    def __init__(self, specs):

        # Basic information
        self.angle = math.radians(specs["angle"])

class MapTile():
    def __init__(self, name):

        # Basic map tile data
        self.name = name
        self.image_path = "images/map_tiles/" + self.name + ".png"
        self.image = pygame.image.load(self.image_path)
        self.size_x = self.image.get_rect().width # Pixels
        self.size_y = self.image.get_rect().height # Pixels

        try:
            #Json map tile data
            self.json_path = "maps/map_tiles/" + self.name + ".json"
            with open(self.json_path, "r", encoding = "utf-8") as file:
                self.json = json.load(file)
        
        except Exception as e:
            pass
        
        try:
            # Mobility map data
            self.stops_specs = self.json.get("stops", [])
            self.stops = [Map.Stop(specs) for specs in self.stops_specs]
        
        except Exception as e:
            self.stops = []
            
        try:

            self.traffic_lights_specs = self.json.get("traffic-lights", [])
            self.traffic_lights = [Map.Traffic_Light(specs) for specs in self.traffic_lights_specs]

        except Exception as e:
            self.traffic_lights = []

        try:
            self.turns_specs = self.json.get("turns", [])
            self.turns = [Map.Turn(specs) for specs in self.turns_specs]
        
        except Exception as e:
            self.turns = []

        try:
            self.road_connections_specs = self.json.get("road-connections", [])
            self.road_connections = [Road_Connection(specs) for specs in self.road_connections_specs]
        
        except Exception as e:
            self.road_connections = []
    
    def update_tile(self, new_size, rotation, shift_x, shift_y, elements_id):
        """
        Moves the tile json and image information to a new position and scaled to a new size.
        """

        # Takes as refference x side cause both should be the same
        scaling = new_size / self.size_x

        # Center all coordinates from the center of the tile
        for stop in self.stops:
            stop.start_x -= self.size_x / 2
            stop.start_y *= -1
            stop.start_y += self.size_y / 2
            stop.end_x -= self.size_x / 2
            stop.end_y *= -1
            stop.end_y += self.size_y / 2

        for traffic_light in self.traffic_lights:
            traffic_light.x -= self.size_x / 2
            traffic_light.y *= -1
            traffic_light.y += self.size_y / 2
        
        for turn in self.turns:
            turn.x -= self.size_x / 2
            turn.y *= -1
            turn.y += self.size_y / 2

        # Resize
        self._resize(scaling)

        # Rotate
        self._rotate(rotation)

        # Shift
        self._move(shift_x, shift_y)

        # Uncenter the coordinates from the tile
        for stop in self.stops:
            stop.start_x += self.size_x / 2
            stop.start_y -= self.size_y / 2
            stop.start_y *= -1
            stop.end_x += self.size_x / 2
            stop.end_y -= self.size_y / 2
            stop.end_y *= -1
        
        for traffic_light in self.traffic_lights:
            traffic_light.x += self.size_x / 2
            traffic_light.y -= self.size_y / 2
            traffic_light.y *= -1
        
        for turn in self.turns:
            turn.x += self.size_x / 2
            turn.y -= self.size_y / 2
            turn.y *= -1

        # Update the different elements ids
        actual_stop_id = elements_id["stops-ids"]
        actual_turn_id = elements_id["turns-ids"]
        actual_traffic_lights_id = elements_id["traffic-lights-ids"]
        for stop in self.stops:
            stop.id += actual_stop_id
            stop.trigger_light_id += actual_traffic_lights_id
            
        actual_stop_id += len(self.stops)
        
        for traffic_light in self.traffic_lights:
            traffic_light.id += actual_traffic_lights_id
        
        actual_traffic_lights_id += len(self.traffic_lights)
        
        for turn in self.turns:
            turn.id += actual_turn_id

        actual_turn_id += len(self.turns)
        
        # Return all information as dictionary ready for json file with all updated information
        stops = []
        for stop in self.stops:
            stops.append(stop.get_json_dictionary())
        
        traffic_lights = []
        for traffic_light in self.traffic_lights:
            traffic_lights.append(traffic_light.get_json_dictionary())
        
        turns = []
        for turn in self.turns:
            turns.append(turn.get_json_dictionary())
        
        return {"surface":self.image,
                "data":{
                    "stops":stops,
                    "turns":turns,
                    "traffic-lights":traffic_lights
                },
                "road-connections":self.road_connections,
                "elements-ids":{
                    "stops-ids":actual_stop_id,
                    "turns-ids":actual_turn_id,
                    "traffic-lights-ids":actual_traffic_lights_id
                }
        }
                
    
    def _resize(self, factor):

        # Resize the tile itself
        self.size_x *= factor
        self.size_y *= factor
        self.image = pygame.transform.scale(self.image, (self.size_x * factor, self.size_y * factor))

        # Resize stops
        for stop in self.stops:
            # Resize start and end points
            stop.start_x *= factor
            stop.start_y *= factor
            stop.end_x *= factor
            stop.end_y *= factor
        
        # Resize traffic lights
        for traffic_light in self.traffic_lights:
            # Resize center point and distances
            traffic_light.x *= factor
            traffic_light.y *= factor
        
        # Resize turns
        for turn in self.turns:
            # Resize point
            turn.x *= factor
            turn.y *= factor
            turn.min_distance *= factor
            turn.max_distance *= factor
    
    def _rotate(self, radians):

        # Rotate the image
        self.image = pygame.transform.rotate(self.image, math.degrees(radians))

        # Rotate stops
        for stop in self.stops:

            # Rotate start and end points
            stop.start_x, stop.start_y = math_utils.rotate_point(stop.start_x, stop.start_y, radians)
            stop.end_x, stop.end_y = math_utils.rotate_point(stop.end_x, stop.end_y, radians)
        
        # Rotate traffic lights
        for traffic_light in self.traffic_lights:

            # Rotate center point
            traffic_light.x, traffic_light.y = math_utils.rotate_point(traffic_light.x, traffic_light.y, radians)
        
        # Rotate turns
        for turn in self.turns:

            # Rotate center point
            turn.x, turn.y = math_utils.rotate_point(turn.x, turn.y, radians)

            # Update angles
            turn.first_angle += radians
            turn.first_angle = math_utils.correct_radian(turn.first_angle)
            turn.second_angle += radians
            turn.second_angle = math_utils.correct_radian(turn.second_angle)

        # Rotate road connections
        for road_connection in self.road_connections:
            road_connection.angle += radians
            road_connection.angle = math_utils.correct_radian(road_connection.angle)
    
    def _move(self, dx, dy):

        # Move stops
        for stop in self.stops:
            # Move start and end points
            stop.start_x += dx
            stop.start_y -= dy
            stop.end_x += dx
            stop.end_y -= dy

        # Move traffic lights
        for traffic_light in self.traffic_lights:
            # Move center point
            traffic_light.x += dx
            traffic_light.y -= dy

        # Move turns
        for turn in self.turns:
            # Move point
            turn.x += dx
            turn.y -= dy