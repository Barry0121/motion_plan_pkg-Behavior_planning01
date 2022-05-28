import rclpy
# import the ROS2 python libraries
from rclpy.node import Node

# TODO: confirm package name with team 2
from planning_interface.msg import PathMsg, SensorMsg, PathObject, SensorObject # Dummy Objects
# from team02_interface.msg import TrackedObjects # Saved for later

from rclpy.qos import ReliabilityPolicy, QoSProfile

import sys
import os
os.environ['OPENBLAS_NUM_THREADS'] = str(1)
import numpy as np
import datetime
import json
import time
import configparser
import graph_ltpl

from planning_interfaces.msg import PathMsg
from planning_interfaces.msg import PathObject
from planning_interfaces.msg import SensorMsg
from planning_interfaces.msg import SensorObject

class MotionPlan(Node):

    def __init__(self):
        # Here we have the class constructor
        # call the class constructor
        super().__init__('motion_plan')
        # create the publisher object (Output to Race Control)
        self.path_pub = self.create_publisher('OutputMsgType-TBD', 'INSERT TOPIC', 10)

        # create subsciber objects
        self.sensor_fusion_sub = self.create_subscription(SensorMsg, 'tracked_objects', self.sensor_fusion, 10) # Dummy Sub
        self.sensor_fusion_sub

        # self.sensor_fusion_sub = self.create_subscription(TrackedObjects, "tracked_objects", self.sensor_fusion, 10) #Sensor Fusion

        # self.race_line_sub = self.create_subscription(msgType2, topic2, self.race_line, 10) #Race line, not sure how often this will get updated... ideally never

        # prevent unused variable warning

        # define the timer period for 0.5 seconds
        self.timer_period = 0.5

        #self.timer = self.create_timer(timer period, callback function called every timer period) "updater"
        self.timer = self.create_timer(self.timer_period, self.plan_path)

        # Store sensor Message Variables
        self.object_list = None

        # publishable path msg objects
        self.pathMsg = PathMsg()

        """
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        INPUT OBJECT LIST FROM SENSOR FUSION TEAM HERE
        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        """
        # init dummy object list
        obj_list_dummy = graph_ltpl.testing_tools.src.objectlist_dummy.ObjectlistDummy(dynamic=True,
                                                                                       vel_scale=0.3,
                                                                                       s0=250.0)
        # self.sensor_fusion_sub()

        # init sample zone (NOTE: only valid with the default track and configuration!)
        # INFO: Zones can be used to temporarily block certain regions (e.g. pit lane, accident region, dirty track, ....).
        #       Each zone is specified in a as a dict entry, where the key is the zone ID and the value is a list with the cells
        #        * blocked layer numbers (in the graph) - pairwise with blocked node numbers
        #        * blocked node numbers (in the graph) - pairwise with blocked layer numbers
        #        * numpy array holding coordinates of left bound of region (columns x and y)
        #        * numpy array holding coordinates of right bound of region (columns x and y)

        zone_example = {'sample_zone': [[64, 64, 64, 64, 64, 64, 64, 65, 65, 65, 65, 65, 65, 65, 66, 66, 66, 66, 66, 66, 66], #blocked layers
                                        [0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 5, 6], #blocked nodes, pair with blocked layers
                                        np.array([[-20.54, 227.56], [23.80, 186.64]]), #left bound region
                                        np.array([[-23.80, 224.06], [20.17, 183.60]])]} #right bound region

        traj_set = {'straight': None}
        tic = time.time()

        while True:
            # -- SELECT ONE OF THE PROVIDED TRAJECTORIES -----------------------------------------------------------------------
            # (here: brute-force, replace by sophisticated behavior planner)
            """
            Team 1 Works Here: behavior decision making
            """



            """
            @@@@@@@@@@@@@@@@@@@@@@@
            USE BEHAVIOR VALUE HERE
            @@@@@@@@@@@@@@@@@@@@@@@
            """
            for sel_action in ["right", "left", "straight", "follow"]:  # try to force 'right', else try next in list
                if sel_action in traj_set.keys():
                    break


            # get simple object list (one vehicle driving around the track)
            # TODO: dummy will be replaced by subscriber data: self.object_list
            obj_list = obj_list_dummy.get_objectlist()

            # -- CALCULATE PATHS FOR NEXT TIMESTAMP ----------------------------------------------------------------------------
            # TODO: make sure this is subscribed to sensor fusion and object list
            ltpl_obj.calc_paths(prev_action_id=sel_action,
                                object_list=obj_list,
                                blocked_zones=zone_example)

            # -- GET POSITION AND VELOCITY ESTIMATE OF EGO-VEHICLE -------------------------------------------------------------
            # (here: simulation dummy, replace with actual sensor readings)
            if traj_set[sel_action] is not None:
                pos_est, vel_est = graph_ltpl.testing_tools.src.vdc_dummy.\
                    vdc_dummy(pos_est=pos_est,
                              last_s_course=(traj_set[sel_action][0][:, 0]),
                              last_path=(traj_set[sel_action][0][:, 1:3]),
                              last_vel_course=(traj_set[sel_action][0][:, 5]),
                              iter_time=time.time() - tic)
            tic = time.time()

            # -- CALCULATE VELOCITY PROFILE AND RETRIEVE TRAJECTORIES ----------------------------------------------------------
            traj_set = ltpl_obj.calc_vel_profile(pos_est=pos_est,
                                                 vel_est=vel_est)[0]
            # -- SEND TRAJECTORIES TO CONTROLLER -------------------------------------------------------------------------------
            # select a trajectory from the set and send it to the controller here

            """
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            PUBLISH TRAJ_SET FOR RACE CONTROL HERE!
            @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            """
            self.plan_path(ltpl_obj) # call the publisher function


    def sensor_fusion(self, msg):
        self.object_list = msg # type: list of dictionaries

    def race_line(self, msg): #import offline graph calculation and store here?
        self.race_line = msg

    # def behavior(self, msg):
    #     """
    #     TODO: Team 1: modify to set behavior from the local code
    #     """
    #     self.behavior = msg

    def plan_path(self, ltpl_obj=ltpl_obj):
        #calculate path

        # setup the path_msg
        self.pathMsg.behavior = "BEHAVIOR"
            self.pathMsg.path_pub = []
            for obj in ltpl_obj:
                tempPathObj = path_object() # TODO: change the object name

                # populate the path_object
                tempPathObj.s = None
                """
                TODO: msg population
                """

                self.pathMsg.path_pub.append(tempPathObj)

        #publish to topic for Race Control Team
        self.path_pub.publish(self.pathMsg)



def main(args=None):
    toppath = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(toppath)

    """
    @@@@@@@@@@@@@@@@@@@@@@@@@@
    GET CSV FOR RACE LINE HERE

    set 'globtraj_input_path' to path of wherever Team4 stores race line
    @@@@@@@@@@@@@@@@@@@@@@@@@@
    """
    ### TODO do we need to subscribe to raceline or just get csv? dummy berlin track for now

    track_specifier = "berlin"
    # will this be the format of raceline?
    # define all relevant paths
    path_dict = {'globtraj_input_path': toppath + "/inputs/traj_ltpl_cl/traj_ltpl_cl_" + track_specifier + ".csv", #replace with path of wherever Team4 stores race line
                 'graph_store_path': toppath + "/inputs/stored_graph.pckl", #new path to store graph of offline graph (?)
                 'ltpl_offline_param_path': toppath + "/params/ltpl_config_offline.ini", #params for generating offline graph (all possible nodes, splines, etc.)
                 'ltpl_online_param_path': toppath + "/params/ltpl_config_online.ini", #params for generating online graph (all possible nodes, splines, etc.)
                 'log_path': toppath + "/logs/graph_ltpl/",  #new path to store local path csv's and messages that are regularly updated and published? and offline graphs
                 'graph_log_id': datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S") #date time for organizing logs
                 }


    # ----------------------------------------------------------------------------------------------------------------------
    # INITIALIZATION AND OFFLINE PART --------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    # intialize graph_ltpl-class
    ltpl_obj = graph_ltpl.Graph_LTPL.Graph_LTPL(path_dict=path_dict,
                                                visual_mode=True, #disable when actually running on car
                                                log_to_file=True)

    # calculate offline graph
    ltpl_obj.graph_init()

    # set start pose based on first point in provided reference-line
    refline = graph_ltpl.imp_global_traj.src.import_globtraj_csv.\
        import_globtraj_csv(import_path=path_dict['globtraj_input_path'])[0]
    pos_est = refline[0, :] #position along race line
    heading_est = np.arctan2(np.diff(refline[0:2, 1]), np.diff(refline[0:2, 0])) - np.pi / 2 #where is car facing
    vel_est = 0.0

    """
    @@@@@@@@@@@@@@@@@@@@@@@@@@
    POSSIBLE LOCALIZATION HERE
    @@@@@@@@@@@@@@@@@@@@@@@@@@
    """
    #puts car on graph based on start pose
    ltpl_obj.set_startpos(pos_est=pos_est,
                          heading_est=heading_est)



    # initialize the ROS communication
    rclpy.init(args=args)
    # declare the node constructor
    motion_plan = MotionPlan()
    # pause the program execution, waits for a request to kill the node (ctrl+c)
    rclpy.spin(motion_plan)
    # Explicity destroy the node
    motion_plan.destroy_node()
    # shutdown the ROS communication
    rclpy.shutdown()

if __name__ == '__main__':
    main()
