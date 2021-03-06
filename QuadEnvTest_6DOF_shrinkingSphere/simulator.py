# Code to simulate the environment when trained
import os
#ignore tensorflow warnings
import warnings
warnings.filterwarnings("ignore")

import gym
import numpy as np
import matplotlib
matplotlib.use('pdf') # To avoid plt.show issues in virtualenv
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import axes3d
from math import e

from stable_baselines.common.policies import MlpPolicy
from stable_baselines import PPO2
from quadcopt_I import QuadcoptEnv_6DOF


env = QuadcoptEnv_6DOF(Random_reset=False, Process_perturbations=True)

tieme_steps_to_simulate = int(env.max_Episode_time_steps) + 1 ## define the number of timesteps to simulate

######################################
##      POLICY LOADING SECTION      ##
######################################

# use of os.path.exists() to check and load the last policy evaluated by training
# function.
print("Policy loading...")

Policy_loading_mode = input("Insert loading mode\nlast: loads last policy saved\nbest: loads best policy saved\nsel: loads a specified policy\n-----> ")

if Policy_loading_mode == "last":
  for i in range(100, 0, -1): ## function look for the last policy evaluated.
    #fileName_toFind = "/home/ghost/giorgio_diliberi/ReinforcementLearning/Stable_Baselines2_Frame/QuadEnvTest_6DOF/Policies/PPO_Quad_" + str(i) + ".zip"
    fileName_toFind = "/C:/Users/ricca/Desktop/Tesi/ReinforcementLearning-main/Stable_Baselines2_Frame/QuadEnvTest_6DOF/Policies/PPO_Quad_" + str(i) + ".zip"
    if os.path.exists(fileName_toFind):
      print("last policy found is PPO_Quad_", i)

      Policy2Load = "Policies/PPO_Quad_" + str(i)
      
      break

  

elif Policy_loading_mode == "best":

  Policy2Load = "EvalClbkLogs/best_model.zip" # best policy name

else:

  Policy2Load  = input("enter the relative path of policy to load (check before if exists): ")
  
  

model = PPO2.load(Policy2Load)
print("Policy ", Policy2Load, " loaded!")

######################################
##     SIMULATION SECTION           ##
######################################
 
#model = PPO2.load("Policies/PPO_Quad_1")  # uncomment this line to load a specific policy instead of the last one

obs = env.reset()

# info vectors initialization for simulation history
info_u = [env.state[0]]
info_v = [env.state[1]]
info_w = [env.state[2]]
info_Vel = [0.]
info_p = [env.state[3]]
info_q = [env.state[4]]
info_r = [env.state[5]]
info_quaternion = np.array([env.state[6:10]]) # quaternion stored in a np.array matrix
info_X = [env.state[10]]
info_Y = [env.state[11]]
info_Z = [env.state[12]]
action_memory = np.array([0., 0., 0., 0.]) ## vector to store actions during the simulation
#Throttle_memory = [env.dTt]
episode_reward = [0.]

X_ref = [env.X_Pos_Goal]
Y_ref = [env.Y_Pos_Goal]
Z_ref = [env.Goal_Altitude]

time=0.
info_time=[time] # elapsed time vector

# SIMULATION

for i in range(tieme_steps_to_simulate): #last number is excluded


    env.X_Pos_Goal=0. #1*np.cos(i/(512*0.30))#e**(-i/300) * 0.5 * np.cos(i/(512*0.075))
    env.Y_Pos_Goal=0.  #1*np.sin(i/(512*0.15))#e**(-i/300) * 0.5 * np.sin(i/(512*0.075))
    env.Goal_Altitude=0.
    if i==512000/2:
      env.X_Pos_Goal=-5.
      env.Y_Pos_Goal=-5.
      env.Goal_Altitude=-35.

    if i==80000:
      env.X_Pos_Goal=10.
      env.Y_Pos_Goal=10.
      env.Goal_Altitude =-25.

    # if i==1536:
    #   env.X_Pos_Goal=0.
    #   env.Y_Pos_Goal=11.1
    #   env.Goal_Altitude=-28.
    
    action, _state = model.predict(obs, deterministic=True) # Add deterministic true for PPO to achieve better performane
    
    obs, reward, done, info = env.step(action) 

    info_u.append(info["u"])
    info_v.append(info["v"])
    info_w.append(info["w"])
    info_p.append(info["p"])
    info_q.append(info["q"])
    info_r.append(info["r"])
    info_quaternion = np.vstack([info_quaternion, [info["q0"], info["q1"], info["q2"], info["q3"]]])
    info_X.append(info["X"])
    info_Y.append(info["Y"])
    info_Z.append(info["Z"])
    action_memory = np.vstack([action_memory, action])
    #Throttle_memory.append(env.linearAct2ThrMap(action[0]))
    episode_reward.append(reward) # save the reward for all the episode

    X_ref.append(env.X_Pos_Goal)
    Y_ref.append(env.Y_Pos_Goal)
    Z_ref.append(env.Goal_Altitude)

    time=time + env.timeStep # elapsed time since simulation start
    info_time.append(time)

    #env.render()
    if done:
      # obs = env.reset()
      break

    if i==512:
      print("mid sim position [X, Y, Z]= ", env.state[10:13])

print("final position [X, Y, Z]= ", env.state[10:13])
dist = np.sqrt((env.state[10]-env.X_Pos_Goal)**2 + (env.state[11]-env.Y_Pos_Goal)**2 + (env.state[12]-env.Goal_Altitude)**2)
print("final distance =", dist)

## PLOT AND DISPLAY SECTION

plt.figure(1)
plt.plot(info_time, info_p)
plt.plot(info_time, info_q)
plt.plot(info_time, info_r)
plt.xlabel('time')
plt.ylabel('Angular velocity [rad/s]')
plt.title('p,q and r')
plt.legend(['p', 'q', 'r'])
plt.savefig('SimulationResults_0803/Angular_velocity_1.jpg')

plt.figure(2)
plt.plot(info_time, info_u)
plt.plot(info_time, info_v)
plt.plot(info_time, info_w)
plt.xlabel('time')
plt.ylabel('Velocity [m/s]')
plt.title('u,v and w')
plt.legend(['u', 'v', 'w'])
plt.savefig('SimulationResults_0803/Velocity_1.jpg')

plt.figure(3)
plt.plot(info_time, info_X)
plt.plot(info_time, info_Y)
plt.plot(info_time, info_Z)
plt.plot(info_time, X_ref)
plt.plot(info_time, Y_ref)
plt.plot(info_time, Z_ref)
plt.xlabel('time')
plt.ylabel('Position NED [m]')
plt.title('X,Y and Z')
plt.legend(['X', 'Y', 'Z', 'X ref', 'Y ref', 'Z ref'])
plt.savefig('SimulationResults_0803/Position_1.jpg')

## CONVERSION OF THE QUATERNION INTO EULER ANGLES
Euler_angles = np.zeros([np.size(info_quaternion, 0), 3])

for row in range(np.size(Euler_angles, 0)):
  q0 = info_quaternion[row, 0]
  q1 = info_quaternion[row, 1]
  q2 = info_quaternion[row, 2]
  q3 = info_quaternion[row, 3]

  Euler_angles[row, 0] = np.arctan2(2*(q0*q1 + q2*q3), 1-2*(q1**2+q2**2))
  Euler_angles[row, 1] = np.arcsin(2*(q0*q2-q3*q1))
  Euler_angles[row, 2] = np.arctan2(2*(q0*q3+q1*q2), 1-2*(q2**2+q3**2))

#Conversion to degrees from radians
Euler_angles = Euler_angles * (180 / np.pi)

plt.figure(4)
plt.plot(info_time, Euler_angles[:, 0])
plt.plot(info_time, Euler_angles[:, 1])
plt.plot(info_time, Euler_angles[:, 2])
plt.xlabel('time')
plt.ylabel('Angles [deg]')
plt.title('Euler Angles')
plt.legend(['Phi', 'Theta', 'Psi'])
plt.savefig('SimulationResults_0803/Euler_1.jpg')

plt.figure(5)
plt.plot(info_time, episode_reward)
plt.xlabel('time')
plt.ylabel('Reward')
plt.title('Episode Reward')
plt.savefig('SimulationResults_0803/reward_1.jpg')

plt.figure(6)
plt.plot(info_time, action_memory[:, 0])
plt.plot(info_time, action_memory[:, 1])
plt.plot(info_time, action_memory[:, 2])
plt.plot(info_time, action_memory[:, 3])
plt.xlabel('time')
plt.ylabel('Actions')
plt.title('Actions in episode [-1, 1]')
plt.legend(['Avg_thr', 'Ail', 'Ele', 'Rud'])
plt.savefig('SimulationResults_0803/action_1.jpg')

info_H = -1 * np.array([info_Z])
H_ref = -1 * np.array([Z_ref])
fig = plt.figure(7)
ax = fig.add_subplot(111, projection='3d')
ax.plot_wireframe(np.array([info_X]), np.array([info_Y]), info_H)
ax.scatter(2, 0, 0, s = 50, c = 'r')
#ax.scatter(0, 0, 0, s = 50, c = 'g')
ax.set_xlim3d([-2.2, 2.2])
ax.set_ylim3d([-2.2, 2.2])
ax.set_zlim3d([-2.2, 2.2])
ax.scatter(0, 0, 0, edgecolors = 'r')
ax.legend(['Traiettoria', 'Partenza', 'Target'])
#ax.plot_wireframe(np.array([0.]), np.array([0.]), np.array([25.]), s = '200')
#ax.plot_wireframe(np.array([10.]), np.array([15.]), np.array([35.]), s = '200', c = 'g')
#ax.plot(np.array([X_ref]), np.array([Y_ref]), info_H)
#ax.xlabel('X')
#ax.ylabel('Y')
#ax.ylabel('H==-Z')
#ax.title('Trajectory')
plt.savefig('SimulationResults_0803/Trajectory_1.jpg')

plt.figure(8)
plt.plot(info_X, info_Y)
plt.scatter(2, 0, s = 50, c ='r')
plt.scatter(0, 0, s = 50, c = 'g')
plt.plot(X_ref, Y_ref)
plt.xlabel('X')
plt.ylabel('Y')
plt.xlim(-2.2, 2.2)
plt.ylim(-2.2, 2.2)
plt.legend(['Traiettoria', 'Partenza', 'Target'])
plt.title('plane X,Y ')

plt.savefig('SimulationResults_0803/Position_2D_1.jpg')

Euler_angles_rad = Euler_angles * (np.pi / 180.)
for count in range(int(env.elapsed_time_steps/8)):

  figCount = 9+count

  fig = plt.figure(figCount)
  ax = fig.add_subplot(111, projection='3d')
  ax.plot_wireframe(np.array([info_X]), np.array([info_Y]), np.array([info_Z]))
  ax.invert_xaxis()
  ax.invert_zaxis()

  step_n = count * 8

  Phi, Theta, Psi = Euler_angles_rad[step_n, :]

  u_Xb = np.cos(Theta) * np.cos(Psi)
  v_Xb = np.cos(Theta) * np.sin(Psi)
  w_Xb = -np.sin(Theta)

  u_Yb = -np.cos(Phi) * np.sin(Psi) + np.sin(Phi) * np.sin(Theta) * np.cos(Psi)
  v_Yb = np.cos(Phi) * np.cos(Psi) + np.sin(Phi) * np.sin(Theta) * np.sin(Psi)
  w_Yb = np.sin(Phi) * np.cos(Theta)

  u_Zb = np.sin(Phi) * np.sin(Psi) + np.sin(Phi) * np.sin(Theta) * np.cos(Psi)
  v_Zb = -np.sin(Phi) * np.cos(Psi) + np.cos(Phi) * np.sin(Theta) * np.sin(Psi)
  w_Zb = np.cos(Phi) * np.cos(Theta)

  x = info_X[step_n]
  y = info_Y[step_n]
  z = info_Z[step_n]

  ax.quiver(x, y, z, u_Xb, v_Xb, w_Xb, length=0.5, normalize=False, color="red") # X_b
  ax.quiver(x, y, z, u_Yb, v_Yb, w_Yb, length=0.5, normalize=False, color="blue") #Y_b
  ax.quiver(x, y, z, u_Zb, v_Zb, w_Zb, length=0.5, normalize=False, color="green") #Z_b

  #ax.set_xlim3d(7.5, -7.5)

  ax.set_xlabel("North")
  ax.set_ylabel("East")
  ax.set_zlabel("Down")

  #ax.scatter(0, 0, -5, c="black", s=1.)
  #ax.scatter(15, 0, 0, c="black", s=1.)
  #ax.scatter(0, 15, 0, c="black", s=1.)
  #ax.scatter(0, 0, -20, c="black", s=1.)

  #plot the waypoint
  #ax.scatter(X_ref[step_n], Y_ref[step_n], Z_ref[step_n], c="red", s=100.)

  fig2save = 'SimulationResults_0803/Orientation/trajectory_1' + str(count) + '.jpg'

  plt.savefig(fig2save)
  n_fig = count


simout_array = np.stack([info_u, info_v, info_w, info_p, info_q, info_r, Euler_angles[:, 0], Euler_angles[:, 1], Euler_angles[:, 2], info_X, info_Y, info_Z], axis=1)

np.savetxt("simout_0803_1.txt", simout_array)

ref_array = np.stack([X_ref, Y_ref, Z_ref], axis=1)

np.savetxt("references_0803_1.txt", ref_array)