"""
Originally designed by pasblo
GNU GENERAL PUBLIC LICENSE
"""

import pygame
import json
import time
import math
import math_utils
import random

class Stop:
    """
    Class representing a stop line defined by a start point and an end point.
    """
    def __init__(self, specs):
        """
        Initializes a Stop object.

        Args:
            specs (dict): A dictionary containing specifications for the Stop.

        Returns:
            None
        """
        self.id = specs["id"]
        self.start_x = specs["start-x"]
        self.start_y = specs["start-y"]
        self.end_x = specs["end-x"]
        self.end_y = specs["end-y"]
        self.trigger_light_id = specs["trigger-traffic-light-id"]
    
    def get_json_dictionary(self):
        """
        Returns a dictionary representing the Stop object in JSON format.

        Args:
            None

        Returns:
            dict: A dictionary containing the attributes of the Stop object.
        """
        return {
            "id": self.id,
            "start-x": self.start_x, 
            "start-y": self.start_y, 
            "end-x": self.end_x,
            "end-y": self.end_y, 
            "trigger-traffic-light-id": self.trigger_light_id
        }

TURN_ANGLE_ERROR = 44 # In degrees

class Turn:
    """
    Class representing a semicircle defined by the position of its center,
    two angles (start and end of the semicircle),
    and two distances indicating the semicircle's minor and major radius.
    """
    def __init__(self, specs):
        """
        Initializes a Turn object.

        Args:
            specs (dict): A dictionary containing specifications for the Turn.

        Returns:
            None
        """
        self.id = specs["id"]
        self.x = specs["x"]
        self.y = specs["y"]
        self.first_angle = math.radians(specs["first-angle"])
        self.second_angle = math.radians(specs["second-angle"])
        self.min_distance = specs["min-distance"]
        self.max_distance = specs["max-distance"]
        self.can_skip = specs["can-skip"]
    
    def get_json_dictionary(self):
        """
        Returns a dictionary representing the Turn object in JSON format.

        Args:
            None

        Returns:
            dict: A dictionary containing the attributes of the Turn object.
        """
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
    Class representing a spawn point defined by an x and y coordinate.
    """
    def __init__(self, specs):
        """
        Initializes a SpawnPoint object.

        Args:
            specs (dict): A dictionary containing specifications for the SpawnPoint.

        Returns:
            None
        """
        self.id = specs["id"]
        self.x = specs["x"]
        self.y = specs["y"]
        self.direction = math.radians(specs["direction"])
        self.speed = specs["speed"]  # Percentage over the maximum speed of the car (0, 1)
        self.probability_per_second = specs["probability-per-second"]
    
    def get_json_dictionary(self):
        """
        Returns a dictionary representing the SpawnPoint object in JSON format.

        Args:
            None

        Returns:
            dict: A dictionary containing the attributes of the SpawnPoint object.
        """
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "direction": math.degrees(self.direction),
            "speed": self.speed,
            "probability-per-second": self.probability_per_second
        }

class Despawn_Line:
    """
    Class representing a line defined by a start point and an end point for despawning vehicles.
    """
    def __init__(self, specs):
        """
        Initializes a DespawnLine object.

        Args:
            specs (dict): A dictionary containing specifications for the DespawnLine.

        Returns:
            None
        """
        self.id = specs["id"]
        self.start_x = specs["start-x"]
        self.start_y = specs["start-y"]
        self.end_x = specs["end-x"]
        self.end_y = specs["end-y"]
    
    def get_json_dictionary(self):
        """
        Returns a dictionary representing the DespawnLine object in JSON format.

        Args:
            None

        Returns:
            dict: A dictionary containing the attributes of the DespawnLine object.
        """
        return {
            "id": self.id,
            "start-x": self.start_x,
            "start-y": self.start_y,
            "end-x": self.end_x,
            "end-y": self.end_y
        }

class CollidingTurns(Exception):
    """
    Exception raised when multiple turns areas collide.

    Attributes:
    - querry: List of turn IDs that collided.
    - message: Additional error message.
    """

    def __init__(self, querry, message=""):
        """
        Initialize the exception.

        Parameters:
        - querry: List of turn IDs that collided.
        - message: Additional error message.
        """
        if message == "":
            super().__init__(f"Several turns areas collided, ids: {querry}")
        else:
            super().__init__(f"Several turns areas collided, ids: {querry}, message:\n{message}")

class Traffic_Light:
    """
    Class representing a traffic light that changes in the order: Red, Amber, Green, Repeat.
    """
    RED = 0
    AMBER = 1
    GREEN = 2

    def __init__(self, specs):
        """
        Initializes a TrafficLight object.

        Args:
            specs (dict): A dictionary containing specifications for the TrafficLight.

        Returns:
            None
        """
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
        """
        Returns a dictionary representing the TrafficLight object in JSON format.

        Args:
            None

        Returns:
            dict: A dictionary containing the attributes of the TrafficLight object.
        """
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
        """
        Updates the state of the TrafficLight based on the time passed.

        Args:
            time_delta (float): The time passed since the last update.

        Returns:
            None
        """
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
        """
        Initialize a Map instance with basic map data and load mobility map data from JSON.

        Parameters:
        - name: The name of the map.
        """
        # Basic map data
        self.name = name
        self.image_path = "images/maps/" + self.name + ".png"
        self.image = pygame.image.load(self.image_path)

        # Loading JSON map data
        try:
            self.json_path = "maps/" + self.name + ".json"
            with open(self.json_path, "r", encoding="utf-8") as file:
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

    # ==============================================================
    # SECTION: Internal functions
    # Description: Internal utility functions for managing the
    # vehicle's state and calculations.
    # ==============================================================

    def _find_traffic_light_by_id(self, target_id):
        """
        Finds a TrafficLight instance in the map by its ID.

        Args:
            target_id (int): The ID of the traffic light to find.

        Returns:
            TrafficLight or None: The TrafficLight instance if found, None otherwise.
        """
        for traffic_light_instance in self.traffic_lights:
            if traffic_light_instance.id == target_id:
                return traffic_light_instance
        return None  # Return None if the ID is not found

    # ==============================================================
    # SECTION: Interact functions
    # Description: Functions that interact with the map
    # ==============================================================

    def spawns_this_execution(self, time_delta):
        """
        Returns a list of spawn points that requested to spawn on this iteration based on probability.

        Parameters:
        - time_delta (float): The time passed since the last iteration in nanoseconds.

        Returns:
        - List[int]: A list of spawn point IDs that should spawn based on probability.
        """
        spawns_ids = []

        for spawn in self.spawns:

            # Calculate the probability of spawning based on time_delta
            spawn_probability = spawn.probability_per_second * (time_delta / 1000000000)
            
            # Check if the spawn should occur based on a random number and probability
            if random.random() < spawn_probability:
                spawns_ids.append(spawn.id)

        return spawns_ids
    
    def tick(self, time_delta):
        """
        Update the state of all traffic lights by progressing their internal timers.

        Parameters:
        - time_delta (float): The time passed since the last iteration in nanoseconds.
        """
        # Update the state of all traffic lights
        for traffic_light in self.traffic_lights:
            traffic_light.tick(time_delta)

    def render(self, screen):
        """
        Render the map on the screen by displaying the map image and drawing various elements.

        Parameters:
        - screen: The Pygame screen to render the map on.
        """
        # Show the image of the map on the screen
        screen.blit(self.image, (0, 0))

        # Draw temporal stop lines
        for stop in self.stops:
            stop_color = self._find_traffic_light_by_id(stop.trigger_light_id).color
            if stop_color == Traffic_Light.RED:
                color = (255, 0, 0)
            elif stop_color == Traffic_Light.AMBER:
                color = (255, 191, 0)
            elif stop_color == Traffic_Light.GREEN:
                color = (0, 255, 0)
            pygame.draw.line(screen, color, (stop.start_x, stop.start_y), (stop.end_x, stop.end_y), 2)

        # Draw temporal turning points
        for turn in self.turns:
            # Draw outer and inner arcs
            rect_outer = pygame.Rect(turn.x - turn.max_distance, turn.y - turn.max_distance,
                                    2 * turn.max_distance, 2 * turn.max_distance)
            pygame.draw.arc(screen, (0, 0, 255), rect_outer, turn.first_angle, turn.second_angle, 2)

            rect_inner = pygame.Rect(turn.x - turn.min_distance, turn.y - turn.min_distance,
                                    2 * turn.min_distance, 2 * turn.min_distance)
            pygame.draw.arc(screen, (0, 0, 255), rect_inner, turn.first_angle, turn.second_angle, 2)

            # Draw lines connecting arcs
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

    # ==============================================================
    # SECTION: Observe functions
    # Description: Functions that check something on the map
    # ==============================================================

    def able_to_cross(self, stop_id):
        """
        Checks if a vehicle is allowed to cross a stop based on the traffic light's color.

        Args:
            stop_id (int): The ID of the stop to check.

        Returns:
            bool: True if the traffic light is green, False otherwise.
        """
        stop_color = self._find_traffic_light_by_id(self.stops[stop_id].trigger_light_id).color

        return stop_color == Traffic_Light.GREEN

    def stops_in_sight(self, vehicle):
        """
        Returns the IDs of all stops in the line of sight of a given vehicle.

        Args:
            vehicle (Vehicle): The vehicle for which stops in sight are checked.

        Returns:
            list: A list of stop IDs that are in the line of sight of the vehicle.
        """
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
        """
        Returns the distance in pixels from the front of a vehicle to a specified stop.

        Args:
            vehicle (Vehicle): The vehicle for which the distance is measured.
            stop_id (int): The ID of the stop.

        Returns:
            float: The distance in pixels from the front of the vehicle to the specified stop.
        """
        stop = self.stops[stop_id]
        return math_utils.distance_point_to_line(
            0, 0,
            stop.start_x - vehicle.front_x, vehicle.front_y - stop.start_y,
            stop.end_x - vehicle.front_x, vehicle.front_y - stop.end_y
        )

    def crossed_turns(self, vehicle):
        """
        Returns a list of turn IDs that the car is inside of based on its position and direction.

        Args:
            vehicle (Vehicle): The vehicle for which to check the crossed turns.

        Returns:
            list: A list of turn IDs that the vehicle is currently inside of.
        """
        crossed_turn_ids = []

        for turn in self.turns:
            # Calculate the distance to the turning point
            car_turn_distance = math_utils.distance_point_to_point(turn.x, turn.y, vehicle.x, vehicle.y)

            # Checking if it's in the correct distance range
            if not (turn.min_distance <= car_turn_distance <= turn.max_distance):
                continue

            # Calculate the angle between the car and the turn point
            car_turn_angle = math_utils.angle_point_to_point(turn.x, turn.y, vehicle.x, vehicle.y)

            # Checking if the car is in the correct section of the semicircle
            if not math_utils.angle_in_between(angle=car_turn_angle, first_angle_forced=turn.second_angle, second_angle_forced=turn.first_angle):
                continue

            crossed_turn_ids.append(turn.id)

        return crossed_turn_ids

    def entry_turn(self, vehicle, turn_id, turning_direction, debug=False):
        """
        Checks if the vehicle is on any of the entry angles of the specified turn.

        Args:
            vehicle (Vehicle): The vehicle for which to check the entry angle.
            turn_id (int): The ID of the turn to check.
            turning_direction (str): The turning direction, either "Counterclockwise" or "Clockwise".
            debug (bool): If True, print debug information.

        Returns:
            bool: True if the vehicle is on the entry angle of the turn, False otherwise.
        """
        turn = self.turns[turn_id]

        # Calculate the angle between the car and the turn point
        car_turn_angle = math_utils.angle_point_to_point(turn.x, turn.y, vehicle.x, vehicle.y)

        # Checking if the car is outside of the allowed angles; bug if any of these distances is 0 it might cause issues
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
    