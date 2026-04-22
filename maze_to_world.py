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
        if maze[y][x] == 0:  # free space
            gx = (x - center_x) * cell_size
            gy = (y - center_y) * cell_size
            free_cells.append((gx, gy))

# Save free cells
with open("free_cells.txt", "w") as f:
    for x, y in free_cells:
        f.write(f"{x},{y}\n")
