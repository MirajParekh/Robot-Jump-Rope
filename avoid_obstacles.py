#!/usr/bin/env python3

"""

@author : Evan Cillie, Cole Pierson, Miraj Parekh

@date : 05 - 27 - 26

@purpose : CSC 325 Final Project (Jump Rope)

description : Have the robot find an arena (1m radius clear around it), play a startup sound and begin the game, where the robot spins increasingly fast, the goal is to not get caught by the robot's lidar scanner via jumping over it. If the robot senses someone it will stop and play a sound, indicating the end of the game.

"""

import rclpy
import time
import math 
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import TwistStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy
from turtlebot3_msgs.srv import Sound

# CONSTANTS #
RANGE = 2.0
MAX_SPEED = 6.0
START_SPEED = 1.0
ACCELERATION_RATE = 0.1

class Robot(Node):
    
    def __init__(self):
            super().__init__('avoidObstacles')


            qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            depth=10
            )
            self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile
            )

            self.publisher = self.create_publisher(
                  TwistStamped,
                  '/cmd_vel',
                  10
            )
            self.client = self.create_client(Sound, '/sound')
            self.request = Sound.Request()

            self.laser = None
            self.jump_rope = None
            self.front = None
            self.back = None 
            self.left = None
            self.right = None


    """
    Desc: plays the sound chosen via sound_id

    Args:
        sound_id (int): value (1-4) of which sound to choose
            1) Startup
            2) Low Battery (4 beeps)
            3) Shutdown (?)
            4) Empty
    
    Returns:
        the sound
    """
    def play_sound(self, sound_id):
        
        self.request.value = int(sound_id)
        
        self.future = self.client.call_async(self.request)
        
        rclpy.spin_until_future_complete(self, self.future)
        
        return self.future.result()

    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def scan_callback(self,msg):
        self.laser = msg.ranges
    
        self.jump_rope = list(self.laser[0:5]) + list(self.laser[354:359])
        self.jump_rope = self.get_range(self.jump_rope)
        self.front = self.get_range(list(self.laser[0:45]) + list(self.laser[354:359]))
        self.right = self.get_range(self.laser[46:136])
        self.left = self.get_range(self.laser[(46 + 180): (136 + 180)])
        self.back = self.get_range(self.laser[(46 + 270): (136 + 270)])



    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def drive_straight(self):
        robot_move = TwistStamped()
        robot_move.twist.linear.x  = self.get_speed()
        robot_move.twist.angular.z = 0.0
        self.publisher.publish(robot_move)


    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def stop_robot(self):
        robot_move = TwistStamped()
        robot_move.twist.linear.x = 0.0
        robot_move.twist.angular.z = 0.0
        self.publisher.publish(robot_move)


    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def turn_robot(self,speed):
        robot_move = TwistStamped()
        robot_move.twist.linear.x = 0.0
        robot_move.twist.angular.z = speed
        self.publisher.publish(robot_move)



    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def get_speed(self):
        calculated_speed = self.front * 0.1
        max_speed = 0.2
        return min(calculated_speed,max_speed)


    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def get_range(self, range):
        result = []
        for value in range:
            if value > 0.0 and not math.isinf(value) and not math.isnan(value) and value < RANGE:
                result.append(value)
            else:
                 
                result.append(RANGE + 1.0)
        if len(result) == 0:
            result = [0]
        return result


    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def jump_rope_spin(self):
        rclpy.spin_once(self)
        t1 = self.get_clock().now()
        while (min(self.jump_rope) > RANGE ):
            t2 = self.get_clock().now()
            time_elapsed = (t2 - t1).nanoseconds / 1000000000
            speed = min(MAX_SPEED, START_SPEED+time_elapsed*ACCELERATION_RATE)
            rclpy.spin_once(self)
            self.turn_robot(speed)
        
        self.stop_robot()


    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """


    def find_arena(self):
        """Reactively finds an open 2m radius area without using state variables."""
        
        current_min = min(self.get_range(self.laser))
        front_min = min(self.get_range(self.front))
        
        msg = TwistStamped() 
        if current_min >= 2.0 :
            msg.twist.linear.x = 0.0
            msg.twist.angular.z = 0.0
            self.publisher.publish(msg)
            return True 
        
        if front_min < 0.5: 
            msg.twist.linear.x = 0.0 
            msg.twist.angular.z = 1.5  
             
  
        else:
            msg.twist.linear.x = 0.2
            msg.twist.angular.z = 0.0

        self.publisher.publish(msg)
        return False 


    def play_starting_sound(self):
        # Collin Harrington assisted with sound playback

        # -- GO! (startup sound) -- 
        self.play_sound(1)

        # -- wait before starting to let sound finish -- 
        time.sleep(2.5)
    """
    Desc: 

    Args:
        msg: 
    
    Returns:
        
    """
    def play_arena_found_sound(self):
        # Collin Harrington assisted with sound playback

        # -- COUNTDOWN (3,2,1) -- 
        self.play_sound(2)
        time.sleep(3)

        # -- GO! (startup sound) -- 
        self.play_sound(1)

        # -- wait before starting to let sound finish -- 
        time.sleep(2.5)

    def play_ending_sound(self):
        self.play_sound(3)
        


def main(args=None):
    rclpy.init(args=args)
    myRobot = Robot()
    rclpy.spin_once(myRobot)
    myRobot.play_starting_sound()
    arena_found = False
    while rclpy.ok() and not arena_found:
        rclpy.spin_once(myRobot)
        arena_found = myRobot.find_arena()
    myRobot.play_arena_found_sound()
    myRobot.jump_rope_spin()  
    myRobot.play_ending_sound()
    myRobot.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()



    



