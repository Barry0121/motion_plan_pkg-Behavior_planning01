# Behavior Planning Based on Graph Based Trajectory Planner
[Sounce: Graph Based Trajectory Planner]{https://github.com/emersonchao/GraphBasedLocalTrajectoryPlanner}

## Overview
Behavior planning module is designed to make a decision on the optimal strategy to take when unexpected situation happened during the race. These situations, most commonly, are staic objects on the track or moving opponent that have blocked the optimal race path given to the car before the race.
This package completes the Graph Based Trajectory Planner's missing behavior planning part. The repository contains the complete ROS2 package that is ready to be customize, build and run in a given ROS2 environment.
The package subscribes to the perception fusion message, which is expected to be published by another node that analyize and compound different perception souces (ex: image, lidar, etc). The package will publish a message with an array of value, representing the local path plan. 
<br> 
We improve upon the original brute force approach by ranking all of the behavior options. Here we have 4: 
1. Follow: as the name suggest, maintain on the optimal global race track, and maintain the current relative velocity with the target objects. 
2. Straight: not following the opponent/object car speed, simply accelerating and following the race path. 
3. Right: overtake the opponent/object from the right side
4. Left: overtake the opponent/object from the left side 
FYI: These actions DOESN'T specify the excecution processures. It simply is an evaluation of the given situation, and provide a suggestion to the local path planning module to choose from a range of available local paths. 
<br>
To complete that goal, we looked at 3 main static distances and 1 type of velocity: distance to object, object position in relation to the track boundary (left and right; this is 2 distances), and the relative velocity between our car and the object. 
The code is designed to include more parameters, such as car orientation, relative accelerations, etc. But we are limited to the only the position and velocity due to our input is from a restrcited simulation. 
<br> 
Using a state machine approach, we looked at the realtive velocity as the root determinator to decide between 3 states: follow, straight, and overtake. In any given situation, we should see that the published behavior message cycle between the three as our car following through with the given action. 
Once we know the car is engaged in a given state, we look at the 3 distance to make some inference between what type of approach we should take. For example, if we choose to overtake based on the relative velocity being negative (meaning we are going faster than the opponnt), the system will look at the distance to see if the timing is safe enough to actually overtake; if not, we will change states to wait for a better oppotunity. 
<br> 
Because the referenced Trajectory Planner, the system our approach is based off of, provides a strong support for generating and narrowing the scope of optimal local paths before we run our behavior planner, we don't want to leave our approach that is proven to work. So we decided to take a similar approach, which is to rank the available action states, and go through then from top ranked to bottom ranked to match with the generated local path, in order to allow the system to participate in our decision. 
This will look like a for-loop check; for all the available options in the list, check if there is a suggested local path from the trajectory planner, if so, we go with this option; if not, iterate to the next suggested action state and repeat the process. 
This approach ensure a boost to the quality of path suggestion while ensuring that our system work, at least at the minimum. 

## Quick Start 
First, clone this repo and go to the `motion_plan_pkg\motion_plan.py`, import all of the message type you defined through your interface node (ex: SensorMsg, PathMsg, etc). 
Then, customize the subscriber to receive those messages, and update the callback function for the subscriber to assign the correct variable with the correct values. 
Fianlly, get into your ROS environment and run: 
```
# run this at the src directory of your workspace
colcon build 
```
Now, you should be able to luanch this node after you have started the perceptions nodes.

## Challenges faced
1. The biggest problem is to ensrue that what we are getting is correct. This means checking all the distances, velocties somewhat makes sense in a given situation. For distances, the best we can do is to approximate with basic assumptions like we are going on a straight path and etc, so in cases that are extreme and unexpected, we still ran into error telling us that there isn't an available path to take. 
2. During integration with the perception fusion team, many of the published message contain different elements. One moment we might have self velocity and another moement we might not. This is not something they can improve on, since many of the instances when this happened, it is usualy due to a environmental uncertainty. We worked around this by keeping the features that are constantly published and useful at the same time. 

## Development timeline
Week 7: Research existing/proposed behavior planning approach to commercial vehicles. Decided to proceed with the finite state machine approach to this problem. We also got introduced to the Trajectory Planner and start looking into it. 
Week 8: Start writting down the basic logic behind bahavior planning and research available frameworks that we can rely on (ex: NAV2) but all of them are somewhat overkill for our need. 
Week 9: Finsihed verison 1 of our code along with our publsihing interface. However, once we started to merge with the local path planning team, we found out they are using the same package with an interface already determined. So we ditched our previous approach and start working with them. 
Week 10+Final: Continued our collaboration. At this point we are working on the same stuff and solving the same problem. By the end, we start to ran tests on svl_sim, but it didn't pan out as smoothly as we would have thought due to path planning issues. 

