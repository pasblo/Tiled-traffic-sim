import math
def rotate_point(x, y, angle, direction = "Counterclockwise"):
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

    return x_rotated, y_rotated

print(rotate_point(1, 1, math.pi / 2, "Clockwise"))