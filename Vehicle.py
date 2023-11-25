"""
Originally designed by pasblo
MIT License
"""

import pygame
import math
import Map
import math_utils
import random

"""
- Name of the vehicle
- Speed in Km/h
- Acceleration in m/s^2 (https://www.translatorscafe.com/unit-converter/en-US/acceleration/2-33/meter/second%C2%B2-seconds)
- Brake deceleration in m/s^2
- Size in m
- Spawning rate in percentage each time a vehicle needs to spawn, the total should be 1, increasing
"""
SUV = {"Name":"SUV", "Max-speed":120, "Acceleration":3.9, "Brake-deceleration":340, "Size":4.4, "Spawning-rate":0.6}
TRUCK = {"Name":"Truck", "Max-speed":60, "Acceleration":3.9, "Brake-deceleration":340, "Size":6, "Spawning-rate":0.7}
BUS = {"Name":"Bus", "Max-speed":60, "Acceleration":3.9, "Brake-deceleration":340, "Size":6, "Spawning-rate":0.8}
BIKE = {"Name":"Bike", "Max-speed":80, "Acceleration":3.9, "Brake-deceleration":340, "Size":1.5, "Spawning-rate":1}

VEHICLES = [SUV, TRUCK, BUS, BIKE]

"""
Vehicle image and sizing
The long side is the x length, the short side is y length.
0º direction means going to the right, 90º direction means going up
    =o==x==o=
    y       >
    =o=====o=
"""

"""
All sizes and positions are in pixels
"""

DISTANCE_TO_STOP = 1 # Distance in meters to a stop where the vehicle will decide to stop or advance

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, type_of_vehicle, starting_state):

        super().__init__()

        # Basic vehicle data
        self.id = starting_state["id"]
        self.name = type_of_vehicle["Name"]
        self.max_speed = type_of_vehicle["Max-speed"] * 1000 / 3600 # In m/s
        self.acceleration = type_of_vehicle["Acceleration"] # In m/s^2
        self.brake_deceleration = type_of_vehicle["Brake-deceleration"] # In m/s^2
        self.real_size = type_of_vehicle["Size"] # In m
        self.image_path = "images/vehicles/" + self.name + ".png"
        self.image = pygame.image.load(self.image_path)

        self.resize_factor = self.real_size / math_utils.pixels_to_meters(self.image.get_rect().width)
        
        # Vehicle size
        self.size_x = self.image.get_rect().width * self.resize_factor # Pixels
        self.size_y = self.image.get_rect().height * self.resize_factor # Pixels

        # Position data
        self.x = starting_state["x"]
        self.y = starting_state["y"]
        self.direction = starting_state["direction"] # In radians
        self.speed = starting_state["speed"]
        self._calculate_front_position()
        self._rotate_image()

        # Status data
        self.braking = False
        self.turning = False
        self.skippingturn = False

        # Map information
        self.closest_stop_id = -1
        self.closest_stop_distance = -1 # In meters
        self.closest_turn_distance = -1 # In pixels

        # Turning information
        self.tangential_vector = (0, 0)
        self.turning_direction = 0 # "Clockwise, Counterclockwise, Tangential"
        self.turning_turn_id = -1 # Turn if of the selected turn to turn around

        # Turning alignment corrections
        self.turn_enter_direction = None
        self.turn_enter_angle = -1 # In radians
        self.turn_enter_distance = -1 # In pixels
        self.turn_angle_error = -1
        self.turn_distance_error = -1

        # Temporal variables
        self.font = pygame.font.Font(None, 36)
    
    def __str__(self):
        """Used to print the instance vehicle"""
        return f"{self.name}"
        
    def calculate_direction_vector(self):
        """Returns the direction vector of this vehicle"""
        return (math.cos(self.direction), math.cos(self.direction))

    def _calculate_front_position(self):
        """Calculates the front point of this vehicle, used for collision avoidance"""

        # Calculate the displacement along x and y axes due to width
        self.front_x = self.x + self.size_x * 0.5 * math.cos(self.direction)
        self.front_y = self.y - self.size_x * 0.5 * math.sin(self.direction) # Minus here for only fourth quadrant
    
    def _rotate_image(self):
        scaled_image = pygame.transform.scale(self.image, (self.size_x, self.size_y))
        self.rotated_image = pygame.transform.rotate(scaled_image, math.degrees(math_utils.correct_radian(self.direction + math.pi)))
        self.rotated_rect = self.rotated_image.get_rect(center = (self.x, self.y))

    def render(self, screen, map, debug = False):

        # Render the vehicle image
        self._rotate_image()
        screen.blit(self.rotated_image, self.rotated_rect.topleft)

        # Render a point for the center front position
        pygame.draw.circle(screen, (0, 0, 255), (self.front_x, self.front_y), 1)

        # Render the speed
        """text_1 = self.font.render(str(self.speed), True, (0, 0, 0))  # Black color
        text_1_rect = text_1.get_rect()
        text_1_rect.topleft = (10, pygame.display.Info().current_h - text_1_rect.height - 10)  # Adjust the position here
        screen.blit(text_1, text_1_rect)

        # Render the closest stop distance
        text_2 = self.font.render(str(self.closest_stop_distance), True, (0, 0, 0))  # Black color
        text_2_rect = text_2.get_rect()
        text_2_rect.topleft = (10, pygame.display.Info().current_h - text_2_rect.height - 40)  # Adjust the position here
        screen.blit(text_2, text_2_rect)

        # Render the direction
        text_3 = self.font.render(str(self.turn_angle_error), True, (0, 0, 0))  # Black color
        text_3_rect = text_3.get_rect()
        text_3_rect.topleft = (10, pygame.display.Info().current_h - text_3_rect.height - 70)  # Adjust the position here
        screen.blit(text_3, text_3_rect)

        # Render the distance to turn point
        text_4 = self.font.render(str(math.degrees(self.direction)), True, (0, 0, 0))  # Black color
        text_4_rect = text_4.get_rect()
        text_4_rect.topleft = (10, pygame.display.Info().current_h - text_4_rect.height - 100)  # Adjust the position here
        screen.blit(text_4, text_4_rect)"""

        if debug and self.turning:
            turn = map.turns[self.turning_turn_id]
            if self.turning_direction == "Clockwise":
                color = (0, 0, 255)
            
            elif self.turning_direction == "Counterclockwise":
                color = (0, 255, 0)
            
            elif self.turning_direction == "Normal":
                color = (255, 0, 0)
            
            else:
                color = (0, 0, 0)

            # Render tangential line to turning point
            pygame.draw.line(screen, color, (self.x, self.y), (self.x + self.tangential_vector[0]*50, self.y - self.tangential_vector[1]*50), 2)

            # Render line to turning point
            pygame.draw.line(screen, color, (self.x, self.y), (turn.x, turn.y), 2)
    
    def braking_distance_to_speed(self, final_speed):
        return (final_speed ** 2 - self.speed ** 2) / (2 * -self.brake_deceleration)
    
    def detect_break_line(self, map):

        # Set braking to false
        self.braking = False

        # Update the distance and id of the closest stop
        self.update_stops(map)

        # Check if there is any stop in sight
        if self.closest_stop_id == -1:
            return False

        # Check if light is red
        if map.able_to_cross(self.closest_stop_id):
            return False
        
        # Check if moving towards stop
        if self.speed < 0:
            return False
        
        # Break so that the car stops right in front of the stop line, in a defined distance
        if self.braking_distance_to_speed(0) + DISTANCE_TO_STOP >= self.closest_stop_distance:
            return True
        
        return False
    
    def select_turn(self, turn_id):

        self.turning_turn_id = turn_id
    
    def detect_entering_in_turn(self, map, turn_id, debug = False):

        turn = map.turns[self.turning_turn_id]

        # Calculating the direction from the turning point to the vehicle
        turn_to_vehicle_direction = math_utils.angle_point_to_point(turn.x, turn.y, self.x, self.y)
        
        # Calculate turning direction
        self.turning_direction, self.tangential_vector = math_utils.movement_rotational_direction(turn_to_vehicle_direction, self.direction)

        #print(self.turning_direction)

        return map.entry_turn(self, turn_id, self.turning_direction, debug = debug)
    
    def turn_around_map_turn(self, map, time_delta, first_turning = False, last_turning = False):
        """
        CAUTION:
        * Only works if it enters through one side and exits the other
        * Only works properly if it enters through any of the turning entrances.
        """

        # Checking if it just finished turning
        if last_turning:
            if self.turning_turn_id != -1:

                # HERE to correct bulletpoint #1
                """
                It would be needed to detect what side entered and what side is going out
                change the new direction to perform the modification or not.
                """

                # HERE to correct buletpoint #2
                """
                Detect if it entered looking inwards or outwards, and if enetered looking out
                revert the conditionals
                """

                # Correct angling missalignment
                turn = map.turns[self.turning_turn_id]
                if self.turn_enter_direction == "Clockwise":
                    new_direction = math_utils.correct_radian(self.turn_enter_angle - (turn.first_angle - turn.second_angle))
                    self.turn_angle_error = math_utils.percentage_difference(self.direction, new_direction)
                    self.direction = new_direction
                
                else:
                    new_direction = math_utils.correct_radian(self.turn_enter_angle + (turn.first_angle - turn.second_angle))
                    self.turn_angle_error = math_utils.percentage_difference(self.direction, new_direction)
                    self.direction = new_direction

                # Correct distance missalignments
                new_position = math_utils.change_distance_without_angle_change(0, 0, self.x - turn.x, turn.y - self.y, self.turn_enter_distance)
                new_x = new_position[0] + turn.x
                new_y = turn.y - new_position[1]
                self.turn_distance_error = math_utils.percentage_difference(self.x + self.y, new_x + new_y)
                self.x = new_x
                self.y = new_y
                return True

        self.turning = True

        turn = map.turns[self.turning_turn_id]

        # Calculating the direction from the turning point to the vehicle
        turn_to_vehicle_direction = math_utils.angle_point_to_point(turn.x, turn.y, self.x, self.y)
        
        # Calculate turning direction
        self.turning_direction, self.tangential_vector = math_utils.movement_rotational_direction(turn_to_vehicle_direction, self.direction)

        # Started turning, save entry point
        if first_turning:
            self.turn_enter_angle = self.direction
            self.turn_enter_direction = self.turning_direction

        # Turn around the turning point automatically
        self.rotate_around_point(turn.x, turn.y, time_delta, self.turning_direction)

        # Started turning, save entry point
        if first_turning:
            self.turn_enter_distance = self.closest_turn_distance

        return True
    
    def colliding_with_line(self, start_x, start_y, end_x, end_y):
        """Detect collisions with a line"""
        
        # Making sure the length x is not 0, cause it won't count for collisions
        len_x = abs(end_x - start_x)
        if len_x == 0:
            len_x = 1
        
        # Making sure the length y is not 0, cause it won't count for collisions
        len_y = abs(end_y - start_y)
        if len_y == 0:
            len_y = 1

        line_rect = pygame.Rect(min(start_x, end_x), min(start_y, end_y),
                            len_x, len_y)

        return self.rotated_rect.colliderect(line_rect)
    
    def colliding_with_vehicle(self, vehicle):
        """Detect collisions with a vehicle, To-DO change for circle collisions"""

        return self.rotated_rect.colliderect(vehicle.rotated_rect)
    
    def accelerate(self, time_delta):
        if not self.braking:
            self.speed += self.acceleration * (time_delta / 1000000000)
            if self.speed > self.max_speed:
                self.speed = self.max_speed
    
    def brake(self, time_delta):
        self.braking = True
        self.speed -= self.brake_deceleration * (time_delta / 1000000000)
        if self.speed < 0.0:
            self.speed = 0
            return True
        return False

    def update_stops(self, map):

        # Calculate all stops in sight of this car
        stops_in_sight_ids = map.stops_in_sight(self)

        # Obtain the closest stop in sight
        self.closest_stop_id = -1
        self.closest_stop_distance = -1
        for stops_in_sight_id in stops_in_sight_ids:
            distance = math_utils.pixels_to_meters(map.distance_to_stop(self, stops_in_sight_id))
            if self.closest_stop_distance == -1:
                self.closest_stop_distance = distance
                self.closest_stop_id = stops_in_sight_id
            elif distance < self.closest_stop_distance:
                self.closest_stop_distance = distance
                self.closest_stop_id = stops_in_sight_id
    
    def set_speed(self, speed): # Overrides braking action
        self.speed = speed
    
    def set_direction(self, direction):
        self.direction = direction

    def move(self, time_delta):
        meters = self.speed * time_delta / 1000000000
        pixels = math_utils.meters_to_pixels(meters) # Meters to pixels to another function
        self.x += pixels * math.cos(self.direction)
        self.y -= pixels * math.sin(self.direction)
        self._calculate_front_position()

    def rotate(self, angular_speed, time_delta):
        self.direction += angular_speed * time_delta / 1000000000
        self.direction = math_utils.correct_radian(self.direction)
        self._calculate_front_position()
    
    def rotate_around_point(self, point_x, point_y, time_delta, direction): # Requires alignment after rotations
        """Rotates the car around a map point"""

        # Radius of the turning circle
        distance_pixels = math_utils.distance_point_to_point(point_x, point_y, self.x, self.y)
        distance = math_utils.pixels_to_meters(distance_pixels)

        # Saving the turn distance
        self.closest_turn_distance = distance_pixels

        # Angular speed in radians per second
        angular_speed = self.speed / distance

        # Fixing turning direction
        if direction == "Clockwise":
            angular_speed *= 1
        
        elif direction == "Counterclockwise":
            angular_speed *= -1
        
        elif direction == "Normal":
            angular_speed *= 0

        # Rotate
        self.rotate(angular_speed, time_delta)
