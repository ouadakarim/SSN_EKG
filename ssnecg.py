# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import sys
from keras.layers import Input, Dense
from keras.models import Model, Sequential, load_model
from keras.optimizers import SGD

TRAIN_SIGNALS = 150
TEST_SIGNALS = 50

class SSNECG:
	_db_f = (np.load("data/filtered.npy").astype(np.float32)+350)/700
	_db_u = (np.load("data/unfiltered.npy").astype(np.float32)+350)/700
	_x_train = None
	_x_test = None

	def __init__(self):
		assert(self._db_f.shape == self._db_u.shape)
		self.model = None
		self.structure = []
		self.frame_size = 0

	def new(self, structure, lr=0.5):
		self.structure = structure
		self.frame_size = structure[0]
		self.model = Sequential()
		self.model.add(self._build_encoder())
		self.model.add(self._build_decoder())
		sgd = SGD(lr=lr, decay=1e-6, momentum=0.9, nesterov=True)
		self.model.compile(optimizer=sgd, loss='mse')
		self._x_train = self._make_set_from_db(0, TRAIN_SIGNALS)
		self._x_test = self._make_set_from_db(TRAIN_SIGNALS, TEST_SIGNALS)

	def load(self, filename):
		self.model = load_model(filename)
		self.structure = [l.output_shape[1] for l in self.model.layers[0].layers]
		self.frame_size = self.structure[0]
		self._x_train = (self._make_set_from_db(0, TRAIN_SIGNALS).astype(np.float32)+350)/700
		self._x_test = (self._make_set_from_db(TRAIN_SIGNALS, TEST_SIGNALS).astype(np.float32)+350)/700

	def save(self, filename=None):
		assert(self.model)
		if not filename:
			filename = '-'.join([str(i) for i in self.structure])+'.h5'
		else:
			filename += '.h5'
		self.model.save(filename)
	
	def train(self, epochs):
		assert(self.model)
		self.model.fit(self._x_train, self._x_train, epochs=epochs, batch_size=2048, validation_data=(self._x_test, self._x_test))
	
	def compress(self, signo, ugly=False):
		assert(self.model)
		inp=self.get_signal(signo, ugly=ugly).reshape((-1, self.frame_size))
		out=self.model.layers[0].predict(inp)
		return out.reshape((np.prod(out.shape)))

	def decompress(self, compressed):
		assert(self.model)
		inp=compressed.reshape((-1, self.structure[-1]))
		out=self.model.layers[1].predict(inp)
		return out.reshape((np.prod(out.shape)))

	def get_signal(self, signo, ugly=False):
		surplus=0
		if self.frame_size>0:
			surplus = -(self._db_f.shape[1]%self.frame_size)
		if surplus==0:
			surplus=None
		if ugly:
			return self._db_u[signo, :surplus]
		else:
			return self._db_f[signo, :surplus]

	def _build_encoder(self):
		inp = Input(shape=(self.frame_size,))
		x=inp
		for l in self.structure[1:]:
			x=Dense(l, activation='relu')(x)
		return Model(inp, x)
	
	def _build_decoder(self):
		inp = Input(shape=(self.structure[-1],))
		x=inp
		for l in self.structure[-2:0:-1]:
			x=Dense(l, activation='relu')(x)
		x = Dense(self.structure[0], activation='sigmoid')(x)
		return Model(inp, x)

	def _make_set_from_db(self, offset, number):
		frames_per_signal = self._db_f.shape[1]//self.frame_size
		surplus = -(self._db_f.shape[1]%self.frame_size)
		if surplus==0:
			surplus = None
		return np.reshape(self._db_f[offset:offset+number, :surplus], (number*frames_per_signal, self.frame_size))

def plot(*arg):
	n = len(arg)
	for i in range(n):
		plt.subplot(n,1,i+1)
		plt.plot(arg[i])
	plt.show()

if __name__ == "__main__":
	e = SSNECG()
	e.load('40-20-2.150000.h5')
	s=e.get_signal(128, ugly=True)
	c=e.compress(128, ugly=True)
	d=e.decompress(c)
	plot(s,c,d)
