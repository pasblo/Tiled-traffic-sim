"""
Originally designed by pasblo
GNU GENERAL PUBLIC LICENSE
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
        """
        Initializes a new instance of the Vehicle class.

        Parameters:
            type_of_vehicle (dict): A dictionary containing information about the vehicle type.
            starting_state (dict): A dictionary containing initial state information for the vehicle.
        """
        # Call the superclass's __init__ method
        super().__init__()

        # Basic vehicle data
        self.id = starting_state["id"]
        self.name = type_of_vehicle["Name"]
        self.max_speed = type_of_vehicle["Max-speed"] * 1000 / 3600  # Convert max speed to m/s
        self.acceleration = type_of_vehicle["Acceleration"]  # In m/s^2
        self.brake_deceleration = type_of_vehicle["Brake-deceleration"]  # In m/s^2
        self.real_size = type_of_vehicle["Size"]  # In m
        self.image_path = "images/vehicles/" + self.name + ".png"
        self.image = pygame.image.load(self.image_path)

        # Calculate resize factor based on real size and image width
        self.resize_factor = self.real_size / math_utils.pixels_to_meters(self.image.get_rect().width)

        # Vehicle size in pixels
        self.size_x = self.image.get_rect().width * self.resize_factor # In pixels
        self.size_y = self.image.get_rect().height * self.resize_factor # In pixels

        # Position data
        self.x = starting_state["x"]
        self.y = starting_state["y"]
        self.direction = starting_state["direction"]  # In radians
        self.speed = starting_state["speed"]
        self._calculate_front_position()  # Calculate front position based on current state
        self._rotate_image()  # Rotate the image based on the current direction

        # Status data
        self.braking = False
        self.turning = False
        self.skippingturn = False

        # Map information
        self.closest_stop_id = -1
        self.closest_stop_distance = -1  # In meters
        self.closest_turn_distance = -1  # In pixels

        # Turning information
        self.tangential_vector = (0, 0)
        self.turning_direction = 0  # "Clockwise, Counterclockwise, Tangential"
        self.turning_turn_id = -1  # Turn id of the selected turn to turn around

        # Turning alignment corrections
        self.turn_enter_direction = None
        self.turn_enter_angle = -1  # In radians
        self.turn_enter_distance = -1  # In pixels
        self.turn_angle_error = -1
        self.turn_distance_error = -1

        # Temporal variables
        self.font = pygame.font.Font(None, 36)
    
    def __str__(self):
        """
        Returns a string representation of the vehicle instance.

        Returns:
            str: A string containing the name of the vehicle.
        """
        # Used to print the instance vehicle by returning its name
        return f"{self.name}"
    
    # ==============================================================
    # SECTION: Internal functions
    # Description: Internal utility functions for managing the
    # vehicle's state and calculations.
    # ==============================================================

    def _calculate_direction_vector(self):
        """
        Returns the direction vector of this vehicle.

        The direction vector is a 2D vector representing the direction in which
        the vehicle is pointing. It is computed using the cosine of the direction
        angle for the x-component and the sine of the direction angle for the
        y-component.

        Returns:
            Tuple[float, float]: A tuple representing the direction vector
                                (x-component, y-component).
        """
        return (math.cos(self.direction), math.sin(self.direction))

    def _calculate_front_position(self):
        """
        Calculates the front point of this vehicle, used for collision avoidance.

        The front point is computed by adjusting the vehicle's position based on its
        size and orientation, considering the width of the vehicle for accurate
        collision detection.

        The front position is calculated by adding half of the vehicle's width to the
        x-coordinate and subtracting half of the vehicle's width from the y-coordinate,
        considering the direction angle.

        Updates:
            self.front_x (float): x-coordinate of the front point.
            self.front_y (float): y-coordinate of the front point.

        Note:
            The subtraction for self.front_y is intentional for calculations in the
            fourth quadrant.

        """
        # Calculate the displacement along x and y axes due to width
        self.front_x = self.x + self.size_x * 0.5 * math.cos(self.direction)
        self.front_y = self.y - self.size_x * 0.5 * math.sin(self.direction)  # Minus here for only fourth quadrant
    
    def _rotate_image(self):
        """
        Rotates and scales the image and creates a rect.

        This function is responsible for transforming the vehicle's image to match
        its orientation and size. It performs scaling and rotation operations on the
        original image and creates a rotated image along with a corresponding rect.

        Steps:
            1. Scale the original image to the specified size.
            2. Rotate the scaled image based on the corrected direction angle.
            3. Create a rect for the rotated image centered at the current (x, y) position.

        Updates:
            self.rotated_image (pygame.Surface): Rotated and scaled image of the vehicle.
            self.rotated_rect (pygame.Rect): Rectangular bounding box for the rotated image.

        """
        # Step 1: Scale the original image to the specified size
        scaled_image = pygame.transform.scale(self.image, (self.size_x, self.size_y))

        # Step 2: Rotate the scaled image based on the corrected direction angle
        corrected_direction = math_utils.correct_radian(self.direction + math.pi)
        self.rotated_image = pygame.transform.rotate(scaled_image, math.degrees(corrected_direction))

        # Step 3: Create a rect for the rotated image centered at the current (x, y) position
        self.rotated_rect = self.rotated_image.get_rect(center=(self.x, self.y))

    # ==============================================================
    # SECTION: Braking functions
    # Description: Functions related to braking and speed control
    # of the vehicle.
    # ==============================================================

    def braking_distance_to_speed(self, final_speed):
        """
        Calculate how much distance is needed for reaching the intended speed.

        This function estimates the braking distance required for the vehicle to
        decelerate from its current speed to the specified final speed, assuming a
        constant brake deceleration.

        Parameters:
            final_speed (float): The intended final speed.

        Returns:
            float: The braking distance needed to reach the intended speed.

        Formula:
            The braking distance (d) is calculated using the formula:
            d = (final_speed^2 - self.speed^2) / (2 * -self.brake_deceleration)

        """
        # Calculate the braking distance using the provided formula
        braking_distance = (final_speed ** 2 - self.speed ** 2) / (2 * -self.brake_deceleration)

        return braking_distance
    
    def detect_break_line(self, map):
        """
        Detects if the vehicle needs to brake at a stop line.

        This function evaluates whether the vehicle should apply brakes based on
        the proximity to the closest stop, the status of the traffic light, the
        direction of movement, and the braking distance required to stop at the
        stop line.

        Parameters:
            map (Map): The map object containing information about stops and traffic lights.

        Returns:
            bool: True if braking is required, False otherwise.

        Steps:
            1. Set braking to False initially.
            2. Update the distance and id of the closest stop.
            3. Check if there is any stop in sight; if not, no need to brake.
            4. Check if the traffic light at the closest stop is red; if not, no need to brake.
            5. Check if the vehicle is moving towards the stop; if not, no need to brake.
            6. Calculate the braking distance required to stop in front of the stop line.
            7. If the calculated braking distance is greater than or equal to the distance
            to the closest stop line, return True (braking is needed).
            8. Otherwise, return False.

        """
        # Step 1: Set braking to False
        self.braking = False

        # Step 2: Update the distance and id of the closest stop
        self.update_stops(map)

        # Step 3: Check if there is any stop in sight
        if self.closest_stop_id == -1:
            return False

        # Step 4: Check if the light is red
        if map.able_to_cross(self.closest_stop_id):
            return False

        # Step 5: Check if moving towards the stop
        if self.speed < 0:
            return False

        # Step 6: Calculate the braking distance required to stop in front of the stop line
        braking_distance = self.braking_distance_to_speed(0) + DISTANCE_TO_STOP

        # Step 7: If the calculated braking distance is greater than or equal to the distance
        # to the closest stop line, return True (braking is needed)
        if braking_distance >= self.closest_stop_distance:
            return True

        # Step 8: Otherwise, return False
        return False

    def update_stops(self, map):
        """
        Updates information about stops in the vehicle's sight.

        Parameters:
            map (Map): The map object containing information about stops.

        Steps:
            1. Calculate all stops in the sight of the vehicle using map.stops_in_sight().
            2. Initialize variables for the closest stop's id and distance.
            3. Iterate through the stops in sight and calculate the distance to each stop.
            4. Update the closest stop information based on the calculated distances.

        Updates:
            self.closest_stop_id (int): The identifier of the closest stop in sight.
            self.closest_stop_distance (float): The distance to the closest stop in sight.
        """
        # Step 1: Calculate all stops in the sight of the vehicle using map.stops_in_sight()
        stops_in_sight_ids = map.stops_in_sight(self)

        # Step 2: Initialize variables for the closest stop's id and distance
        self.closest_stop_id = -1
        self.closest_stop_distance = -1

        # Step 3: Iterate through the stops in sight and calculate the distance to each stop
        for stops_in_sight_id in stops_in_sight_ids:
            distance = math_utils.pixels_to_meters(map.distance_to_stop(self, stops_in_sight_id))

            # Step 4: Update the closest stop information based on the calculated distances
            if self.closest_stop_distance == -1:
                self.closest_stop_distance = distance
                self.closest_stop_id = stops_in_sight_id
            elif distance < self.closest_stop_distance:
                self.closest_stop_distance = distance
                self.closest_stop_id = stops_in_sight_id

    # ==============================================================
    # SECTION: Turning functions
    # Description: Functions related to vehicle turning and
    # rotation around map points.
    # ==============================================================

    def select_turn(self, turn_id):
        """
        Selects a turn for the vehicle to navigate.

        This function sets the specified turn_id as the turning_turn_id attribute,
        indicating the selected turn for the vehicle to navigate.

        Parameters:
            turn_id (int): The identifier of the selected turn.

        Updates:
            self.turning_turn_id (int): The identifier of the selected turn.

        """
        # Set the specified turn_id as the turning_turn_id attribute
        self.turning_turn_id = turn_id
    
    def detect_entering_in_turn(self, map, turn_id, debug=False):
        """
        Detects if the vehicle is entering a specific turn.

        This function calculates the direction from the turning point to the vehicle,
        determines the turning direction, and then checks if the vehicle is entering
        the specified turn based on its movement and the provided turn_id.

        Parameters:
            map (Map): The map object containing information about turns.
            turn_id (int): The identifier of the turn to check.
            debug (bool): A flag indicating whether to print debug information (default is False).

        Returns:
            bool: True if the vehicle is entering the specified turn, False otherwise.

        Steps:
            1. Retrieve information about the selected turn using self.turning_turn_id.
            2. Calculate the direction from the turning point to the vehicle.
            3. Determine the turning direction and tangential vector based on the calculated direction.
            4. Check if the vehicle is entering the specified turn using map.entry_turn().
            5. Return the result of the entry_turn check.

        """
        # Step 1: Retrieve information about the selected turn using self.turning_turn_id
        turn = map.turns[self.turning_turn_id]

        # Step 2: Calculate the direction from the turning point to the vehicle
        turn_to_vehicle_direction = math_utils.angle_point_to_point(turn.x, turn.y, self.x, self.y)

        # Step 3: Determine the turning direction and tangential vector based on the calculated direction
        self.turning_direction, self.tangential_vector = math_utils.movement_rotational_direction(turn_to_vehicle_direction, self.direction)

        # Step 4: Check if the vehicle is entering the specified turn using map.entry_turn()
        result = map.entry_turn(self, turn_id, self.turning_direction, debug=debug)

        # Step 5: Return the result of the entry_turn check
        return result

    def turn_around_map_turn(self, map, time_delta, first_turning=False, last_turning=False):
        """
        Turns the vehicle around a specified map turn.

        CAUTION:
        * Only works if it enters through one side and exits the other
        * Only works properly if it enters through any of the turning entrances.

        Parameters:
            map (Map): The map object containing information about turns.
            time_delta (float): The time passed since the last update.
            first_turning (bool): True if the vehicle is starting to turn, False otherwise (default is False).
            last_turning (bool): True if the vehicle just finished turning, False otherwise (default is False).

        Returns:
            bool: True if the turning process is successful, False otherwise.

        Steps:
            1. Check if the vehicle just finished turning.
            2. If it finished turning, correct angling and distance missalignments.
            3. If it finished turning, return True.
            4. If it's starting to turn, calculate the direction from the turning point to the vehicle.
            5. Calculate the turning direction and tangential vector based on the calculated direction.
            6. If it's starting to turn, save the entry point (angle and direction).
            7. Rotate the vehicle around the turning point based on the turning direction.
            8. If it's starting to turn, save the entry point (distance).
            9. Return True.

        """
        # Step 1: Check if the vehicle just finished turning
        if last_turning:
            if self.turning_turn_id != -1:

                # Step 2: Correct angling and distance missalignments
                """
                It would be needed to detect what side entered and what side is going out
                change the new direction to perform the modification or not.
                """
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

        # Step 3: If it didn't finish turning, return True
        self.turning = True

        # Step 4: Calculate the direction from the turning point to the vehicle
        turn = map.turns[self.turning_turn_id]
        turn_to_vehicle_direction = math_utils.angle_point_to_point(turn.x, turn.y, self.x, self.y)

        # Step 5: Calculate the turning direction and tangential vector based on the calculated direction
        self.turning_direction, self.tangential_vector = math_utils.movement_rotational_direction(turn_to_vehicle_direction, self.direction)

        # Step 6: If it's starting to turn, save the entry point (angle and direction)
        if first_turning:
            self.turn_enter_angle = self.direction
            self.turn_enter_direction = self.turning_direction

        # Step 7: Rotate the vehicle around the turning point based on the turning direction
        self.rotate_around_point(turn.x, turn.y, time_delta, self.turning_direction)

        # Step 8: If it's starting to turn, save the entry point (distance)
        if first_turning:
            self.turn_enter_distance = self.closest_turn_distance

        # Step 9: Return True
        return True

    def rotate(self, angular_speed, time_delta):
        """
        Rotates the vehicle.

        Parameters:
            angular_speed (float): The angular speed in radians per second.
            time_delta (float): The time passed since the last update.

        Steps:
            1. Update the direction based on the angular speed and time_delta.
            2. Correct the direction angle to ensure it remains within the valid radian range.
            3. Recalculate the front position of the vehicle.

        Updates:
            self.direction (float): The updated direction angle of the vehicle.
        """
        # Step 1: Update the direction based on the angular speed and time_delta
        self.direction += angular_speed * time_delta / 1000000000
        
        # Step 2: Correct the direction angle to ensure it remains within the valid radian range
        self.direction = math_utils.correct_radian(self.direction)

        # Step 3: Recalculate the front position of the vehicle
        self._calculate_front_position()
    
    def rotate_around_point(self, point_x, point_y, time_delta, direction):
        """
        Rotates the vehicle around a specified point on the map.

        Parameters:
            point_x (float): The x-coordinate of the rotation point.
            point_y (float): The y-coordinate of the rotation point.
            time_delta (float): The time passed since the last update.
            direction (str): The direction of rotation ("Clockwise", "Counterclockwise", or "Normal").

        Steps:
            1. Calculate the distance between the vehicle and the rotation point in pixels and meters.
            2. Save the turn distance for future reference.
            3. Calculate the angular speed in radians per second based on the vehicle's speed and distance.
            4. Adjust the angular speed based on the specified rotation direction.
            5. Rotate the vehicle using the calculated angular speed and time_delta.

        Updates:
            self.closest_turn_distance (float): The saved turn distance for future reference.
            self.direction (float): The updated direction angle of the vehicle.
        """
        # Step 1: Calculate the distance between the vehicle and the rotation point in pixels and meters
        distance_pixels = math_utils.distance_point_to_point(point_x, point_y, self.x, self.y)
        distance = math_utils.pixels_to_meters(distance_pixels)

        # Step 2: Save the turn distance for future reference
        self.closest_turn_distance = distance_pixels

        # Step 3: Calculate the angular speed in radians per second based on the vehicle's speed and distance
        angular_speed = self.speed / distance

        # Step 4: Adjust the angular speed based on the specified rotation direction
        if direction == "Clockwise":
            angular_speed *= 1
        elif direction == "Counterclockwise":
            angular_speed *= -1
        elif direction == "Normal":
            angular_speed *= 0

        # Step 5: Rotate the vehicle using the calculated angular speed and time_delta
        self.rotate(angular_speed, time_delta)

    # ==============================================================
    # SECTION: Collisions functions
    # Description: Functions related to collision detection with
    # lines and other vehicles.
    # ==============================================================

    def colliding_with_line(self, start_x, start_y, end_x, end_y):
        """
        Detects collisions between the vehicle and a line.

        This function checks if the vehicle's rotated rectangle collides with the
        specified line defined by its start and end points.

        Parameters:
            start_x (float): x-coordinate of the start point of the line.
            start_y (float): y-coordinate of the start point of the line.
            end_x (float): x-coordinate of the end point of the line.
            end_y (float): y-coordinate of the end point of the line.

        Returns:
            bool: True if the vehicle collides with the line, False otherwise.

        Steps:
            1. Ensure the length x and length y are not 0, to avoid issues with collisions.
            2. Create a rectangle representing the line using pygame.Rect.
            3. Check for collisions between the vehicle's rotated rectangle and the line rectangle.
            4. Return the result of the collision check.

        """
        # Step 1: Ensure the length x and length y are not 0, to avoid issues with collisions
        len_x = abs(end_x - start_x)
        if len_x == 0:
            len_x = 1

        len_y = abs(end_y - start_y)
        if len_y == 0:
            len_y = 1

        # Step 2: Create a rectangle representing the line using pygame.Rect
        line_rect = pygame.Rect(min(start_x, end_x), min(start_y, end_y), len_x, len_y)

        # Step 3: Check for collisions between the vehicle's rotated rectangle and the line rectangle
        collision_result = self.rotated_rect.colliderect(line_rect)

        # Step 4: Return the result of the collision check
        return collision_result
    
    def colliding_with_vehicle(self, vehicle):
        """
        Detects collisions between the vehicle and another vehicle.

        This function checks if the distance between the centers of the two vehicles
        is less than the sum of their half heights, indicating a collision.

        Parameters:
            vehicle (Vehicle): The other vehicle to check for collision.

        Returns:
            bool: True if the vehicles collide, False otherwise.

        Steps:
            1. Calculate the distance between the centers of the two vehicles.
            2. Check if the distance minus the sum of their half heights is less than 0.
            3. Return the result of the collision check.

        """
        # Step 1: Calculate the distance between the centers of the two vehicles
        distance = math_utils.distance_point_to_point(self.x, self.y, vehicle.x, vehicle.y)

        # Step 2: Check if the distance minus the sum of their half heights is less than 0
        collision_result = (distance - self.size_y/2 - vehicle.size_y/2) < 0

        # Step 3: Return the result of the collision check
        return collision_result

    def update_vehicle_collisions(self, vehicles_list):
        """
        Update the list of vehicles with which the current vehicle is colliding.

        Args:
            vehicles_list (list): List of Vehicle objects.

        Returns:
            None
        """
        self.colliding_vehicles = []

        for vehicle in vehicles_list:
            if vehicle != self:
                if self.colliding_with_vehicle(vehicle):
                    self.colliding_vehicles.append(vehicle.id)

    # ==============================================================
    # SECTION: Moving functions
    # Description: Functions for moving the vehicle around the map.
    # ==============================================================

    def move(self, time_delta):
        """
        Moves the vehicle based on its speed and direction.

        Parameters:
            time_delta (float): The time passed since the last update.

        Steps:
            1. Calculate the distance traveled in meters based on the current speed and time_delta.
            2. Convert the distance from meters to pixels using math_utils.meters_to_pixels().
            3. Update the x and y coordinates based on the calculated distance and direction.
            4. Recalculate the front position of the vehicle.

        Updates:
            self.x (float): The updated x-coordinate of the vehicle.
            self.y (float): The updated y-coordinate of the vehicle.
        """
        # Step 1: Calculate the distance traveled in meters based on the current speed and time_delta
        meters = self.speed * time_delta / 1000000000
        
        # Step 2: Convert the distance from meters to pixels using math_utils.meters_to_pixels()
        pixels = math_utils.meters_to_pixels(meters)

        # Step 3: Update the x and y coordinates based on the calculated distance and direction
        self.x += pixels * math.cos(self.direction)
        self.y -= pixels * math.sin(self.direction)

        # Step 4: Recalculate the front position of the vehicle
        self._calculate_front_position()

    def render(self, screen, map, debug=False):
        """
        Draw the vehicle and any debugging information on the given screen.

        Parameters:
            screen: The Pygame screen surface to draw on.
            map: The map object containing information about turns and stops.
            debug (bool): Flag to enable/disable debugging information.

        Renders:
            - Rotated vehicle image.
            - Center front position point.
            - Debugging information if debug is True.
        """
        # Render the rotated vehicle image
        self._rotate_image()
        screen.blit(self.rotated_image, self.rotated_rect.topleft)

        # Render a point for the center front position
        pygame.draw.circle(screen, (0, 0, 255), (int(self.front_x), int(self.front_y)), 1)

        # Collision rendering
        if len(self.colliding_vehicles) > 0:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.size_y*2, 2)

        """
        # Render the speed
        text_1 = self.font.render(str(self.speed), True, (0, 0, 0))  # Black color
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
        screen.blit(text_4, text_4_rect)
        """

        # Debugging information for turning
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
            pygame.draw.line(screen, color, (int(self.x), int(self.y)),
                            (int(self.x + self.tangential_vector[0] * 50), int(self.y - self.tangential_vector[1] * 50)), 2)

            # Render line to turning point
            pygame.draw.line(screen, color, (int(self.x), int(self.y)), (int(turn.x), int(turn.y)), 2)
    
    def accelerate(self, time_delta):
        """
        Accelerates the vehicle.

        Parameters:
            time_delta (float): The time passed since the last update.

        Steps:
            1. Check if the vehicle is not currently braking.
            2. If not braking, increase the speed based on acceleration and time_delta.
            3. If the speed exceeds the maximum speed, set it to the maximum speed.

        Updates:
            self.speed (float): The updated speed of the vehicle.
        """
        # Step 1: Check if the vehicle is not currently braking
        if not self.braking:
            # Step 2: If not braking, increase the speed based on acceleration and time_delta
            self.speed += self.acceleration * (time_delta / 1000000000)
            
            # Step 3: If the speed exceeds the maximum speed, set it to the maximum speed
            if self.speed > self.max_speed:
                self.speed = self.max_speed
    
    def brake(self, time_delta):
        """
        Applies braking to the vehicle.

        Parameters:
            time_delta (float): The time passed since the last update.

        Steps:
            1. Set the braking flag to True.
            2. Decrease the speed based on brake_deceleration and time_delta.
            3. If the speed becomes negative, set it to 0 and return True (vehicle has come to a complete stop).
            4. Otherwise, return False.

        Updates:
            self.speed (float): The updated speed of the vehicle.
        Returns:
            bool: True if the vehicle has come to a complete stop, False otherwise.
        """
        # Step 1: Set the braking flag to True
        self.braking = True
        
        # Step 2: Decrease the speed based on brake_deceleration and time_delta
        self.speed -= self.brake_deceleration * (time_delta / 1000000000)
        
        # Step 3: If the speed becomes negative, set it to 0 and return True
        if self.speed < 0.0:
            self.speed = 0
            return True
        
        # Step 4: Otherwise, return False
        return False

    # ==============================================================
    # SECTION: State change functions
    # Description: Functions for updating and changing the state
    # of the vehicle.
    # ==============================================================

    def set_speed(self, speed):
        """
        Sets the speed of the vehicle, overriding any ongoing braking action.

        Parameters:
            speed (float): The new speed value to set.

        Updates:
            self.speed (float): The updated speed of the vehicle.
        """
        # Overrides any ongoing braking action by directly setting the new speed
        self.speed = speed
    
    def set_direction(self, direction):
        """
        Sets the direction of the vehicle.

        Parameters:
            direction (float): The new direction angle in radians.

        Updates:
            self.direction (float): The updated direction angle of the vehicle.
        """
        # Set the direction of the vehicle to the specified angle
        self.direction = direction
