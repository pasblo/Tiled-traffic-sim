"""
Originally designed by pasblo
MIT License
"""

import pygame
import json
import time
import math
import math_utils
import random

class Stop:
    """
    Line defined by a start point and an end point.
    """
    def __init__(self, specs):
        self.id = specs["id"]
        self.start_x = specs["start-x"]
        self.start_y = specs["start-y"]
        self.end_x = specs["end-x"]
        self.end_y = specs["end-y"]
        self.trigger_light_id = specs["trigger-traffic-light-id"]
    
    def get_json_dictionary(self):
        return {
            "id":self.id,
            "start-x":self.start_x, 
            "start-y":self.start_y, 
            "end-x":self.end_x,
            "end-y":self.end_y, 
            "trigger-traffic-light-id":self.trigger_light_id
        }

TURN_ANGLE_ERROR = 10 # In degrees

class Turn:
    """
    Semicricle defined by a position of its centre,
    two angles, one defining the start of the semicricle (Counterclockwise),
    and a second angle defining the end of the semicircle.
    Finally two distances indicating the semicricle minor radius and
    major radius.
    """
    def __init__(self, specs):
        self.id = specs["id"]
        self.x = specs["x"]
        self.y = specs["y"]
        self.first_angle = math.radians(specs["first-angle"])
        self.second_angle = math.radians(specs["second-angle"])
        self.min_distance = specs["min-distance"]
        self.max_distance = specs["max-distance"]
        self.can_skip = specs["can-skip"]
    
    def get_json_dictionary(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "first-angle": math.degrees(self.first_angle),
            "second-angle": math.degrees(self.second_angle),
            "min-distance": self.min_distance,
            "max-distance": self.max_distance,
            "can-skip": self.can_skip
        }


class Spawn_Point:
    """
    Point defined by an x and y coordinate
    """
    def __init__(self, specs):
        self.id = specs["id"]
        self.x = specs["x"]
        self.y = specs["y"]
        self.direction = math.radians(specs["direction"])
        self.speed = specs["speed"] # Percentage over the maximum speed of the car (0, 1)
        self.probability_per_second = specs["probability-per-second"]
    
    def get_json_dictionary(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "direction": math.degrees(self.direction),
            "speed": self.speed,
            "probability-per-second": self.probability_per_second
        }

class Despawn_Line:
    def __init__(self, specs):
        self.id = specs["id"]
        self.start_x = specs["start-x"]
        self.start_y = specs["start-y"]
        self.end_x = specs["end-x"]
        self.end_y = specs["end-y"]
    
    def get_json_dictionary(self):
        return {
            "id": self.id,
            "start-x": self.start_x,
            "start-y": self.start_y,
            "end-x": self.end_x,
            "end-y": self.end_y
        }

class CollidingTurns(Exception):
    def __init__(self, querry, message = ""):
        if message == "":
            super().__init__(f"Several turns areas collided, ids: {querry}")
        else:
            super().__init__(f"Several turns areas collided, ids: {querry}, message:\n{message}")

class Traffic_Light: # Future implement also support traffic lights that work detecting if cars are coming
    """
    All traffic lights change in the following order:
    - Red
    - Green
    - Amber
    - Repeat
    """
    RED = 0
    AMBER = 1
    GREEN = 2
    def __init__(self, specs):
        self.id = specs["id"]
        self.x = specs["x"]
        self.y = specs["y"]

        # Base times
        self.time_red = specs["time-red"]
        self.time_amber = specs["time-amber"]
        self.time_green = specs["time-green"]

        # Default state
        default_color = specs["default-color"]
        if default_color == "red":
            self.color = self.RED

        elif default_color == "amber":
            self.color = self.AMBER
        
        elif default_color == "green":
            self.color = self.GREEN
        
        # Main timer
        self.time_passed_since_last_change = specs["default-time-in"] * 1000000000
    
    def get_json_dictionary(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "time-red": self.time_red,
            "time-amber": self.time_amber,
            "time-green": self.time_green,
            "default-time-in": self.time_passed_since_last_change / 1000000000,
            "default-color": ["red", "amber", "green"][self.color]
        }
    
    def tick(self, time_delta):
        self.time_passed_since_last_change += time_delta
        if self.color == self.RED and self.time_passed_since_last_change >= (self.time_red * 1000000000):

            # Change to green
            self.color = self.GREEN
            self.time_passed_since_last_change = 0
        
        elif self.color == self.GREEN and self.time_passed_since_last_change >= (self.time_green * 1000000000):

            # Change to amber
            self.color = self.AMBER
            self.time_passed_since_last_change = 0
        
        elif self.color == self.AMBER and self.time_passed_since_last_change >= (self.time_amber * 1000000000):

            # Change to red
            self.color = self.RED
            self.time_passed_since_last_change = 0

class Map:
    def __init__(self, name):

        # Basic map data
        self.name = name
        self.image_path = "images/maps/" + self.name + ".png"
        self.image = pygame.image.load(self.image_path)

        # Loading json map data
        try:
            self.json_path = "maps/" + self.name + ".json"
            with open(self.json_path, "r", encoding = "utf-8") as file:
                self.json = json.load(file)
        
        except Exception as e:
            pass
        
        # Mobility map data
        try:
            self.stops_specs = self.json.get("stops", [])
            self.stops = [Stop(specs) for specs in self.stops_specs]

        except Exception as e:
            self.stops = []
        
        try:
            self.traffic_lights_specs = self.json.get("traffic-lights", [])
            self.traffic_lights = [Traffic_Light(specs) for specs in self.traffic_lights_specs]
        
        except Exception as e:
            self.traffic_lights = []

        try:
            self.turns_specs = self.json.get("turns", [])
            self.turns = [Turn(specs) for specs in self.turns_specs]
        
        except Exception as e:
            self.turns = []
        
        try:
            self.spawns_specs = self.json.get("spawn-points", [])
            self.spawns = [Spawn_Point(specs) for specs in self.spawns_specs]
        
        except Exception as e:
            self.spawns = []
        
        try:
            self.despawns_specs = self.json.get("despawn-points", [])
            self.despawns = [Despawn_Line(specs) for specs in self.despawns_specs]
        
        except Exception as e:
            self.despawns = []
    
    # Function to find Traffic_Light instance by ID
    def _find_traffic_light_by_id(self, target_id):
        for traffic_light_instance in self.traffic_lights:
            if traffic_light_instance.id == target_id:
                return traffic_light_instance
        return None  # Return None if the ID is not found
    
    def able_to_cross(self, stop_id):
        stop_color = self._find_traffic_light_by_id(self.stops[stop_id].trigger_light_id).color

        if stop_color == Traffic_Light.GREEN:
            return True

        else:
            return False
    
    def stops_in_sight(self, vehicle):
        """Returns the ids of all stops in sigt"""

        stop_ids_in_sight = []

        for stop in self.stops:

            # Check if stop is in sight
            angle_point1 = math_utils.angle_point_to_point(vehicle.front_x, vehicle.front_y, stop.start_x, stop.start_y)
            angle_point2 = math_utils.angle_point_to_point(vehicle.front_x, vehicle.front_y, stop.end_x, stop.end_y)

            # Check if the direction angle is between the two angles to points
            if math_utils.angle_in_between(angle_point1, angle_point2, vehicle.direction):
                stop_ids_in_sight.append(stop.id)
        
        return stop_ids_in_sight

    def distance_to_stop(self, vehicle, stop_id):
        """Returns the distance in pixels to the stop id provided"""
        stop = self.stops[stop_id]
        return math_utils.distance_point_to_line(0, 0, stop.start_x - vehicle.front_x, vehicle.front_y - stop.start_y, stop.end_x - vehicle.front_x, vehicle.front_y - stop.end_y)
    
    def crossed_turns(self, vehicle):
        """Returns all turns the car is inside of"""

        crossed_turn_ids = []

        for turn in self.turns:

            # Calculate the distance to the turning point
            car_turn_distance = math_utils.distance_point_to_point(turn.x, turn.y, vehicle.x, vehicle.y)

            # Checking if its in the correct distance range
            if not (turn.min_distance <= car_turn_distance <= turn.max_distance):
                continue

            # Calculate the angle between the car and the turn point
            car_turn_angle = math_utils.angle_point_to_point(turn.x, turn.y, vehicle.x, vehicle.y)

            # Checking if the car is in the correct section of the semicircle
            if not math_utils.angle_in_between(angle = car_turn_angle, first_angle_forced=turn.second_angle, second_angle_forced=turn.first_angle):
                continue

            crossed_turn_ids.append(turn.id)

        return crossed_turn_ids

    def entry_turn(self, vehicle, turn_id, turning_direction, debug = False):
        """Checks if the vehicle is on any of the entry angles of the turn id"""

        turn = self.turns[turn_id]

        # Calculate the angle between the car and the turn point
        car_turn_angle = math_utils.angle_point_to_point(turn.x, turn.y, vehicle.x, vehicle.y)
        
        # Checking if the car is outside of the allowed angles, Bug if any of these distances is 0 it might cause issues
        distance_to_first_angle = math_utils.closest_angular_distance(turn.first_angle, car_turn_angle, turning_direction)
        distance_to_second_angle = math_utils.closest_angular_distance(turn.second_angle, car_turn_angle, turning_direction)

        # Calculate the turn span of the turn
        turn_span = math_utils.correct_radian(turn.second_angle - turn.first_angle)

        # Print debug information if requested
        if debug:
            print(f"Turn angle {car_turn_angle}, dist_first {distance_to_first_angle}, dist_second {distance_to_second_angle}, turning_direction {turning_direction}, first angle {turn.first_angle}, second angle {turn.second_angle}, turn span {turn_span}")

        # Checking if the angle is in the correct range
        if abs(distance_to_first_angle) > math.radians(TURN_ANGLE_ERROR) and abs(distance_to_second_angle) > math.radians(TURN_ANGLE_ERROR):
            return False
        
        # What follows here is a mess that nobody will ever understand - Pablo Rivero Lázaro
        if abs(distance_to_first_angle) <= math.radians(TURN_ANGLE_ERROR):
            
            if turning_direction == "Counterclockwise":

                # Inside the turn
                if abs(distance_to_second_angle) < turn_span:

                    if distance_to_first_angle < 0:
                        return True
                
                else:
                    if distance_to_first_angle > 0:
                        return True
            
            elif turning_direction == "Clockwise":

                # Inside the turn
                if abs(distance_to_second_angle) < turn_span:

                    if distance_to_first_angle > 0:
                        return True
                
                else:
                    if distance_to_first_angle < 0:
                        return True
        
        if abs(distance_to_second_angle) <= math.radians(TURN_ANGLE_ERROR):

            if turning_direction == "Clockwise":

                # Inside the turn
                if abs(distance_to_first_angle) < turn_span:

                    if distance_to_second_angle < 0:
                        return True
                    
                else:
                    if distance_to_second_angle > 0:
                        return True
            
            elif turning_direction == "Counterclockwise":

                # Inside the turn
                if abs(distance_to_first_angle) < turn_span:

                    if distance_to_second_angle > 0:
                        return True
                    
                else:
                    if distance_to_second_angle < 0:
                        return True

        return False
    
    def spawns_this_execution(self, time_delta):
        """Returns a list of the spawns that requested to spawn on this iteration based on probability"""
        spawns_ids = []

        for spawn in self.spawns:

            # Calculate the probability of spawning based on time_delta
            spawn_probability = spawn.probability_per_second * (time_delta / 1000000000)
            
            # Check if the spawn should occur based on a random number and probability
            if random.random() < spawn_probability:
                spawns_ids.append(spawn.id)

        return spawns_ids
    
    def tick(self, time_delta):

        # Do tick for all traffic lights
        for traffic_light in self.traffic_lights:
            traffic_light.tick(time_delta)
        
    def render(self, screen):

        # Show image of the map on the screen
        screen.blit(self.image, (0, 0))

        # Draw temporal stop lines
        for stop in self.stops:
            stop_color = self._find_traffic_light_by_id(self.stops[stop.id].trigger_light_id).color
            if stop_color == Traffic_Light.RED:
                color = (255, 0, 0)
            
            elif stop_color == Traffic_Light.AMBER:
                color = (255, 191, 0)
            
            elif stop_color == Traffic_Light.GREEN:
                color = (0, 255, 0)
            pygame.draw.line(screen, color, (stop.start_x, stop.start_y), (stop.end_x, stop.end_y), 2)
        
        # Draw temporal turning points
        for turn in self.turns:
            rect = pygame.Rect(turn.x - turn.max_distance, turn.y - turn.max_distance,
                                2 * turn.max_distance, 2 * turn.max_distance)
            pygame.draw.arc(screen, (0, 0, 255), rect, turn.first_angle, turn.second_angle, 2)

            rect = pygame.Rect(turn.x - turn.min_distance, turn.y - turn.min_distance,
                                2 * turn.min_distance, 2 * turn.min_distance)
            pygame.draw.arc(screen, (0, 0, 255), rect, turn.first_angle, turn.second_angle, 2)
            
            inner_start = math_utils.get_point_on_circle(turn.x, turn.y, turn.min_distance, turn.first_angle)
            outer_start = math_utils.get_point_on_circle(turn.x, turn.y, turn.max_distance, turn.first_angle)
            pygame.draw.line(screen, (0, 0, 255), outer_start, inner_start, 2)

            inner_end = math_utils.get_point_on_circle(turn.x, turn.y, turn.min_distance, turn.second_angle)
            outer_end = math_utils.get_point_on_circle(turn.x, turn.y, turn.max_distance, turn.second_angle)
            pygame.draw.line(screen, (0, 0, 255), outer_end, inner_end, 2)
        
        # Draw spawn points
        for spawn in self.spawns:
            pygame.draw.circle(screen, (0, 0, 0), (spawn.x, spawn.y), 1)
        
        # Draw despawn points
        for despawn in self.despawns:
            pygame.draw.line(screen, (0, 0, 0), (despawn.start_x, despawn.start_y), (despawn.end_x, despawn.end_y), 1)