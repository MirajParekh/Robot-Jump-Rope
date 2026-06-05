# Robot-Jump-Rope by Miraj, Cole, and Evan

To run up this project, download the .py file in the repo, and put it inside a standard ROS2 package (you'll have to do this). Make sure to include dependencies like rclpy, sensor_msgs, geometry_msgs, and turtlebot3_msgs. 

When executing the package, the robot will move around a space until it finds an area suitable to be the arena. Once discovered, the game sound commences and the robot will play jump-rope, spinning around until it catches a player that fails to jump over the virtual LiDAR-based rope. The robot will continually accelerate its spinning, and once a player loses, the game will end. 
