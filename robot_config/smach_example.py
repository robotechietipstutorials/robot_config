import smach
import smach_ros
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

class GetTrigger(smach.State):
    def __init__(self, node):
        smach.State.__init__(self, outcomes=['to_box1', 'to_box2'])
        self.node = node
        self.trigger_received = False
        self.trigger_value = None
        self.subscription = self.node.create_subscription(
            Bool,
            'trigger',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.trigger_value = msg.data
        self.trigger_received = True
        self.node.get_logger().info(f"Trigger: {self.trigger_value}")

    def execute(self, userdata):
        self.node.get_logger().info("Executing State GET_TRIGGER")
        while not self.trigger_received:
            rclpy.spin_once(self.node)  
            time.sleep(0.1)  
        self.trigger_received = False
        if self.trigger_value:
            return 'to_box1' 
        else:
            return 'to_box2'  

class CheckBox1(smach.State):
    def __init__(self, node):
        smach.State.__init__(self, outcomes=['done'])
        self.node = node
        self.publisher = self.node.create_publisher(String, 'box_number', 10)
        self.message = String()

    def execute(self, userdata):
        self.node.get_logger().info("Executing State CHECKBOX_1")
        time.sleep(2)
        self.message.data = "check_box2"
        self.publisher.publish(self.message)
        return 'done'  

class CheckBox2(smach.State):
    def __init__(self, node):
        smach.State.__init__(self, outcomes=['done'])
        self.node = node
        self.publisher = self.node.create_publisher(String, 'box_number', 10)
        self.message = String()

    def execute(self, userdata):
        self.node.get_logger().info("Executing State CHECKBOX_2")
        time.sleep(2) 
        self.message.data = "check_box1"
        self.publisher.publish(self.message)
        return 'done' 


class StateMachineNode(Node):
    def __init__(self):
        super().__init__('ros2_smach_node')
        self.sm = smach.StateMachine(outcomes=['done'])
        with self.sm:
            smach.StateMachine.add('GET_TRIGGER', GetTrigger(self), transitions={'to_box1': 'CHECK_BOX1', 'to_box2': 'CHECK_BOX2'})
            smach.StateMachine.add('CHECK_BOX1', CheckBox1(self), transitions={'done': 'GET_TRIGGER'})
            smach.StateMachine.add('CHECK_BOX2', CheckBox2(self), transitions={'done': 'GET_TRIGGER'})

        self.smach_viewer = smach_ros.IntrospectionServer('state_machine_viewer', self.sm, '/SM_ROOT')
        self.smach_viewer.start()

        self.execute_state_machine()

    def execute_state_machine(self):
        outcome = self.sm.execute()
        self.get_logger().info(f'ROS2 SM completed : {outcome}')
        self.smach_viewer.stop()

def main(args=None):
    rclpy.init(args=args)
    node = StateMachineNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

