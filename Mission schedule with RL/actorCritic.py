#######################################################################
# Copyright (C)                                                       #
# 2016 - 2019 Pinard Liu(liujianping-ok@163.com)                      #
# https://www.cnblogs.com/pinard                                      #
# Permission given to modify the code as long as you keep this        #
# declaration at the top                                              #
#######################################################################
## https://www.cnblogs.com/pinard/p/10272023.html ##
## 强化学习(十四) Actor-Critic ##
import matplotlib.pyplot as plt
import gym
import tensorflow as tf
import numpy as np
import random
from collections import deque
import RemainingTimeTotalModule
import globalVariableLocal as globalVariable
import myEnvLocal as myEnv

# Hyper Parameters
GAMMA = 0.9 # discount factor
LEARNING_RATE=0.001

class Actor():
    def __init__(self, env, sess):
        # init some parameters
        self.time_step = 0
        self.state_dim = env.observation_space.n
        self.action_dim = env.action_space.n
        self.create_softmax_network()

        # Init session
        self.session = sess
        self.session.run(tf.global_variables_initializer())

    def create_softmax_network(self):
        # network weights
        W1 = self.weight_variable([self.state_dim, 20])
        b1 = self.bias_variable([20])
        W2 = self.weight_variable([20, self.action_dim])
        b2 = self.bias_variable([self.action_dim])
        # input layer
        self.state_input = tf.placeholder("float", [None, self.state_dim])
        self.tf_acts = tf.placeholder(tf.int32, [None,2], name="actions_num")
        self.td_error = tf.placeholder(tf.float32, None, "td_error")  # TD_error
        # hidden layers
        h_layer = tf.nn.relu(tf.matmul(self.state_input, W1) + b1)
        # softmax layer
        self.softmax_input = tf.matmul(h_layer, W2) + b2
        # softmax output
        self.all_act_prob = tf.nn.softmax(self.softmax_input, name='act_prob')

        self.neg_log_prob = tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.softmax_input,
                                                                           labels=self.tf_acts)
        self.exp = tf.reduce_mean(self.neg_log_prob * self.td_error)

        #这里需要最大化当前策略的价值，因此需要最大化self.exp,即最小化-self.exp
        self.train_op = tf.train.AdamOptimizer(LEARNING_RATE).minimize(-self.exp)

    def weight_variable(self, shape):
        initial = tf.truncated_normal(shape)
        return tf.Variable(initial)

    def bias_variable(self, shape):
        initial = tf.constant(0.0, shape=shape)
        return tf.Variable(initial)

    def choose_action(self, observation):
        prob_weights = self.session.run(self.all_act_prob, feed_dict={self.state_input: observation[np.newaxis, :]})
        print('prob_weights', prob_weights)
        action = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())  # select action w.r.t the actions prob
        print('action',action)
        return action

    def choose_action_greedy(self, observation):
        prob_weights = self.session.run(self.all_act_prob, feed_dict={self.state_input: observation[np.newaxis, :]})
        p = prob_weights.ravel().tolist()
        action=p.index(max(p))
        # action = np.random.choice(range(prob_weights.shape[1]), p=prob_weights.ravel())  # select action w.r.t the actions prob
        return action

    def learn(self, state, action, td_error):
        s = state[np.newaxis, :]
        one_hot_action = np.zeros(self.action_dim)
        one_hot_action[action] = 1
        a = one_hot_action[np.newaxis, :]
        # train on episode
        self.session.run(self.train_op, feed_dict={
             self.state_input: s,
             self.tf_acts: a,
             self.td_error: td_error,
        })

EPSILON = 0.01 # final value of epsilon
REPLAY_SIZE = 10000 # experience replay buffer size
BATCH_SIZE = 32 # size of minibatch
REPLACE_TARGET_FREQ = 10 # frequency to update target Q network

class Critic():
    def __init__(self, env, sess):
        # init some parameters
        self.time_step = 0
        self.epsilon = EPSILON
        self.state_dim = env.observation_space.n
        self.action_dim = env.action_space.n

        self.create_Q_network()
        self.create_training_method()

        # Init session
        self.session = sess
        self.session.run(tf.global_variables_initializer())

    def create_Q_network(self):
        # network weights
        W1q = self.weight_variable([self.state_dim, 20])
        b1q = self.bias_variable([20])
        W2q = self.weight_variable([20, 1])
        b2q = self.bias_variable([1])
        self.state_input = tf.placeholder(tf.float32, [1, self.state_dim], "state")
        # hidden layers
        h_layerq = tf.nn.relu(tf.matmul(self.state_input, W1q) + b1q)
        # Q Value layer
        self.Q_value = tf.matmul(h_layerq, W2q) + b2q

    def create_training_method(self):
        self.next_value = tf.placeholder(tf.float32, [1,1], "v_next")
        self.reward = tf.placeholder(tf.float32, None, 'reward')

        with tf.variable_scope('squared_TD_error'):
            self.td_error = self.reward + GAMMA * self.next_value - self.Q_value
            self.loss = tf.square(self.td_error)
        with tf.variable_scope('train'):
            self.train_op = tf.train.AdamOptimizer(self.epsilon).minimize(self.loss)

    def train_Q_network(self, state, reward, next_state):
        s, s_ = state[np.newaxis, :], next_state[np.newaxis, :]
        v_ = self.session.run(self.Q_value, {self.state_input: s_})
        td_error, _ = self.session.run([self.td_error, self.train_op],
                                          {self.state_input: s, self.next_value: v_, self.reward: reward})
        return td_error

    def weight_variable(self,shape):
        initial = tf.truncated_normal(shape)
        return tf.Variable(initial)

    def bias_variable(self,shape):
        initial = tf.constant(0.01, shape = shape)
        return tf.Variable(initial)

# Hyper Parameters
ENV_NAME = 'CartPole-v0'
EPISODE = 1000 # Episode limitation
STEP = 6 # Step limitation in an episode
TEST = 10 # The number of experiment test every 100 episode

def main():
    # 在总的学习开始前初始化时间窗口存储器
  globalVariable.initTask()
  RemainingTimeTotalModule.initRemainingTimeTotal()
  # globalVariable.initsatState()


  # initialize OpenAI Gym env and dqn agent
  sess = tf.InteractiveSession()
  env = myEnv.MyEnv()#导入自我编写环境
  actor = Actor(env, sess)
  critic = Critic(env, sess)
  ax = []
  ay = []
  for episode in range(EPISODE):
    # initialize task
    # initialize task
    ep_r=0

    globalVariable.initTasklist()  # 每个episode开始前都初始化Tasklist
    state = env.reset()
    # Train
    for step in range(STEP):
      print('state',state)
      action = actor.choose_action(state) # e-greedy action for train
      next_state,reward,done,_ = env.step(action)
      td_error = critic.train_Q_network(state, reward, next_state)  # gradient = grad[r + gamma * V(s_) - V(s)]
      actor.learn(state, action, td_error)  # true_gradient = grad[logPi(s,a) * td_error]
      #每一步都学习，而不是像PG一样只在跑完一个episode后学习
      state = next_state
      ep_r += reward
      if done:
          break
    ax.append(episode)  # 添加 i 到 x 轴的数据中
    ay.append(ep_r)  # 添加 i 的平方到 y 轴的数据中
    plt.clf()  # 清除之前画的图
    plt.plot(ax, ay)  # 画出当前 ax 列表和 ay 列表中的值的图形
    plt.pause(0.1)  # 暂停一秒
    plt.ioff()
    # # Test every 100 episodes
    # if episode % 100 == 0:
    #   total_reward = 0
    #   for i in range(TEST):
    #     state = env.reset()
    #     for j in range(STEP):
    #       env.render()
    #       action = actor.choose_action(state) # direct action for test
    #       state,reward,done,_ = env.step(action)
    #       total_reward += reward
    #       if done:
    #         break
    #   ave_reward = total_reward/TEST
    #   print ('episode: ',episode,'Evaluation Average Reward:',ave_reward)

  state = env.reset()
  globalVariable.initTasklist()
  for j in range(STEP):
      # env.render()

      action = actor.choose_action_greedy(state)
      print('Task', state[1], 'action', action)
      state, reward, done, _ = env.step(action)
      if done:
          # print(total_reward)
          break


if __name__ == '__main__':
  main()