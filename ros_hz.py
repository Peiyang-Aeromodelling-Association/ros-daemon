import rospy, rostopic
import sys

TOPIC = sys.argv[1]

rospy.init_node('ros_topic_hz' + TOPIC.replace('/','_'))

h = rostopic.ROSTopicHz(-1)
s1 = rospy.Subscriber(TOPIC, rospy.AnyMsg, h.callback_hz, callback_args=TOPIC)
rospy.sleep(1)
h.print_hz([TOPIC])
