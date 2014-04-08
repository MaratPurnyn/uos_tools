#!/usr/bin/env python
import roslib; roslib.load_manifest('acc_finder')
import rospy

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

LIN_MAX = 0.75
ANG_MAX = 1.0   # adjust this value to the rough maximum angular velocity

state = 'stopped'
start = rospy.Time(0.0)

def odom_cb(msg):
    global state

    twist = msg.twist.twist
    t = (rospy.Time.now() - start).to_sec()

    if state == 'wait_for_stop':
        if twist.linear.x > -0.05 and twist.linear.x < 0.05 and twist.angular.z > -0.1 and twist.angular.z < 0.1:
            state = 'stopped'
            rospy.loginfo('state transition --> %s', state)
        return

    if state == 'backward' and twist.linear.x < -0.9 * LIN_MAX:
        rospy.loginfo('backward from 0 to %f m/s in %f sec', twist.linear.x, t)
    elif state == 'forward' and twist.linear.x > 0.9 * LIN_MAX:
        rospy.loginfo('forward from 0 to %f m/s in %f sec', twist.linear.x, t)
    elif state == 'turning_clockwise' and twist.angular.z < -0.9 * ANG_MAX:
        rospy.loginfo('turning_clockwise from 0 to %f rad/s in %f sec', twist.angular.z, t)
    elif state == 'turning_counter_clockwise' and twist.angular.z > 0.9 * ANG_MAX:
        rospy.loginfo('turning_counter_clockwise from 0 to %f rad/s in %f sec', twist.angular.z, t)
    else:
        return

    state = 'wait_for_stop'
    rospy.loginfo('state transition --> %s', state)


def cmd_vel_cb(msg):
    global state, start

    if state != 'stopped':
        return

    if msg.linear.x < -0.5:
        start = rospy.Time.now()
        state = 'backward'
    elif msg.linear.x > 0.5:
        start = rospy.Time.now()
        state = 'forward'
    elif msg.angular.z < -1.0:
        start = rospy.Time.now()
        state = 'turning_clockwise'
    elif msg.angular.z > 1.0:
        start = rospy.Time.now()
        state = 'turning_counter_clockwise'
    else:
        return

    rospy.loginfo('state transition --> %s', state)


def listener():
    rospy.init_node('acc_finder', anonymous=True)
    rospy.Subscriber('odom', Odometry, odom_cb)
    rospy.Subscriber('cmd_vel', Twist, cmd_vel_cb)
    rospy.spin()

if __name__ == '__main__':
    listener()
