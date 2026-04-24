# 🚀 MAZE SOLVING ROBOT USING D* (ROS2 + GAZEBO)

## 📌 PROJECT DESCRIPTION
A robot that navigates a dynamic maze using:
- SLAM for mapping
- Nav2 (A*) for planning
- Dynamic obstacles (D*-like behavior)

---

## 📁 PROJECT FILES
- maze_to_world.py → Generates maze.world + free_cells.txt  
- dynamic_walls.py → Dynamic obstacle generation  
- maze.world → Gazebo world  
- free_cells.txt → Valid spawn positions  

---

## 🧩 MAZE GENERATION CODE (maze_to_world.py)

```python
import random

width, height = 11, 11
cell_size = 1.0

maze = [[1 for _ in range(width)] for _ in range(height)]

center_x = width // 2
center_y = height // 2

def carve(x, y):
    dirs = [(2,0), (-2,0), (0,2), (0,-2)]
    random.shuffle(dirs)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy

        if 0 < nx < width and 0 < ny < height and maze[ny][nx] == 1:
            maze[ny][nx] = 0
            maze[y + dy//2][x + dx//2] = 0
            carve(nx, ny)

maze[center_y][center_x] = 0
carve(center_x, center_y)

safe = 1
for y in range(center_y - safe, center_y + safe + 1):
    for x in range(center_x - safe, center_x + safe + 1):
        maze[y][x] = 0

def wall_block(x, y):
    return f"""
    <model name='wall_{x}_{y}'>
      <static>true</static>
      <link name='link'>
        <pose>{x} {y} 0.5 0 0 0</pose>
        <collision name='collision'>
          <geometry>
            <box><size>{cell_size} {cell_size} 1</size></box>
          </geometry>
        </collision>
        <visual name='visual'>
          <geometry>
            <box><size>{cell_size} {cell_size} 1</size></box>
          </geometry>
        </visual>
      </link>
    </model>
    """

world = """<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="maze_world">

  <plugin name="gazebo_ros_init" filename="libgazebo_ros_init.so"/>
  <plugin name="gazebo_ros_factory" filename="libgazebo_ros_factory.so"/>

  <include>
    <uri>model://ground_plane</uri>
  </include>

  <include>
    <uri>model://sun</uri>
  </include>
"""

for y in range(height):
    for x in range(width):
        if maze[y][x] == 1:
            gx = (x - center_x) * cell_size
            gy = (y - center_y) * cell_size
            world += wall_block(gx, gy)

world += """
  </world>
</sdf>
"""

with open("maze.world", "w") as f:
    f.write(world)

print("maze.world generated")

free_cells = []

for y in range(height):
    for x in range(width):
        if maze[y][x] == 0:
            gx = (x - center_x) * cell_size
            gy = (y - center_y) * cell_size
            free_cells.append((gx, gy))

with open("free_cells.txt", "w") as f:
    for x, y in free_cells:
        f.write(f"{x},{y}\n")
```

---

## 🔄 DYNAMIC WALLS CODE (dynamic_walls.py)

```python
import rclpy
from rclpy.node import Node
from gazebo_msgs.srv import SpawnEntity, DeleteEntity
import random
import threading

class DynamicMaze(Node):

    def __init__(self):
        super().__init__('dynamic_maze')

        self.spawn_cli = self.create_client(SpawnEntity, '/spawn_entity')
        self.delete_cli = self.create_client(DeleteEntity, '/delete_entity')

        while not self.spawn_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service...')
        while not self.delete_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for delete service...')

        self.free_cells = []
        with open("free_cells.txt", "r") as f:
            for line in f:
                x, y = map(float, line.strip().split(","))
                self.free_cells.append((x, y))

        self.active_positions = set()

        self.timer = self.create_timer(120.0, self.update_maze)

    def spawn_wall(self, name, x, y):
        req = SpawnEntity.Request()
        req.name = name
        req.xml = f"""
        <sdf version='1.6'>
          <model name='{name}'>
            <static>true</static>
            <link name='link'>
              <pose>{x} {y} 0.5 0 0 0</pose>
              <collision name='collision'>
                <geometry><box><size>1 1 1</size></box></geometry>
              </collision>
              <visual name='visual'>
                <geometry><box><size>1 1 1</size></box></geometry>
              </visual>
            </link>
          </model>
        </sdf>
        """
        self.spawn_cli.call_async(req)

    def delete_wall(self, name, pos):
        req = DeleteEntity.Request()
        req.name = name
        self.delete_cli.call_async(req)
        self.active_positions.remove(pos)

    def update_maze(self):
        x, y = random.choice(self.free_cells)

        if (x, y) in self.active_positions:
            return

        if abs(x) < 1 and abs(y) < 1:
            return

        name = f"wall_{x}_{y}_{random.randint(0,1000)}"

        self.spawn_wall(name, x, y)
        self.active_positions.add((x, y))

        threading.Timer(110.0, lambda: self.delete_wall(name, (x, y))).start()


def main():
    rclpy.init()
    node = DynamicMaze()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## 🚀 COMPLETE RUN COMMANDS

```bash
# ==============================
# MAPPING PHASE
# ==============================

# STEP 1: GENERATE MAZE
python3 maze_to_world.py

# STEP 2: LAUNCH GAZEBO
ros2 launch gazebo_ros gazebo.launch.py world:=/home/<your-username>/maze.world

# STEP 3: SPAWN ROBOT
ros2 run gazebo_ros spawn_entity.py \
-entity waffle \
-file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf \
-x 0 -y 0 -z 0.1

# STEP 4: START DYNAMIC WALLS
python3 dynamic_walls.py

# STEP 5: STATIC TF (MAPPING)
ros2 run tf2_ros static_transform_publisher \
0 0 0 0 0 0 base_footprint base_scan

# STEP 6: START SLAM
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true

# STEP 7: OPEN RVIZ
rviz2
# Set Fixed Frame = map
# Add Map (/map) and LaserScan (/scan)

# STEP 8: TELEOP ROBOT
ros2 run turtlebot3_teleop teleop_keyboard

# STEP 9: SAVE MAP
ros2 run nav2_map_server map_saver_cli -f my_map


# ==============================
# NAVIGATION PHASE
# ==============================

# STEP 10: CLOSE ALL TERMINALS

# STEP 11: RESTART GAZEBO
ros2 launch gazebo_ros gazebo.launch.py world:=/home/<your-username>/maze.world

# STEP 12: SPAWN ROBOT AGAIN
ros2 run gazebo_ros spawn_entity.py \
-entity waffle \
-file /opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle/model.sdf \
-x 0 -y 0 -z 0.1

# STEP 13: TF (NAVIGATION)
ros2 run tf2_ros static_transform_publisher \
0 0 0 0 0 0 base_link base_scan

ros2 run tf2_ros static_transform_publisher \
0 0 0 0 0 0 base_footprint base_link

# STEP 14: START NAVIGATION
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:=/home/<your-username>/my_map.yaml

# STEP 15: OPEN RVIZ & SET GOAL
rviz2
# Click "2D Goal Pose"
# Select destination point

# STEP 16 : Open a new terminal 
# Run python3 dynamic_maze.py
# This starts spawning the maze walls dynamically

# Robot will navigate automatically
```

---

## 🎯 OUTPUT
- Robot explores maze  
- Map is created  
- Dynamic walls appear/disappear  
- Robot replans path automatically  

---

## 💡 CONCEPT
- A* → Path planning  
- Dynamic obstacles → D* behavior  
- Continuous replanning  
