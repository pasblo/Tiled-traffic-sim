"""
Originally designed by pasblo
GNU GENERAL PUBLIC LICENSE
"""

import Vehicle
import random
import pygame

going_to_break = True
going_to_turn = True

def move_vehicles(vehicle_list, map, time_delta, set_vehicle):
    """
    Autonomously move vehicles, handling turning and stopping as necessary.

    CAUTION:
    * Assumes no concatenated turns.

    Args:
        vehicle_list (list): List of vehicle objects.
        map: Map object representing the environment.
        time_delta (float): Time passed since the last update.
        set_vehicle (int): The ID of the vehicle for which debugging information is printed.
    """

    # Iterate through all vehicles
    for vehicle in vehicle_list:

        # Check for colliding turns
        last_turn = vehicle.turning
        vehicle.turning = False
        last_turn_id = vehicle.turning_turn_id
        started_turning = False
        ended_turning = False
        new_turn = False
        detected_turns_ids = map.crossed_turns(vehicle)

        entered_turns = []
        skippable_turns = []

        # Check if the vehicle exited the turn it was navigating
        if not last_turn_id in detected_turns_ids and len(detected_turns_ids) != 0:

            # Filter turns that the vehicle has just entered
            for turn_id in detected_turns_ids:
                if vehicle.detect_entering_in_turn(map, turn_id, debug=(vehicle.id == set_vehicle)):
                    entered_turns.append(turn_id)

            # Decide whether to turn or not and which turn to use
            if len(entered_turns) != 0:

                # Decide if the vehicle turns or not
                skip_turn = random.randint(0, 1)

                # Check for skippable turns
                skippable_turns = [turn_id for turn_id in entered_turns if map.turns[turn_id].can_skip == "True"]
                if len(skippable_turns) != 0 and skip_turn == 1:
                    vehicle.skippingturn = True

                # Select which turn to use if multiple options exist
                vehicle.select_turn(random.choice(entered_turns))

        # Detect start turning and end turning flags
        if len(detected_turns_ids) != 0 and (len(entered_turns) != 0 or last_turn_id in detected_turns_ids) and going_to_turn:

            new_turn = True

            # Just started turning
            if not last_turn:
                started_turning = True

        else:

            # Just finished turning
            if last_turn:
                ended_turning = True

        # Debug
        if vehicle.id == set_vehicle:
            print(f"Vehicle {vehicle.id} last turning: {last_turn}, detected turns {detected_turns_ids}, entered_turns {entered_turns}, skippable turns {skippable_turns}, chosen turn {vehicle.turning_turn_id}, started turning {started_turning}, ended turning {ended_turning}, skipped turning {vehicle.skippingturn}")

        # Rotate function
        if (new_turn or ended_turning) and not vehicle.skippingturn:
            vehicle.turn_around_map_turn(map, time_delta, started_turning, ended_turning)

        # Keep it turning to avoid end-of-turn bug
        elif vehicle.skippingturn and not ended_turning:
            vehicle.turning = True

        # Reset the skipping turn state after not detecting any turns
        if len(detected_turns_ids) == 0:
            vehicle.skippingturn = False

        # Check for brakes, avoid braking while turning
        if vehicle.detect_break_line(map) and going_to_break and ((not new_turn and not ended_turning) or vehicle.skippingturn):
            vehicle.brake(time_delta)

        # Increase acceleration
        vehicle.accelerate(time_delta)

        # Move the vehicle
        vehicle.move(time_delta)

def check_collisions(vehicle_list):
    for vehicle in vehicle_list:
        vehicle.update_vehicle_collisions(vehicle_list)
    
def render_vehicles(vehicle_list, screen, map, set_vehicle):
    """
    Display all vehicles on the screen along with their debugging information.

    Args:
        vehicle_list (list): List of vehicle objects.
        screen: The Pygame display surface.
        map: Map object representing the environment.
        set_vehicle (int): The ID of the vehicle for which debugging information is displayed.
    """
    for vehicle in vehicle_list:
        vehicle.render(screen, map, debug=(set_vehicle == vehicle.id))
        if set_vehicle == vehicle.id:
            pygame.draw.rect(screen, (0, 255, 0), vehicle.rotated_rect, 2)

def spawn_vehicles(map, time_delta, latest_vehicle_id):
    """
    Add new vehicles to the map following the probabilities of spawning for each spawn point.

    Args:
        map: Map object representing the environment.
        time_delta: Time elapsed since the last frame.
        latest_vehicle_id (int): The ID of the latest spawned vehicle.

    Returns:
        dict: A dictionary containing the list of new vehicles and the updated latest vehicle ID.
    """
    new_vehicles = []

    # Getting the list of spawn points that will spawn vehicles in this execution
    spawns_ids = map.spawns_this_execution(time_delta)

    for spawn_id in spawns_ids:
        spawn = map.spawns[spawn_id]
        vehicle_type_random = random.random()

        for vehicle in Vehicle.VEHICLES:
            
            # Check if this vehicle should spawn
            if vehicle_type_random <= vehicle["Spawning-rate"]:
                vehicle_speed = vehicle["Max-speed"] * spawn.speed  # The spawn speed is a percentage of the max speed
                new_vehicle = Vehicle.Vehicle(vehicle, {"id": latest_vehicle_id, "x": spawn.x, "y": spawn.y, "direction": spawn.direction, "speed": vehicle_speed})
                new_vehicles.append(new_vehicle)
                latest_vehicle_id += 1
                break
    
    return {"vehicles": new_vehicles, "new_id": latest_vehicle_id}
    
def despawn_vehicles(map, vehicles_list):
    """
    Remove vehicles from the map if they are in contact with a despawn line.

    Args:
        map: Map object representing the environment.
        vehicles_list (list): List of Vehicle objects.

    Returns:
        list: Updated list of vehicles after despawning.
    """

    new_vehicles_list = []

    # To-Do: Optimize to only check for despawn points on tiles the vehicle is in

    for vehicle in vehicles_list:
        vehicle_collides = False

        for despawn in map.despawns:
            # Checking if the vehicle is colliding with any despawn line
            if vehicle.colliding_with_line(despawn.start_x, despawn.start_y, despawn.end_x, despawn.end_y):
                vehicle_collides = True

        if not vehicle_collides:
            new_vehicles_list.append(vehicle)

    return new_vehicles_list
