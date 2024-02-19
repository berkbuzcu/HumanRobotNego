"""
gwr-tb :: Episodic-GWR
@author: German I. Parisi (german.parisi@gmail.com)

@adapted: Nikhil Churamani (nc528)
@last-modified: Aug 25, 2021
"""

import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import math
from .gammagwr import GammaGWR
from .utils import concordance_correlation_coefficient

__metaclass__ = type
class EpisodicGWR(GammaGWR):

    def __init__(self):
        self.iterations = 0
    
    def init_network(self, ds, labels, num_context, max_nodes, age=600, av_delta=0.1, random=False):
        
        assert self.iterations < 1, "Can't initialize a trained network"
        assert ds is not None, "Need a dataset to initialize a network"
        
        # Lock to prevent training
        self.locked = False

        # Start with 2 neurons
        self.num_nodes = 2
        self.num_labels = 2
        self.dimension = ds.shape[1]
        self.num_context = num_context
        self.depth = self.num_context + 1
        empty_neuron = np.zeros((self.depth, self.dimension))
        self.weights = [empty_neuron, empty_neuron]
        
        # Global context
        self.g_context = np.zeros((self.depth, self.dimension))        
        
        # Create habituation counters
        self.habn = [1, 1]
        
        # Create edge and age matrices
        self.edges = np.ones((self.num_nodes, self.num_nodes))
        self.ages = np.zeros((self.num_nodes, self.num_nodes))
        
        # Temporal connections; needed for trajectories
        self.temporal = np.zeros((self.num_nodes, self.num_nodes))

        # Label histogram
        self.alabelsArousal = np.zeros(self.num_nodes)
        self.alabelsValence = np.zeros(self.num_nodes)
        # # Label histogram
        # self.num_labels = e_labels
        self.alabels = []
        # self.alabels.append(-np.ones((self.num_nodes, 2)))
        # Initialize weights
        self.random = random
        self.max_age =  age

        self.max_nodes = max_nodes


        if self.random:
            init_ind = np.random.randint(0, ds.shape[0], 2)
        else:
            init_ind = list(range(0, self.num_nodes))

        for i in range(0, len(init_ind)):
            self.weights[i] = ds[init_ind[i]]

        # Context coefficients

    def update_temporal(self, current_ind, previous_ind, **kwargs):
        new_node = kwargs.get('new_node', False)
        if new_node:
            self.temporal = super(EpisodicGWR, self).expand_matrix(self.temporal)
        if previous_ind != -1 and previous_ind != current_ind:
            self.temporal[previous_ind, current_ind] += 1

    def update_labels(self, bmu, label, **kwargs):
        new_node = kwargs.get('new_node', False)

        if not new_node:
            if self.alabelsArousal[bmu] < label[1]:
                self.alabelsArousal[bmu] += self.av_delta * self.alabelsArousal[bmu]
            else:
                self.alabelsArousal[bmu] -= self.av_delta * self.alabelsArousal[bmu]

            if self.alabelsValence[bmu] < label[0]:
                self.alabelsValence[bmu] += self.av_delta * self.alabelsValence[bmu]
            else:
                self.alabelsValence[bmu] -= self.av_delta * self.alabelsValence[bmu]
        else:

            self.alabelsArousal = np.concatenate((self.alabelsArousal, [label[1]]), axis=0)
            self.alabelsValence = np.concatenate((self.alabelsValence, [label[0]]), axis=0)

    def remove_isolated_nodes(self):
        ind_c = 0
        rem_c = 0
        while (ind_c < self.num_nodes):
            neighbours = np.nonzero(self.edges[ind_c])
            if len(neighbours[0]) < 1:
                if self.num_nodes > 2:
                    self.weights.pop(ind_c)
                    self.habn.pop(ind_c)
                    self.alabelsValence = np.delete(self.alabelsValence, ind_c, axis=0)
                    self.alabelsArousal = np.delete(self.alabelsArousal, ind_c, axis=0)
                    self.edges = np.delete(self.edges, ind_c, axis=0)
                    self.edges = np.delete(self.edges, ind_c, axis=1)
                    self.ages = np.delete(self.ages, ind_c, axis=0)
                    self.ages = np.delete(self.ages, ind_c, axis=1)
                    self.temporal = np.delete(self.temporal, ind_c, axis=0)
                    self.temporal = np.delete(self.temporal, ind_c, axis=1)
                    self.num_nodes -= 1
                    rem_c += 1
                else: return
            else:
                ind_c += 1
        #print("(-- Removed %s neuron(s))" % rem_c)


    def replay_samples(self, size):
        samples = np.zeros(size, dtype=int)
        r_weights = np.zeros((self.num_nodes, size, self.dimension))
        r_labels = np.zeros((self.num_nodes, 2, size))
        for i in range(0, self.num_nodes):
            for r in range(0, size):
                if r == 0:
                    samples[r] = i
                else:
                    samples[r] = np.argmax(self.temporal[int(samples[r - 1]), :])
                r_weights[i, r] = self.weights[int(samples[r])][0]
                r_labels[i, 0, r] = self.alabelsValence[int(samples[r])]
                r_labels[i, 1, r] = self.alabelsArousal[int(samples[r])]

        return r_weights, r_labels

    def train_egwr(self, ds_vectors, ds_labels, epochs, a_threshold, beta,
                   l_rates, context, regulated, hab_threshold=0.2, max_neighbours=6, again=False):
        
        assert not self.locked, "Network is locked. Unlock to train."

        if not again:
            self.samples = ds_vectors.shape[0]
        self.max_epochs = epochs
        self.a_threshold = a_threshold   
        self.epsilon_b, self.epsilon_n = l_rates
        self.beta = beta
        self.regulated = regulated
        self.context = context
        if not self.context:
            self.g_context.fill(0)
        self.hab_threshold = hab_threshold
        self.tau_b = 0.3
        self.tau_n = 0.1

        self.max_neighbors = max_neighbours
        self.new_node = 0.5
        self.a_inc = 1
        self.a_dec = 0.1
        self.mod_rate = 0.01
        self.misclassified_thresh = 0.3
        # self.alphas = self.compute_alphas(self.depth)
        self.av_delta = 0.1

        # Start training
        error_counter = np.zeros(self.max_epochs)
        previous_bmu = np.zeros((self.depth, self.dimension))
        previous_ind = -1
        for epoch in range(0, self.max_epochs):
            for iteration in range(0, self.samples):
                # Generate input sample
                self.g_context[0] = ds_vectors[iteration]
                label = ds_labels[iteration]

                # Update global context
                for z in range(1, self.depth):
                    self.g_context[z] = (self.beta * previous_bmu[z]) + ((1-self.beta) * previous_bmu[z-1])
                
                # Find the best and second-best matching neurons

                bmus = super(EpisodicGWR, self).find_bmus(self.g_context, s_best = True)
                b_index = bmus[0][1]
                s_index = bmus[1][1]
                b_distance = bmus[0][0]
                # b_label = np.argmax(self.alabels[0][b_index])
                b_label = [self.alabelsValence[b_index], self.alabelsArousal[b_index]]
                if np.linalg.norm(label-b_label) > self.misclassified_thresh:
                    misclassified = 1
                else:
                    misclassified = 0

                # Quantization error
                error_counter[epoch] += b_distance
                
                # Compute network activity
                a = math.exp(-b_distance)

                # Store BMU at time t for t+1
                previous_bmu = self.weights[b_index]

                if (not self.regulated) or (self.regulated and misclassified):
                    
                    if (a < self.a_threshold
                        and self.habn[b_index] < self.hab_threshold
                        and self.num_nodes < self.max_nodes):
                        # Add new neuron
                        n_index = self.num_nodes
                        super(EpisodicGWR, self).add_node(b_index)
                       
                        # Add label histogram           
                        self.update_labels(n_index, label, new_node=True)
    
                        # Update edges and ages
                        super(EpisodicGWR, self).update_edges(b_index, s_index, new_index=n_index)
                        
                        # Update temporal connections
                        self.update_temporal(n_index, previous_ind, new_node=True)
    
                        # Habituation counter                    
                        super(EpisodicGWR, self).habituate_node(n_index, self.tau_b, new_node=True)
                    
                    else:
                        # Habituate BMU
                        super(EpisodicGWR, self).habituate_node(b_index, self.tau_b)
    
                        # Update BMU's weight vector
                        b_rate, n_rate = self.epsilon_b, self.epsilon_n
                        if self.regulated and misclassified:
                            b_rate *= self.mod_rate
                            n_rate *= self.mod_rate
                        else:
                            # Update BMU's label histogram
                            self.update_labels(b_index, label)

                        # if imagined:
                        super(EpisodicGWR, self).update_weight(b_index, b_rate, a)
                        # else:
                        #     super(EpisodicGWR, self).update_weight(b_index, b_rate)
    
                        # Update BMU's edges // Remove BMU's oldest ones
                        super(EpisodicGWR, self).update_edges(b_index, s_index)
    
                        # Update temporal connections
                        self.update_temporal(b_index, previous_ind)
    
                        # Update BMU's neighbors
                        super(EpisodicGWR, self).update_neighbors(b_index, n_rate)
                        
                self.iterations += 1
                    
                previous_ind = b_index

            # Remove old edges
            super(EpisodicGWR, self).remove_old_edges()
            
            # Average quantization error (AQE)
            error_counter[epoch] /= self.samples
            
            #print("(Epoch: %s, NN: %s, ATQE: %s)" % (epoch + 1, self.num_nodes, error_counter[epoch]))
            
        # Remove isolated neurons
        self.remove_isolated_nodes()

    # def test(self, ds_vectors, ds_labels, **kwargs):
    #     test_accuracy = kwargs.get('test_accuracy', False)
    #     test_vecs = kwargs.get('ret_vecs', False)
    #     test_samples = ds_vectors.shape[0]
    #     self.bmus_index = -np.ones(test_samples)
    #     self.bmus_weight = np.zeros((test_samples, self.dimension))
    #     self.bmus_label = -np.ones((len(self.num_labels), test_samples))
    #     self.bmus_activation = np.zeros(test_samples)
    #
    #     input_context = np.zeros((self.depth, self.dimension))
    #
    #     if test_accuracy:
    #         acc_counter = np.zeros(len(self.num_labels))
    #
    #     for i in range(0, test_samples):
    #         input_context[0] = ds_vectors[i]
    #         # Find the BMU
    #         b_index, b_distance = super(EpisodicGWR, self).find_bmus(input_context)
    #         self.bmus_index[i] = b_index
    #         self.bmus_weight[i] = self.weights[b_index][0]
    #         self.bmus_activation[i] = math.exp(-b_distance)
    #         for l in range(0, len(self.num_labels)):
    #             self.bmus_label[l, i] = np.argmax(self.alabels[l][b_index])
    #
    #         for j in range(1, self.depth):
    #             input_context[j] = input_context[j-1]
    #
    #         if test_accuracy:
    #             for l in range(0, len(self.num_labels)):
    #                 if self.bmus_label[l, i] == ds_labels[l, i]:
    #                     acc_counter[l] += 1
    #
    #     if test_accuracy: self.test_accuracy =  acc_counter / ds_vectors.shape[0]
    #
    #     if test_vecs:
    #         s_labels = -np.ones((1, test_samples))
    #         if len(self.num_labels) > 1:
    #             s_labels[0] = self.bmus_label[1]
    #         else:
    #             s_labels[0] = self.bmus_label[0]
    #         return self.bmus_weight, s_labels
    #
    # def test_classifier(self, ds_vectors, ds_labels, classifier, **kwargs):
    #     test_accuracy = kwargs.get('test_accuracy', False)
    #     test_vecs = kwargs.get('ret_vecs', False)
    #     test_samples = ds_vectors.shape[0]
    #     self.bmus_index = -np.ones(test_samples)
    #     self.bmus_weight = np.zeros((test_samples, self.dimension))
    #     self.bmus_label = -np.ones((len(self.num_labels), test_samples))
    #     self.bmus_activation = np.zeros(test_samples)
    #
    #     input_context = np.zeros((self.depth, self.dimension))
    #
    #     if test_accuracy:
    #         acc_counter = np.zeros(len(self.num_labels))
    #
    #     for i in range(0, test_samples):
    #         input_context[0] = ds_vectors[i]
    #         # Find the BMU
    #         b_index, b_distance = super(EpisodicGWR, self).find_bmus(input_context)
    #         self.bmus_index[i] = b_index
    #         self.bmus_weight[i] = self.weights[b_index][0]
    #         self.bmus_activation[i] = math.exp(-b_distance)
    #
    #         for l in range(0, len(self.num_labels)):
    #             self.bmus_label[l, i] = np.argmax(
    #                 classifier.predict(np.array(self.bmus_weight[i]).reshape((1, self.dimension))))
    #
    #
    #         for j in range(1, self.depth):
    #             input_context[j] = input_context[j - 1]
    #
    #         if test_accuracy:
    #             for l in range(0, len(self.num_labels)):
    #                 if self.bmus_label[l, i] == ds_labels[l, i]:
    #                     acc_counter[l] += 1
    #
    #     if test_accuracy: self.test_accuracy = acc_counter / ds_vectors.shape[0]
    #
    #     if test_vecs:
    #         s_labels = -np.ones((1, test_samples))
    #         if len(self.num_labels) > 1:
    #             s_labels[0] = self.bmus_label[1]
    #         else:
    #             s_labels[0] = self.bmus_label[0]
    #         return self.bmus_weight, s_labels

    def annotate(self, ds_vectors):
        test_samples = ds_vectors.shape[0]
        self.bmus_index = -np.ones(test_samples)
        self.bmus_weight = np.zeros((test_samples, self.dimension))

        input_context = np.zeros((self.depth, self.dimension))
        arousals, valences = [], []
        for i in range(0, ds_vectors.shape[0]):
            input_context[0] = ds_vectors[i]
            # Find the BMU
            b_index, _ = super(EpisodicGWR, self).find_bmus(input_context)
            self.bmus_index[i] = b_index
            self.bmus_weight[i] = self.weights[b_index][0]
            for j in range(1, self.depth):
                input_context[j] = input_context[j - 1]
            try:
                valences.append(np.round(self.alabelsValence[b_index]), 3)
                arousals.append(np.round(self.alabelsArousal[b_index]), 3)
            except:
                valences.append(self.alabelsValence[b_index])
                arousals.append(self.alabelsArousal[b_index])
        valences = [min(1, max(-1, valences[i])) for i in range(len(valences))]
        arousals = [min(1, max(-1, arousals[i])) for i in range(len(arousals))]
        return arousals, valences

    def test_av(self, ds_vectors, ds_labels, test_accuracy=False):
        test_samples = ds_vectors.shape[0]
        self.bmus_index = -np.ones(test_samples)
        self.bmus_weight = np.zeros((test_samples, self.dimension))

        input_context = np.zeros((self.depth, self.dimension))
        arousals, valences = [], []
        for i in range(0, ds_vectors.shape[0]):
            input_context[0] = ds_vectors[i]
            # Find the BMU
            b_index, b_distance = super(EpisodicGWR, self).find_bmus(input_context)
            self.bmus_index[i] = b_index
            self.bmus_weight[i] = self.weights[b_index][0]
            for j in range(1, self.depth):
                input_context[j] = input_context[j - 1]
            valences.append(self.alabelsValence[b_index])
            arousals.append(self.alabelsArousal[b_index])
        if test_accuracy:
            ccc_a, ccc_v, rmse_a, rmse_v = -1, -1, -1, -1

            ccc_v = np.round(concordance_correlation_coefficient(ds_labels[:, 0], valences), 2)
            ccc_a = np.round(concordance_correlation_coefficient(ds_labels[:, 1], arousals), 2)

            # rmse_a = mean_squared_error(ds_labels[0, :], arousals, squared=False)
            # rmse_v = mean_squared_error(ds_labels[1, :], valences, squared=False)

            return self.bmus_weight, [ccc_a, ccc_v], np.hstack([np.array(valences).reshape((len(valences), 1)),
                                                                np.array(arousals).reshape((len(arousals), 1))])
        return self.bmus_weight,  np.hstack([np.array(valences).reshape((len(valences), 1)),
                                             np.array(arousals).reshape((len(arousals), 1))])
