import tensorflow as tf
import numpy as np

from Model import Model


class DQN:
    def __init__(self, model: Model, gamma=0.9, learnging_rate=0.0001):
        self.model = model
        self.actionTypes = model.actionTypes
        self.actionModel = model.actionModel
        self.moveModel = model.moveModel
        self.gamma = gamma
        self.lr = learnging_rate
        # --------------------------训练模型--------------------------- #
        self.actionModel.optimizer = tf.optimizers.Adam(learning_rate=self.lr)
        self.actionModel.loss_func = tf.losses.MeanSquaredError()

        self.moveModel.optimizer = tf.optimizers.Adam(learning_rate=self.lr)
        self.moveModel.loss_func = tf.losses.MeanSquaredError()
        # self.act_model.train_loss = tf.metrics.Mean(name="train_loss")
        # ------------------------------------------------------------ #
        self.act_global_step = 0
        self.move_global_step = 0
        self.update_target_steps = 100  # 每隔200个training steps再把model的参数复制到target_model中

    # train functions for act model
    def act_predict(self, obs):
        """ 使用self.act_model的value网络来获取 [Q(s,a1),Q(s,a2),...]
        """
        return self.actionModel.predict(obs)

    def act_train_step(self, action, features, labels):
        """ 训练步骤
        """
        with tf.GradientTape() as tape:
            # 计算 Q(s,a) 与 target_Q的均方差，得到loss
            predictions = self.actionModel(features, training=True)
            enum_action = list(enumerate(action))
            pred_action_value = tf.gather_nd(predictions, indices=enum_action)
            loss = self.actionModel.loss_func(labels, pred_action_value)
        gradients = tape.gradient(loss, self.actionModel.trainable_variables)
        self.actionModel.optimizer.apply_gradients(
            zip(gradients, self.actionModel.trainable_variables))
        self.model.act_loss.append(loss)
        # self.act_model.train_loss.update_state(loss)

    def trainActionModel(self, action, features, labels, epochs=1):
        """ 训练模型
        """
        for epoch in tf.range(1, epochs+1):
            self.act_train_step(action, features, labels)

    def actionLearn(self, obs, action, reward, next_obs, terminal):
        """ 使用DQN算法更新self.act_model的value网络
        """
        # print('learning')
        # 每隔200个training steps同步一次model和target_model的参数
        # if self.act_global_step % self.update_target_steps == 0:
        #     self.act_replace_target()

        # 从target_model中获取 max Q' 的值，用于计算target_Q

        self.trainActionModel(action, obs, reward, epochs=1)
        self.act_global_step += 1
        # print('finish')

    def actionTargetUpdate(self):
        '''预测模型权重更新到target模型权重'''
        for i, l in enumerate(self.act_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=0).get_layers()):
            l.set_weights(self.actionModel.get_layer(index=1).get_layer(
                index=0).get_layer(index=0).get_layer(index=i).get_weights())
        for i, l in enumerate(self.act_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=1).get_layers()):
            l.set_weights(self.actionModel.get_layer(index=1).get_layer(
                index=0).get_layer(index=1).get_layer(index=i).get_weights())

        # for i, l in enumerate(self.act_target_model.get_layer(index=1).get_layer(index=1).get_layer(index=0).get_layers()):
        #     l.set_weights(self.act_model.get_layer(index=1).get_layer(index=1).get_layer(index=0).get_layer(index=i).get_weights())
        # for i, l in enumerate(self.act_target_model.get_layer(index=1).get_layer(index=1).get_layer(index=1).get_layers()):
        #     l.set_weights(self.act_model.get_layer(index=1).get_layer(index=1).get_layer(index=1).get_layer(index=i).get_weights())

        # for i, l in enumerate(self.act_target_model.get_layer(index=1).get_layer(index=2).get_layer(index=0).get_layers()):
        #     l.set_weights(self.act_model.get_layer(index=1).get_layer(index=2).get_layer(index=0).get_layer(index=i).get_weights())
        # for i, l in enumerate(self.act_target_model.get_layer(index=1).get_layer(index=2).get_layer(index=1).get_layers()):
        #     l.set_weights(self.act_model.get_layer(index=1).get_layer(index=2).get_layer(index=1).get_layer(index=i).get_weights())

        self.act_target_model.get_layer(index=1).get_layer(index=2).set_weights(
            self.actionModel.get_layer(index=1).get_layer(index=2).get_weights())

        # self.act_target_model.get_layer(index=1).get_layer(index=6).set_weights(self.act_model.get_layer(index=1).get_layer(index=6).get_weights())

    # train functions for move_model

    def move_predict(self, obs):
        """ 使用self.move_model的value网络来获取 [Q(s,a1),Q(s,a2),...]
        """
        return self.moveModel.predict(obs)

    def move_train_step(self, action, features, labels):
        """ 训练步骤
        """
        with tf.GradientTape() as tape:
            # 计算 Q(s,a) 与 target_Q的均方差，得到loss
            predictions = self.moveModel(features, training=True)
            enum_action = list(enumerate(action))
            pred_action_value = tf.gather_nd(predictions, indices=enum_action)
            loss = self.moveModel.loss_func(labels, pred_action_value)
        gradients = tape.gradient(loss, self.moveModel.trainable_variables)
        self.moveModel.optimizer.apply_gradients(
            zip(gradients, self.moveModel.trainable_variables))
        self.model.move_loss.append(loss)
        # self.move_plot_loss()
        # print("Move loss: ", loss)
        # self.move_model.train_loss.update_state(loss)

    def move_train_model(self, action, features, labels, epochs=1):
        """ 训练模型
        """
        for epoch in tf.range(1, epochs+1):
            self.move_train_step(action, features, labels)

    def move_learn(self, obs, action, reward, next_obs, terminal):
        """ 使用DQN算法更新self.move_model的value网络
        """
        self.move_train_model(action, obs, reward, epochs=1)
        self.move_global_step += 1

    def move_replace_target(self):
        '''预测模型权重更新到target模型权重'''

        for i, l in enumerate(self.move_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=0).get_layers()):
            l.set_weights(self.moveModel.get_layer(index=1).get_layer(
                index=0).get_layer(index=0).get_layer(index=i).get_weights())
        for i, l in enumerate(self.move_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=1).get_layers()):
            l.set_weights(self.moveModel.get_layer(index=1).get_layer(
                index=0).get_layer(index=1).get_layer(index=i).get_weights())

        # for i, l in enumerate(self.move_target_model.get_layer(index=1).get_layer(index=1).get_layer(index=0).get_layers()):
        #     l.set_weights(self.move_model.get_layer(index=1).get_layer(index=1).get_layer(index=0).get_layer(index=i).get_weights())
        # for i, l in enumerate(self.move_target_model.get_layer(index=1).get_layer(index=1).get_layer(index=1).get_layers()):
        #     l.set_weights(self.move_model.get_layer(index=1).get_layer(index=1).get_layer(index=1).get_layer(index=i).get_weights())

        # for i, l in enumerate(self.move_target_model.get_layer(index=1).get_layer(index=2).get_layer(index=0).get_layers()):
        #     l.set_weights(self.move_model.get_layer(index=1).get_layer(index=2).get_layer(index=0).get_layer(index=i).get_weights())
        # for i, l in enumerate(self.move_target_model.get_layer(index=1).get_layer(index=2).get_layer(index=1).get_layers()):
        #     l.set_weights(self.move_model.get_layer(index=1).get_layer(index=2).get_layer(index=1).get_layer(index=i).get_weights())

        self.move_target_model.get_layer(index=1).get_layer(index=2).set_weights(
            self.moveModel.get_layer(index=1).get_layer(index=2).get_weights())

        # self.move_target_model.get_layer(index=1).get_layer(index=6).set_weights(self.move_model.get_layer(index=1).get_layer(index=6).get_weights())

    def replace_target(self):
        # print("replace target")

        # copy conv3d_1
        self.model.shared_target_model.get_layer(index=0).set_weights(
            self.model.shared_model.get_layer(index=0).get_weights())
        # copy batchnormalization_1
        self.model.shared_target_model.get_layer(index=1).set_weights(
            self.model.shared_model.get_layer(index=1).get_weights())

        # copy shard_resnet block
        for i, l in enumerate(self.model.shared_target_model.get_layer(index=4).get_layer(index=0).get_layers()):
            l.set_weights(self.model.shared_model.get_layer(
                index=4).get_layer(index=0).get_layer(index=i).get_weights())
        for i, l in enumerate(self.model.shared_target_model.get_layer(index=4).get_layer(index=1).get_layers()):
            l.set_weights(self.model.shared_model.get_layer(
                index=4).get_layer(index=1).get_layer(index=i).get_weights())

        for i, l in enumerate(self.model.shared_target_model.get_layer(index=5).get_layer(index=0).get_layers()):
            l.set_weights(self.model.shared_model.get_layer(
                index=5).get_layer(index=0).get_layer(index=i).get_weights())
        for i, l in enumerate(self.model.shared_target_model.get_layer(index=5).get_layer(index=1).get_layers()):
            l.set_weights(self.model.shared_model.get_layer(
                index=5).get_layer(index=1).get_layer(index=i).get_weights())

        self.move_replace_target()
        self.actionTargetUpdate()
