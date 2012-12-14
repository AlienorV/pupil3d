"""
Point class __init__.py is used as a manager class for Points (plural) 
This class makes attributes of points accessible to other programs
And can be used for global point manipulation.  

Later on we will need to handle attributes of points in relation to each camera
The point_cluster.py file and PointCluster class will be used to perform this relation 
in the future. 
"""

import numpy as np
import OpenGL.GL as gl

class Points(object):
	"""Manager Class for Point objects"""
	def __init__(self):
		self.f_pts = None
		self.n_pts = None
		self.colors = None
		self.scale = 1.0 

		self.verts = None
		self.aabb_verts = None
		self.avg = None

	def load_ply(self, ply):
		ply = ply.readlines() #get lines as list
		header = map(lambda s: s.strip(), ply[:13])
		
		ply_lines = np.asarray([i.split() for i in ply[13:]], dtype='f4')
		self.f_pts = ply_lines[:,0:3]
		self.n_pts = ply_lines[:,3:6]
		self.colors = ply_lines[:,6:]	

	def load_sparse_ply(self, ply):
		# this method will not be used in the final version of this program
		# but keeping it here, because we may want to view sparse .ply files
		# for intermediate results... however, this can be done in meshlab
		ply = ply.readlines() #get lines as list
		header = map(lambda s: s.strip(), ply[:12])
		num_vert = int(header[4].split()[2]) #total number of vertices

		ply_lines = np.asarray([i.split() for i in ply[13:]], dtype='f4')
		# projection_info = np.asarray([i.split() for i in ply[-num_cam*2:]], dtype='f4')
		# cameras = projection_info[::2] # even step for focal planes
		# focal_planes = projection_info[1::2] # odd step

		self.f_pts = ply_lines[:,0:3]
		self.colors = ply_lines[:,3:6]	

		# return pts, cameras, focal_planes

	def make_verts(self):
		v = []
		n = (0,1,0)

		for pt, cr in zip(self.f_pts, self.colors):
			v.append((pt, n, cr/255))

		self.verts = np.asarray(v, dtype=[('position','f4',3), ('normal','f4',3), ('color','f4',3)] )

	def make_AABB(self):
		x_min = np.min(self.f_pts[:,0])
		y_min = np.min(self.f_pts[:,1])
		z_min = np.min(self.f_pts[:,2])

		x_max = np.max(self.f_pts[:,0])
		y_max = np.max(self.f_pts[:,1])
		z_max = np.max(self.f_pts[:,2])

		p = ( 	(x_min, y_min, z_max), (x_min, y_max, z_max), (x_max, y_max, z_max), (x_max, y_min, z_max),
				(x_min, y_min, z_min), (x_min, y_max, z_min), (x_max, y_max, z_min), (x_max, y_min, z_min) )
		n = ( ( 0, 0, 1), (1, 0, 0), ( 0, 1, 0), (-1, 0, 0), (0,-1, 0), ( 0, 0,-1) );
		c = ( (1.0, 0.0, 0., 1.0) )
		self.aabb_verts = np.array([(p[0], n[0], c[0]), (p[1], n[0], c[0]), (p[2], n[0], c[0]), (p[3], n[0], c[0]), #front face
							(p[4], n[5], c[0]), (p[5], n[5], c[0]), (p[6], n[5], c[0]), (p[7], n[5], c[0]), #back face
							(p[0], n[3], c[0]), (p[1], n[3], c[0]), (p[5], n[3], c[0]), (p[4], n[3], c[0]), #left face
							(p[1], n[2], c[0]), (p[5], n[2], c[0]), (p[6], n[2], c[0]), (p[2], n[2], c[0]), #top face
							(p[3], n[1], c[0]), (p[2], n[1], c[0]), (p[6], n[1], c[0]), (p[7], n[1], c[0]), #right face
							(p[0], n[4], c[0]), (p[4], n[4], c[0]), (p[7], n[4], c[0]), (p[3], n[4], c[0]), #bottom face
							],
						dtype = [('position','f4',3), ('normal','f4',3), ('color','f4',3)] )

		#volume_centroid = np.abs(x_max - x_min)*np.abs(y_max - y_min)*np.abs(z_max-z_min)
		self.avg = -np.array([np.mean(self.f_pts[:,0]), np.mean(self.f_pts[:,1]), np.mean(self.f_pts[:,2]) ])


	def _get_scale(self):
		return self.scale
	def _set_scale(self, value):
		self.scale = float(value)

	def _make_smooth(self):
		gl.glEnable(gl.GL_POINT_SMOOTH)
	def _make_square(self):
		gl.glDisable(gl.GL_POINT_SMOOTH)

	def _render(self, var):
		if var:
			gl.glEnable(gl.GL_POINT_SMOOTH)
		else:
			gl.glDisable(gl.GL_POINT_SMOOTH)

