"""
Originally designed by pasblo
GNU GENERAL PUBLIC LICENSE
All this meth is for pygame logic, with (0, 0) on the top left of the window
"""

import math

MAP_SCALE = 5 # x pixels = 1 meter

# ==============================================================
# SECTION: Map conversion functions
# Description: Functions to convert map measures to real measures
# ==============================================================

def pixels_to_meters(pixel):
    """Converts pixels to meters."""
    return pixel / MAP_SCALE
    
def meters_to_pixels(meters):
    """Converts meters to pixels."""
    return meters * MAP_SCALE

# ==============================================================
# SECTION: Angular functions
# Description: Functions relating angular operations and logic
# ==============================================================

def correct_degree(angle):
    """Ensures the angle is within 0 to 359 degrees."""
    return angle % 360

def correct_radian(angle):
    """Ensures the angle is within 0 to 2*pi radians."""
    return angle % (2 * math.pi)

def correct_signed_radian(angle):
    """Ensures the angle is within -2*pi to 2*pi radians."""
    if angle > 2 * math.pi:
        return angle - 2 * math.pi

    elif angle < -2 * math.pi:
        return angle + 2 * math.pi

    else:
        return angle

def ordered_angles(start_angle, end_angle, side = "small"):
    """Orders angles based on the specified side (small or big)."""
    first_angle = 0
    second_angle = 0

    # Checking what angle should we assign as first and second angle
    diff1 = correct_radian(start_angle - end_angle)
    diff2 = correct_radian(end_angle - start_angle)
    if diff1 >= diff2:
        if side == "small":
            second_angle = start_angle
            first_angle = end_angle

        elif side == "big":
            second_angle = end_angle
            first_angle = start_angle
    
    else:
        if side == "small":
            second_angle = end_angle
            first_angle = start_angle
        
        elif side == "big":
            second_angle = start_angle
            first_angle = end_angle
    
    return (first_angle, second_angle)

def angle_in_between(start_angle = 0, end_angle = 0, angle = 0, side = "small", first_angle_forced = None, second_angle_forced = None):
    """Checks if an angle is between two other angles."""
    if first_angle_forced != None and second_angle_forced != None:
        first_angle = first_angle_forced
        second_angle = second_angle_forced
    
    else:
        first_angle, second_angle = ordered_angles(start_angle, end_angle, side)

    # Check if the angle is between start_angle and end_angle in the clockwise direction
    if second_angle - first_angle <= 0:
        end = second_angle - first_angle + 2*math.pi
    else:
        end = second_angle - first_angle
    
    if angle - first_angle <= 0:
        angle = angle - first_angle + 2*math.pi
    
    else:
        angle = angle - first_angle
    
    return angle >= end

def angle_point_to_point(origin_x, origin_y, far_x, far_y):
    """Calculates the angle between two points."""
    return correct_radian(math.atan2(origin_y-far_y, far_x-origin_x))

def angle_between_vectors(angle, vector):
    """Calculates the angle between a given angle and a vector."""
    return math.atan2(vector[1], vector[0]) - angle

def closest_angular_distance(static_angle, moving_angle, turning_direction = "Clockwise"):
    """Returns a positive number if the moving angle is moving towards the static one, and negative number if moving away"""

    if turning_direction == "Clockwise":

        # Fixing 0 - 360 angle problem
        if static_angle == 2*math.pi and moving_angle != 2*math.pi:
            static_angle = 0

        # Finding the distance in radians
        diff = (moving_angle - static_angle)
        if diff > math.pi:
            diff -= 2*math.pi
        return diff

    elif turning_direction == "Counterclockwise":

        # Fixing 0 - 360 angle problem
        if static_angle == 0 and moving_angle != 0:
            static_angle = 2*math.pi
        
        # Finding the distance in radians
        diff = (static_angle - moving_angle)
        if diff > math.pi:
            diff -= 2*math.pi
        return diff

    else:
        return 0
    
# ==============================================================
# SECTION: Vector oprtations functions
# Description: Functions to operate with vectors
# ==============================================================

def dot_product(x1, y1, x2, y2):
    """Calculates the dot product of two vectors."""
    return x1 * x2 + y1 * y2

def cross_product(x1, y1, x2, y2):
    """Calculates the cross product of two vectors."""
    return x1 * x2 - y1 * y2

def scalar_multiply(scalar, x1, y1):
    """Multiplies a vector by a scalar."""
    return [scalar * x1, scalar * y1]

def vector_subtract(x1, y1, x2, y2):
    """Subtracts one vector from another."""
    return [x1 - x2, y1 - y2]

def calculate_tangential_component(v1, v2):
    """Calculates the tangential component of v2 with respect to v1."""

    # Calculate the dot product of v1 and v2
    dot_product_v1_v2 = dot_product(v1[0], v1[1], v2[0], v2[1])

    # Calculate the dot product of v1 and itself
    dot_product_v1_v1 = dot_product(v1[0], v1[1], v1[0], v1[1])

    # Calculate the scalar for the projection
    scalar = dot_product_v1_v2 / dot_product_v1_v1

    # Calculate the projection of v2 onto v1
    projection_v1_v2 = scalar_multiply(scalar, v1[0], v1[1])

    # Calculate the tangential component of v2
    tangential_component = vector_subtract(v2[0], v2[1], projection_v1_v2[0], projection_v1_v2[1])

    return tangential_component

def vector_from_direction_centered(angle):
    """Calculates a vector located in the origin that matches
    the direction provided as parameter"""
    return (math.cos(angle), math.sin(angle))

# ==============================================================
# SECTION: Distance functions
# Description: Functions to calculate distances between
# matematical objects.
# ==============================================================

def distance_point_to_line(point_x, point_y, line_x1, line_y1, line_x2, line_y2):
    """Calculate the CLOSEST distance between a point and a line"""
    numerator = abs((line_y2 - line_y1) * point_x - (line_x2 - line_x1) * point_y + line_x2 * line_y1 - line_y2 * line_x1)
    denominator = math.sqrt((line_y2 - line_y1)**2 + (line_x2 - line_x1)**2)
    distance = numerator / denominator
    return distance

def distance_point_to_segment(point_x, point_y, line_x1, line_y1, line_x2, line_y2):
    """Calculates the shortest distance from a point to a line segment defined
    by its start and end points in a two-dimensional space"""

    # Calculate coefficients A, B, C for the equation of the line
    A = line_y2 - line_y1
    B = line_x1 - line_x2

    # Check if the segment is a point
    if A == 0 and B == 0:
        return distance_point_to_point(point_x, point_y, line_x1, line_y1)

    # Check if the perpendicular projection of the point onto the line segment lies within the segment
    dot_product = (point_x - line_x1) * (line_x2 - line_x1) + (point_y - line_y1) * (line_y2 - line_y1)
    squared_length = (line_x2 - line_x1)**2 + (line_y2 - line_y1)**2

    # Calculate the parameter 't' for the projection onto the line segment
    t = max(0, min(1, dot_product / squared_length))

    # Calculate the coordinates of the perpendicular projection on the line segment
    projection_x = line_x1 + t * (line_x2 - line_x1)
    projection_y = line_y1 + t * (line_y2 - line_y1)

    # Calculate the distance from the point to the line segment
    distance_to_segment = math.sqrt((point_x - projection_x)**2 + (point_y - projection_y)**2)

    return distance_to_segment

def distance_point_to_point(point1_x, point1_y, point2_x, point2_y):
    """Calculate the distance between two points"""
    delta_x = point2_x - point1_x
    delta_y = point2_y - point1_y
    distance = math.sqrt(delta_x**2 + delta_y**2)
    return distance

# ==============================================================
# SECTION: Movement and rotation functions
# Description: Functions to calculate directions of movement
# ==============================================================

def movement_rotational_direction(point_to_object_direction, object_direction):
    """Determines the rotational direction of movement."""

    # Get vector direction to object
    vector_direction_to_object = vector_from_direction_centered(point_to_object_direction)

    # Get vector direction of object
    vector_direction_of_object = vector_from_direction_centered(object_direction)

    # Get tangential projection of direction of object to direction to object
    tangential_component = calculate_tangential_component(vector_direction_to_object, vector_direction_of_object)

    cross_product_result = 0

    # First local quadrant
    if 0 <= point_to_object_direction < math.pi/2:
        cross_product_result = cross_product(tangential_component[0], tangential_component[1], 0, 1)
    
    # Second local quadrant
    elif math.pi/2 <= point_to_object_direction < math.pi:
        cross_product_result = cross_product(tangential_component[0], tangential_component[1], 1, 0)
    
    # Third local quadrant
    elif math.pi <= point_to_object_direction < 3*math.pi/2:
        cross_product_result = cross_product(tangential_component[0], tangential_component[1], 0, -1)
    
    # Fourth local quadrant
    elif 3*math.pi/2 <= point_to_object_direction < 2*math.pi or point_to_object_direction == 0:
        cross_product_result = cross_product(tangential_component[0], tangential_component[1], -1, 0)
    
    #print("Vdto: " + str(vector_direction_to_object) + ", Cdoo: " + str(vector_direction_of_object))

    if cross_product_result > 0:
        return ("Counterclockwise", tangential_component)
    elif cross_product_result < 0:
        return ("Clockwise", tangential_component)
    else:
        return ("Normal", tangential_component)

def change_distance_without_angle_change(x1, y1, x2, y2, d_new):
    """Calculates a new coordinate for the second point to fix the
        distance between two points maintaining the direction"""

    # Calculate the initial distance
    d_initial = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # Calculate the scaling factor
    s = d_new / d_initial

    # Scale the vector (x2 - x1, y2 - y1)
    x2_new = x1 + s * (x2 - x1)
    y2_new = y1 + s * (y2 - y1)

    return x2_new, y2_new

def rotate_point(x, y, angle, direction = "Counterclockwise"): # Works properly
    """
    Helper function to rotate a point (x, y) around the origin.

    Parameters:
        x (float): x-coordinate of the point.
        y (float): y-coordinate of the point.
        angle (float): Angle of rotation in radians.
        direction (str): Direction of rotation, "clockwise" or "counterclockwise".
                        Default is "clockwise".

    Returns:
        tuple: Rotated coordinates (x_rotated, y_rotated).
    """
    if direction == "Clockwise":
        x_rotated = x * math.cos(angle) + y * math.sin(angle)
        y_rotated = -x * math.sin(angle) + y * math.cos(angle)
        
    elif direction == "Counterclockwise":
        x_rotated = x * math.cos(angle) - y * math.sin(angle)
        y_rotated = x * math.sin(angle) + y * math.cos(angle)
    
    else:
        x_rotated = -1
        y_rotated = -1

    return x_rotated, y_rotated

# ==============================================================
# SECTION: Location functions
# Description: Functions to obtain points in objects or lines
# ==============================================================

def get_point_on_circle(circle_x, circle_y, radius, angle):
    """Calculates a point in the radius of a circle"""
    x = circle_x + radius * math.cos(angle)
    y = circle_y - radius * math.sin(angle)
    return int(x), int(y)

def is_point_on_line(x, y, start_x, start_y, end_x, end_y):
    """Check if a point is on the line segment defined by two other points"""
    # Using cross product to determine if the point is on the line
    cross_product = (y - start_y) * (end_x - start_x) - (x - start_x) * (end_y - start_y)

    # All points on the line will have a cross product of 0
    return abs(cross_product) < 1e-10

def are_lines_intersecting(start1_x, start1_y, end1_x, end1_y, start2_x, start2_y, end2_x, end2_y):
    """Check if two line segments are intersecting"""

    # Using cross product to determine if the lines are intersecting
    cross_product1 = (end2_x - start2_x) * (start1_y - start2_y) - (end2_y - start2_y) * (start1_x - start2_x)
    cross_product2 = (end1_x - start1_x) * (start1_y - start2_y) - (end1_y - start1_y) * (start1_x - start2_x)
    cross_product3 = (end1_x - start1_x) * (end2_y - start2_y) - (end1_y - start1_y) * (end2_x - start2_x)

    # Lines are intersecting if cross products have different signs
    return cross_product1 * cross_product2 > 0 and cross_product1 * cross_product3 > 0

def find_intersection(seg1_start, seg1_end, seg2_start, seg2_end):
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0  # Collinear
        return 1 if val > 0 else 2  # Clockwise or counterclockwise

    def on_segment(p, q, r):
        return q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1])

    o1 = orientation(seg1_start, seg1_end, seg2_start)
    o2 = orientation(seg1_start, seg1_end, seg2_end)
    o3 = orientation(seg2_start, seg2_end, seg1_start)
    o4 = orientation(seg2_start, seg2_end, seg1_end)

    if o1 != o2 and o3 != o4:
        # Segments intersect
        return (
            ((seg1_start[0] * seg1_end[1] - seg1_start[1] * seg1_end[0]) * (seg2_start[0] - seg2_end[0]) -
             (seg1_start[0] - seg1_end[0]) * (seg2_start[0] * seg2_end[1] - seg2_start[1] * seg2_end[0])) /
            ((seg1_start[0] - seg1_end[0]) * (seg2_start[1] - seg2_end[1]) - (seg1_start[1] - seg1_end[1]) * (seg2_start[0] - seg2_end[0])),
            ((seg1_start[0] * seg1_end[1] - seg1_start[1] * seg1_end[0]) * (seg2_start[1] - seg2_end[1]) -
             (seg1_start[1] - seg1_end[1]) * (seg2_start[0] * seg2_end[1] - seg2_start[1] * seg2_end[0])) /
            ((seg1_start[0] - seg1_end[0]) * (seg2_start[1] - seg2_end[1]) - (seg1_start[1] - seg1_end[1]) * (seg2_start[0] - seg2_end[0]))
        )
    elif o1 == 0 and on_segment(seg1_start, seg2_start, seg1_end):
        # Segments are collinear and seg2_start lies on seg1
        return seg2_start
    elif o2 == 0 and on_segment(seg1_start, seg2_end, seg1_end):
        # Segments are collinear and seg2_end lies on seg1
        return seg2_end
    elif o3 == 0 and on_segment(seg2_start, seg1_start, seg2_end):
        # Segments are collinear and seg1_start lies on seg2
        return seg1_start
    elif o4 == 0 and on_segment(seg2_start, seg1_end, seg2_end):
        # Segments are collinear and seg1_end lies on seg2
        return seg1_end
    else:
        # Segments do not intersect
        return None

def semicircle_lines(cx, cy, start_angle, end_angle, radius1, radius2):

    # Calculate the coordinates of the starting and ending points of the segment
    start_x = cx + radius1 * math.cos(start_angle)
    start_y = -cy + radius1 * math.sin(start_angle)

    end_x = cx + radius1 * math.cos(end_angle)
    end_y = -cy + radius1 * math.sin(end_angle)

    # Calculate the coordinates of the starting and ending points of the outer circle
    outer_start_x = cx + radius2 * math.cos(start_angle)
    outer_start_y = -cy + radius2 * math.sin(start_angle)

    outer_end_x = cx + radius2 * math.cos(end_angle)
    outer_end_y = -cy + radius2 * math.sin(end_angle)

    return ((start_x, -start_y), (outer_start_x, -outer_start_y)), ((end_x, -end_y), (outer_end_x, -outer_end_y))
# ==============================================================
# SECTION: Misc functions
# Description: Miscelanious functions
# ==============================================================

def percentage_difference(a, b):
    """Calculates the percentage difference between two values."""
    return abs((a - b) / ((a + b) / 2)) * 100

def find_new_numbers(old_list, new_list):
    old_set = set(old_list)
    new_set = set(new_list)
    
    new_numbers = new_set - old_set
    
    return len(new_numbers), list(new_numbers)
