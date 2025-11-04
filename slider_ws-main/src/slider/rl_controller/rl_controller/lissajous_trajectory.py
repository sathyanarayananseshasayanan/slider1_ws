# target_publisher.py
import math
from typing import Tuple
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import QoSPresetProfiles
import argparse

# --- CLI args (kept) ---
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('lissa_A',default=2.0, type=float)
parser.add_argument('lissa_B',default=2.0, type=float)
parser.add_argument('lissa_a',default=1, type=int)
parser.add_argument('lissa_b',default=2, type=int)
parser.add_argument('lissa_delta',default=1.0, type=float)
parser.add_argument('lissa_omega',default=0.05, type=float)

# parser.add_argument('target_y')
known_args, _ = parser.parse_known_args()
lissa_omega = float(known_args.lissa_omega)
lissa_A = float(known_args.lissa_A)
lissa_B = float(known_args.lissa_B)
lissa_a = float(known_args.lissa_a)
lissa_b = float(known_args.lissa_b)
lissa_delta = float(known_args.lissa_delta)

# target_y_arg = float(known_args.target_y)


# --- Lissajous helper ---
def lissajous_state(
    t: float,
    center: Tuple[float, float, float],
    A: float, B: float,
    a: float, b: float,
    delta: float,
    omega: float,
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
    """
    Position and velocity on a Lissajous curve at time t.

    x = cx + A * sin(a * (omega*t) + delta)
    y = cy + B * sin(b * (omega*t))
    z = cz

    vx = A * a * omega * cos(a * (omega*t) + delta)
    vy = B * b * omega * cos(b * (omega*t))
    vz = 0
    """
    cx, cy, cz = center
    theta = omega * t

    x = cx + A * math.sin(a * theta + delta)
    y = cy + B * math.sin(b * theta)
    z = cz

    vx = A * a * omega * math.cos(a * theta + delta)
    vy = B * b * omega * math.cos(b * theta)
    vz = 0.0

    return (x, y, z), (vx, vy, vz)


class LissajousTrajectory(Node):
    def __init__(self):
        super().__init__('target_point')

        self.declare_parameter('frame_id', 'world')
        self.declare_parameter('publish_rate', 10.0)

        self.declare_parameter('lissa_A', 1.0)
        self.declare_parameter('lissa_B', 1.0)
        self.declare_parameter('lissa_a', 1.0)
        self.declare_parameter('lissa_b', 2.0)
        self.declare_parameter('lissa_delta', 0.0)
        self.declare_parameter('lissa_omega', 1.0)    

        frame = self.get_parameter('frame_id').get_parameter_value().string_value
        self.rate = float(self.get_parameter('publish_rate').get_parameter_value().double_value)
        
        self.dt = 1.0 / self.rate
        self.t = 0.0  # time accumulator

        self.A = lissa_A
        self.B = lissa_B
        self.a = lissa_a
        self.b = lissa_b
        self.delta = lissa_delta
        self.omega = lissa_omega

        # Message setup (initialize at t=0)
        self.msg = Odometry()
        self.msg.header.frame_id = frame
        (x, y, z), (vx, vy, vz) = lissajous_state(
            t=0.0,
            center=(0.0, 0.0, 0.0),
            A=self.A, B=self.B,
            a=self.a, b=self.b,
            delta=self.delta,
            omega=self.omega,
        )
        self.msg.pose.pose.position.x = x
        self.msg.pose.pose.position.y = y
        self.msg.pose.pose.position.z = z
        self.msg.twist.twist.linear.x = vx
        self.msg.twist.twist.linear.y = vy
        self.msg.twist.twist.linear.z = vz

        self.publisher_ = self.create_publisher(
            Odometry,
            'target_point',
            QoSPresetProfiles.get_from_short_key('system_default')
        )
        self.timer = self.create_timer(self.dt, self._tick)

    def _tick(self):
        # advance time
        self.t += self.dt

        # compute state
        (x, y, z), (vx, vy, vz) = lissajous_state(
            t=self.t,
            center=(0.0, 0.0, 0.0),
            A=self.A, B=self.B,
            a=self.a, b=self.b,
            delta=self.delta,
            omega=self.omega,
        )

        self.msg.header.stamp = self.get_clock().now().to_msg()
        self.msg.pose.pose.position.x = x
        self.msg.pose.pose.position.y = y
        self.msg.pose.pose.position.z = z
        self.msg.twist.twist.linear.x = vx
        self.msg.twist.twist.linear.y = vy
        self.msg.twist.twist.linear.z = vz
        self.publisher_.publish(self.msg)


def main(args=None):
    rclpy.init(args=args)
    node = LissajousTrajectory()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
