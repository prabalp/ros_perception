#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import numpy as np
from geometry_msgs.msg import Twist

class LineFollower(object):

    def __init__(self):
    
        self.image_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, self.camera_callback)
        self.bridge_object = CvBridge()
        self.speed_pub = rospy.Publisher ("/cmd_vel", Twist, queue_size=1)

    def camera_callback(self,data):
        try:
            # We select bgr8 because its the OpenCV encoding by default
            cv_image = self.bridge_object.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except CvBridgeError as e:
            print(e)        

        height, width, channels = cv_image.shape
        descentre = 160
        rows_to_watch = 60
        crop_img = cv_image[(height)/2+descentre:(height)/2+(descentre+rows_to_watch)][1:width]
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
        upper_yellow = np.array([70,48,255])
        lower_yellow = np.array([50,28,245])

        # Threshold the HSV image to get only yellow colors
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        m = cv2.moments(mask, False)
        try:
            cx, cy = m['m10']/m['m00'], m['m01']/m['m00']
        except ZeroDivisionError:
            cy, cx = height/2, width/2

        error_x = cx - width / 2;
        speed_cmd = Twist();
        speed_cmd.linear.x = 0.2;
        speed_cmd.angular.z = -error_x / 100;
        
        self.speed_pub.publish(speed_cmd)


def main():

    rospy.init_node('line_following_node', anonymous=True)
    line_follower_object = LineFollower()
    
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
