import math
class Circle:
    def __init__(self,center,rad):
        self.center=center
        self.rad=rad
class Point:
    def __init__(self,pointx,pointy):
        self.pointx=pointx
        self.pointy=pointy
def point_in_circle(circle, point):
    distance_sq = (point.pointx - circle.center.pointx)**2 + (point.pointy - circle.center.pointy)**2
    radius_sq = circle.rad**2
    return distance_sq <= radius_sq
    
rad=int(input())
pointx=int(input())
pointy=int(input())
centerx=int(input())
centery=int(input())
circle=Circle(Point(centerx,centery),rad)
point=Point(pointx,pointy)
print("point in the circle or not",end="")
print(point_in_circle(circle,point))