import math

def correct_radian(angle):
    """Ensures the angle is within 0 to 2*pi radians."""
    return angle % (2 * math.pi)

def angle_point_to_point(origin_x, origin_y, far_x, far_y):
    """Calculates the angle between two points."""
    return correct_radian(math.atan2(origin_y-far_y, far_x-origin_x))

print(angle_point_to_point)