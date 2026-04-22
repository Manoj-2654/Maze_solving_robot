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

        # Load free cells
        self.free_cells = []
        with open("free_cells.txt", "r") as f:
            for line in f:
                x, y = map(float, line.strip().split(","))
                self.free_cells.append((x, y))

        self.active_positions = set()

        # Spawn every 5 sec
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
        self.get_logger().info(f"Spawned wall at ({x}, {y})")

    def delete_wall(self, name, pos):
        req = DeleteEntity.Request()
        req.name = name
        self.delete_cli.call_async(req)
        self.active_positions.remove(pos)
        self.get_logger().info(f"Deleted wall {name}")

    def update_maze(self):
        x, y = random.choice(self.free_cells)

        # avoid overlap
        if (x, y) in self.active_positions:
            return

        # avoid robot spawn area
        if abs(x) < 1 and abs(y) < 1:
            return

        name = f"wall_{x}_{y}_{random.randint(0,1000)}"

        self.spawn_wall(name, x, y)
        self.active_positions.add((x, y))

        # delete after 15 sec
        threading.Timer(110.0, lambda: self.delete_wall(name, (x, y))).start()


def main():
    rclpy.init()
    node = DynamicMaze()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
