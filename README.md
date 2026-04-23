# Maze_solving_robot
a robot which uses D* algorithm to solve dynamic maze
# ==============================
# 🚀 MAZE SOLVING ROBOT - RUN GUIDE
# ==============================


# ==============================
# STEP 1: CREATE MAZE GENERATION FILE
# ==============================

nano maze_gen.py

# (Paste the maze generation code here and save)


# ==============================
# STEP 2: GENERATE MAZE WORLD
# ==============================

python3 maze_gen.py

# Output: maze.world file generated


# ==============================
# STEP 3: LAUNCH GAZEBO WITH MAZE
# ==============================

ros2 launch gazebo_ros gazebo.launch.py world:=/home/<your-username>/maze.world


# ==============================
# STEP 4: SPAWN ROBOT IN GAZEBO
# ==============================

ros2 run gazebo_ros spawn_entity.py \
-entity waffle \
-file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf \
-x 0 -y 0 -z 0.1


# ==============================
# STEP 5: PUBLISH STATIC TF (MAPPING PHASE)
# ==============================

ros2 run tf2_ros static_transform_publisher \
0 0 0 0 0 0 base_footprint base_scan


# ==============================
# STEP 6: START SLAM (MAPPING)
# ==============================

ros2 launch slam_toolbox online_async_launch.py \
use_sim_time:=true \
debug_logging:=true \
map_update_interval:=0.5


# ==============================
# STEP 7: OPEN RVIZ2 FOR VISUALIZATION
# ==============================

rviz2

# In RViz:
# - Set Fixed Frame → map
# - Add Map → /map
# - Add LaserScan → /scan


# ==============================
# STEP 8: TELEOPERATE ROBOT (EXPLORE MAZE)
# ==============================

ros2 run turtlebot3_teleop teleop_keyboard


# ==============================
# STEP 9: SAVE GENERATED MAP
# ==============================

ros2 run nav2_map_server map_saver_cli -f my_map

# Output: my_map.yaml and my_map.pgm


# ==============================
# STEP 10: CLOSE ALL TERMINALS (IMPORTANT)
# ==============================

# Close all running terminals before starting navigation phase


# ==============================
# STEP 11: RESTART GAZEBO
# ==============================

ros2 launch gazebo_ros gazebo.launch.py world:=/home/<your-username>/maze.world


# ==============================
# STEP 12: SPAWN ROBOT AGAIN
# ==============================

ros2 run gazebo_ros spawn_entity.py \
-entity waffle \
-file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf \
-x 0 -y 0 -z 0.1


# ==============================
# STEP 13: PUBLISH TF (NAVIGATION PHASE)
# ==============================

ros2 run tf2_ros static_transform_publisher \
0 0 0 0 0 0 base_link base_scan

ros2 run tf2_ros static_transform_publisher \
0 0 0 0 0 0 base_footprint base_link


# ==============================
# STEP 14: START NAVIGATION (NAV2)
# ==============================

ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:=/home/<your-username>/my_map.yaml


# ==============================
# STEP 15: SET GOAL IN RVIZ
# ==============================

# Open RViz2
# Click "2D Goal Pose"
# Select destination point

# Robot will autonomously navigate using A* + D*


# ==============================
# ✅ END OF EXECUTION
# ==============================
is this ok forr readme
