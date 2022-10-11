"""
gwr-tb :: Gamma-GWR based on Marsland et al. (2002)'s Grow-When-Required network
@author: German I. Parisi (german.parisi@gmail.com)
@last-modified: 25 August 2021
@author: Nikhil Churamani (nc528)
"""

import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import math
from heapq import nsmallest
from sklearn.metrics.pairwise import cosine_distances, paired_euclidean_distances
from typing import Tuple, Union, Callable, Any
__metaclass__ = type
class GammaGWR(object):

    def __init__(self):
        self.iterations = 0
        
    def compute_alphas(self, num_coeff):
        alpha_w = np.zeros(num_coeff)
        for h in range(0, len(alpha_w)):
            alpha_w[h] = np.exp(-h)
        alpha_w[:] = alpha_w[:] / sum(alpha_w)
        return alpha_w

    def compute_distance(self, x, y, type='euc'):
        # return np.linalg.norm(np.dot(self.alphas.T, (x-y)))
        if type.startswith('euc'):
            # return np.linalg.norm(np.dot(self.alphas.T, (paired_euclidean_distances(x,y))))
            return np.linalg.norm(x - y)
            # return np.linalg.norm(np.dot(self.alphas.T, (x-y)))

        else:
            return np.linalg.norm(np.dot(self.alphas.T, (cosine_distances(x, y))))

    def find_bs(self, dis, winners):
        bs = nsmallest(winners, ((k, i) for i, k in enumerate(dis)))
        return bs

    def find_bmus(self, input_vector, **kwargs):
        second_best = kwargs.get('s_best', False)
        winners = kwargs.get('winners', 2)

        distances = np.zeros(self.num_nodes)
        for i in range(0, self.num_nodes):
            if len(self.weights[i].shape) < 2:
                self.weights[i] = np.expand_dims(self.weights[i], axis=0)
            distances[i] = self.compute_distance(self.weights[i], input_vector)
        if second_best:
            # Compute best and second-best matching units
            BMUs = self.find_bs(distances, winners)
            return BMUs
        else:
            b_index = distances.argmin()
            b_distance = distances[b_index]
            return b_index, b_distance

    def expand_matrix(self, matrix):
        ext_matrix = np.hstack((matrix, np.zeros((matrix.shape[0], 1))))
        ext_matrix = np.vstack((ext_matrix, np.zeros((1, ext_matrix.shape[1]))))
        return ext_matrix

    def init_network(self, ds, random, **kwargs):
        
        assert self.iterations < 1, "Can't initialize a trained network"
        assert ds is not None, "Need a dataset to initialize a network"

        # ds is the dataset used to train the model
        # ds.shape --> [numberOfDatapoints, data_dimensionality]

        # Lock to prevent training
        self.locked = False
        
        # Start with 2 neurons
        self.num_nodes = 2
        self.dimension = ds.shape[1]
        self.num_context = kwargs.get('num_context', 0)
        self.depth = self.num_context + 1
        empty_neuron = np.zeros((self.depth, self.dimension))
        self.weights = [empty_neuron, empty_neuron]
        
        # Global context
        self.g_context = np.zeros((self.depth, self.dimension))        
        # Depth represents the time look-back (K for K-filtering) and dimension is for the weight of the neuron

        # Create habituation counters (start at 1 and decrease as the training progresses)
        self.habn = [1, 1]
        
        # Create edge and age matrices
        self.edges = np.ones((self.num_nodes, self.num_nodes))
        self.ages = np.zeros((self.num_nodes, self.num_nodes))
        # Edges are the connections between neurons and age is the age of that connection (how many fires)

        # Label histograms
        empty_label_hist = -np.ones(ds.num_classes)
        self.alabels = [empty_label_hist, empty_label_hist]
        
        # Initialize weights
        self.random = random

        # If random, set the weights equal to any two datapoints
        if self.random: init_ind = np.random.randint(0, ds.shape[0], 2)
        else: init_ind = list(range(0, self.num_nodes))
        for i in range(0, len(init_ind)):
            self.weights[i] = ds[init_ind[i]]
            self.alabels[i][int(ds.labels[i])] = 1
            # print(self.weights[i])
            
        # Context coefficients
        self.alphas = self.compute_alphas(self.depth)
        
    def add_node(self, b_index):
        # Summing last winner neuron and the global context and modulating with new_node factor (here 0.5)
        new_neuron = np.array(np.dot(self.weights[b_index] + self.g_context, self.new_node))
        self.weights.append(new_neuron)
        self.num_nodes += 1

    def update_weight(self, index, epsilon, act=None):
        delta = np.dot((self.g_context - self.weights[index]), (epsilon * self.habn[index]))
        if act is not None:
            delta = np.dot(delta,(1-act))
        self.weights[index] = self.weights[index] + delta
        # self.weights[index] /= np.max(self.weights[index])

    def habituate_node(self, index, tau, **kwargs):
        new_node = kwargs.get('new_node', False)
        if not new_node:
            self.habn[index] += tau * 1.05 * (1 - self.habn[index]) - tau
        else:
            self.habn.append(1)
            
    def update_neighbors(self, index, epsilon):
        b_neighbors = np.nonzero(self.edges[index])
        for z in range(0, len(b_neighbors[0])):
            neIndex = b_neighbors[0][z]
            self.update_weight(neIndex, epsilon)
            self.habituate_node(neIndex, self.tau_n, new_node=False)
 
    def update_labels(self, bmu, label, **kwargs):
        new_node = kwargs.get('new_node', False)
        if not new_node:
            for a in range(0, self.num_classes):
                if a == label:
                    self.alabels[bmu][a] += self.a_inc
                else:
                    if label != -1:
                        self.alabels[bmu][a] -= self.a_dec
                        if (self.alabels[bmu][a] < 0):
                            self.alabels[bmu][a] = 0
        else:
            new_alabel = np.zeros(self.num_classes)
            if label != -1:
                new_alabel[int(label)] = self.a_inc
            self.alabels.append(new_alabel)
                            
    def update_edges(self, fi, si, **kwargs):
        new_index = kwargs.get('new_index', False)
        self.ages += 1
        if not new_index:
            self.edges[fi, si] = 1  
            self.edges[si, fi] = 1
            self.ages[fi, si] = 0
            self.ages[si, fi] = 0
        else:
            self.edges = self.expand_matrix(self.edges)
            self.ages = self.expand_matrix(self.ages)
            self.edges[fi, si] = 0
            self.edges[si, fi] = 0
            self.ages[fi, si] = 0
            self.ages[si, fi] = 0
            self.edges[fi, new_index] = 1
            self.edges[new_index, fi] = 1
            self.edges[si, new_index] = 1
            self.edges[new_index, si] = 1
      
    def remove_old_edges(self):
        for i in range(0, self.num_nodes):
            neighbours = np.nonzero(self.edges[i])
            for j in neighbours[0]:
                if self.ages[i, j] >  self.max_age:
                    self.edges[i, j] = 0
                    self.edges[j, i] = 0
                    self.ages[i, j] = 0
                    self.ages[j, i] = 0
                              
    def remove_isolated_nodes(self):
        if self.num_nodes > 2:
            ind_c = 0
            rem_c = 0
            while (ind_c < self.num_nodes):
                neighbours = np.nonzero(self.edges[ind_c])
                if len(neighbours[0]) < 1:
                    self.weights.pop(ind_c)
                    self.alabels.pop(ind_c)
                    self.habn.pop(ind_c)
                    self.edges = np.delete(self.edges, ind_c, axis=0)
                    self.edges = np.delete(self.edges, ind_c, axis=1)
                    self.ages = np.delete(self.ages, ind_c, axis=0)
                    self.ages = np.delete(self.ages, ind_c, axis=1)
                    self.num_nodes -= 1
                    rem_c += 1
                else:
                    ind_c += 1
            #print("(-- Removed %s neuron(s))" % rem_c)
                
    def train_ggwr(self, ds, epochs, a_threshold, beta, l_rates):
        
        assert not self.locked, "Network is locked. Unlock to train."
        assert ds.vectors.shape[1] == self.dimension, "Wrong dimensionality"
        
        self.samples = ds.vectors.shape[0]
        self.max_epochs = epochs
        self.a_threshold = a_threshold                      # Activation Threshold
        self.epsilon_b, self.epsilon_n = l_rates
        self.beta = beta
        
        self.hab_threshold = 0.1                            # How much to habituate a singe neuron before adding new
        self.tau_b = 0.3
        self.tau_n = 0.1
        self.max_nodes = self.samples                       # OK for batch, bad for incremental
        self.max_neighbors = 10
        self.max_age = ds.vectors.shape[0] * 2
        self.new_node = 0.5
        self.num_classes = ds.num_classes
        self.a_inc = 1
        self.a_dec = 0.1
  
        # Start training
        error_counter = np.zeros(self.max_epochs)
        previous_bmu = np.zeros((self.depth, self.dimension))
        
        for epoch in range(0, self.max_epochs):
            
            for iteration in range(0, self.samples):
                
                # Generate input sample
                self.g_context[0] = ds.vectors[iteration]
                label = ds.labels[iteration]
                
                # Update global context
                for z in range(1, self.depth):
                    self.g_context[z] = (self.beta * previous_bmu[z]) + ((1-self.beta) * previous_bmu[z-1])
                
                # Find the best and second-best matching neurons
                bmus = self.find_bmus(self.g_context, s_best = True, winners=5)
                b_index = bmus[0][1]
                s_index = bmus[0][1]
                b_distance = bmus[1][1]

                # Quantization error
                error_counter[epoch] += b_distance
                
                # Compute network activity
                activation = math.exp(-b_distance)

                # Store BMU at time t for t+1
                previous_bmu = self.weights[b_index]
                
                if (activation < self.a_threshold
                    and self.habn[b_index] < self.hab_threshold
                    and self.num_nodes < self.max_nodes):
                   
                    # Add new neuron
                    n_index = self.num_nodes
                    self.add_node(b_index)
                   
                    # Add label histogram
                    self.update_labels(n_index, label, new_node = True)                   

                    # Update edges and ages
                    self.update_edges(b_index, s_index, new_index = n_index)

                    # Habituation counter                    
                    self.habituate_node(n_index, self.tau_b, new_node = True)
                    
                else:
                    # Habituate BMU
                    self.habituate_node(b_index, self.tau_b)

                    # Update BMU's weight vector
                    self.update_weight(b_index, self.epsilon_b)

                    # Update BMU's edges // Remove BMU's oldest ones
                    self.update_edges(b_index, s_index) 

                    # Update BMU's neighbors
                    self.update_neighbors(b_index, self.epsilon_n)
                    
                    # Update BMU's label histogram
                    self.update_labels(b_index, label)
                    
                self.iterations += 1

            # Remove old edges
            self.remove_old_edges()
            
            # Average quantization error (AQE)
            error_counter[epoch] /= self.samples
            
            #print("(Epoch: %s, NN: %s, ATQE: %s)" %
                   # (epoch + 1, self.num_nodes, error_counter[epoch]))
            
        # Remove isolated neurons
        self.remove_isolated_nodes()

    def test_gammagwr(self, test_ds, **kwargs):
        test_accuracy = kwargs.get('test_accuracy', None)
        self.bmus_index = -np.ones(self.samples)
        self.bmus_label = -np.ones(self.samples)
        self.bmus_activation = np.zeros(self.samples)
        
        input_context = np.zeros((self.depth, self.dimension))
        
        if test_accuracy: acc_counter = 0
        
        for i in range(0, test_ds.vectors.shape[0]):
            input_context[0] = test_ds.vectors[i]
            
            # Find the BMU
            b_index, b_distance = self.find_bmus(input_context)
            self.bmus_index[i] = b_index
            self.bmus_activation[i] = math.exp(-b_distance)
            self.bmus_label[i] = np.argmax(self.alabels[b_index])
            
            for j in range(1, self.depth):
                input_context[j] = input_context[j-1]
            
            if test_accuracy:
                if self.bmus_label[i] == test_ds.labels[i]:
                    acc_counter += 1

        if test_accuracy:
            self.test_accuracy = acc_counter / test_ds.vectors.shape[0]
