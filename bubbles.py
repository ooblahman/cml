''' Rayleigh-Benard convection ''' 

import seaborn as sns
import matplotlib.pyplot as plt
import pdb
import numpy as np
from typing import Tuple
import colorcet as cc
from tqdm import tqdm

from cml import *

np.random.seed(9999)

class CML_bubbles:
	def __init__(self, shape: Tuple, temp: float, eps: float, sigma: float, alpha: float, eta: float, T_c: float):
		'''
		shape: (m, n) grid
		temp: temperature difference between upper and lower plates
		nu: viscosity
		kappa: thermal diffusion coefficient
		eta: pressure effect
		kappa: thermal expansion coefficient
		dt (optional): rate of particle advection 
		'''
		self.shape = shape
		self.temp = temp
		self.eps = eps
		self.sigma = sigma
		self.alpha = alpha
		self.eta = eta
		self.T_c = T_c
		self.reset()

	def laplace_x(self, u):
		ret = -u
		ret += np.c_[u[:,1:],u[:,0]] / 2
		ret += np.c_[u[:,-1],u[:,:-1]] / 2
		return ret

	def laplace_y(self, u):
		ret = -u
		ret[0] = 0
		ret[-1] = 0
		ret[1:-1] += (u[:-2] + u[2:]) / 2
		return ret

	def laplace(self, u):
		return (self.laplace_x(u) + self.laplace_y(u)) / 2

	def density(self, T):
		return np.tanh(self.alpha*(T-self.T_c))

	def step(self):
		# Thermal diffusion
		T = self.T + self.eps*self.laplace(self.T)

		# Bubble nucleation
		T[1:-1] -= (self.sigma/2)*T[1:-1]*(self.density(T[:-2]) - self.density(T[2:]))

		# Evaporative cooling / condensative heating
		m, n = self.shape
		for y in range (1, m-1):
			for x in range(n):
				mult = 0.
				if T[y, x] > self.T_c and self.T[y, x] < self.T_c:
					mult = -1.
				elif T[y, x] < self.T_c and self.T[y, x] > self.T_c:
					mult = 1.
				T[y, (x+1)%m] += mult*self.eta
				T[y, (x-1)%m] += mult*self.eta
				T[y-1, x] += mult*self.eta
				T[y+1, x] += mult*self.eta

		# Reapply boundary conditions
		T[0,:] = 0.
		T[-1,:] = self.temp

		self.T = T

	def reset(self):
		# Symmetry-breaking initial conditions
		self.T = (self.temp / 2) + np.random.normal(size=self.shape, scale=1e-3)
		self.T[0,:] = 0.
		self.T[-1,:] = self.temp

if __name__ == '__main__':
	m, n = 48, 48
	temp = 9.95
	eps = 0.5
	sigma = 0.1
	alpha = 10
	eta = 0.1
	T_c = 10

	# pdb.set_trace()

	''' Save as plot ''' 
	# model = CML_bubbles((m, n), temp, eps, sigma, alpha, eta, T_c)

	# fig, axs = plt.subplots(1, 3, figsize=(12, 6))

	# for _ in range(500):
	# 	model.step()

	# axs[0].contourf(model.T, 20, cmap='inferno')
	# axs[0].invert_yaxis()
	# axs[0].axis('off')

	# for _ in range(500):
	# 	model.step()

	# axs[1].contourf(model.T, 20, cmap='inferno')
	# axs[1].invert_yaxis()
	# axs[1].axis('off')

	# for _ in range(500):
	# 	model.step()

	# axs[2].contourf(model.T, 20, cmap='inferno')
	# axs[2].invert_yaxis()
	# axs[2].axis('off')

	# fig.tight_layout()
	# fig.savefig('bubbles.png', bbox_inches='tight', pad_inches=0)

	# plt.show()

	''' Characteristic curve ''' 
	t0 = 1000
	tn = 100
	k = 3
	temp_rng = np.linspace(9.7, 10.05, 100)
	data = []
	for temp in tqdm(temp_rng):
		model = CML_bubbles((m, n), temp, eps, sigma, alpha, eta, T_c)
		for _ in range(t0):
			model.step()
		flux = 0.
		for _ in range(tn):
			flux += (model.T[-k] - temp).mean()
			model.step()
		flux /= tn
		data.append(flux)
	data = np.array(data)

	fig, ax = plt.subplots(figsize=(12, 4))
	ax.plot(temp_rng, data)
	ax.set_xlabel('External temperature $E$')

	fig.tight_layout()
	fig.savefig('bubbles_curve.png', bbox_inches='tight', pad_inches=0)

	plt.show()

	''' Lyapunov spectra ''' 
	# t0 = 1000
	# tn = 20
	# temp_rng = np.linspace(9.8, 10.1, 75)
	# n_perturb = 40
	# eps_perturb = 0.5
	# k_exponents = m*n

	# spectra = []
	# for temp in tqdm(temp_rng):
	# 	model = CML_bubbles((m, n), temp, eps, sigma, alpha, eta, T_c)

	# 	for _ in range(t0):
	# 		model.step()

	# 	perturbed = []
	# 	for _ in range(n_perturb):
	# 		model_ = CML_bubbles((m, n), temp, eps, sigma, alpha, eta, T_c)
	# 		model_.T = model.T.copy() 
	# 		model_.T[1:-1] += np.random.normal(size=(m-2, n), scale=eps_perturb)
	# 		perturbed.append(model_)

	# 	spectrum = np.zeros(k_exponents)
	# 	ds = np.vstack([(model_.T - model.T).ravel() for model_ in perturbed])
	# 	for _ in range(tn):
	# 		for model_ in perturbed:
	# 			model_.step()
	# 		model.step()
	# 		ds_ = np.vstack([(model_.T - model.T).ravel() for model_ in perturbed])
	# 		jac = np.linalg.lstsq(ds, ds_)[0]
	# 		Q, R = np.linalg.qr(jac.T, mode='complete')
	# 		spectrum += np.log(np.abs(np.diag(R)[:k_exponents]))
	# 		ds = ds_
	# 	spectra.append(spectrum)
	# spectra = np.array(spectra)

	# fig, ax = plt.subplots(figsize=(12, 5))
	# for i in range(spectra.shape[1]):
	# 	ax.scatter(temp_rng, spectra[:,i], color='blue', s=1)
	# envelope = spectra.max(axis=1)
	# ax.plot(temp_rng, envelope, color='black', alpha=0.5)
	# ax.plot(temp_rng, np.zeros_like(temp_rng), color='black')
	# ax.set_ylim(ymin=-100)
	# ax.set_xlabel('External temperature $E$')

	# fig.tight_layout()
	# fig.savefig('bubbles_lyapunov.png', bbox_inches='tight', pad_inches=0)
	# plt.show()

	''' Save as video ''' 
	# from matplotlib.animation import FFMpegWriter

	# writer = FFMpegWriter(fps=15, metadata={'title': 'rb_convectoin'})
	# fig, axs = plt.subplots(1, 2, figsize=(13, 4))

	# with writer.saving(fig, 'rb_convection.mp4', dpi=100):
	# 	model.reset()
	# 	for _ in tqdm(range(1000)):
	# 		axs[0].clear()
	# 		axs[1].clear()
	# 		axs[0].contourf(model.T, 20, cmap='inferno_r')
	# 		axs[1].quiver(model.Vx, model.Vy)
	# 		writer.grab_frame()
	# 		model.step()