"""
__init__.py file for the graphics class.  
The graphics class is used for rendering points, cameras, and images 
in a 3D scene.  

This class will contain the main loop of the graphics (glumpy) class. 
Other functions/classes used for graphics will be located within this directory. 
"""
import sys
import numpy as np

import glumpy
import glumpy.atb as atb
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from ctypes import *

import trackball, eye

class Visualize(object):
	"""Graphics Class Manager"""
	def __init__(self, title="SfM Browser"):
		self.title = title
		self.point_manager = None
		self.camera_manager = None
		self.verts = None
		self.bar = None
		self.space_key = False

		self.fig_size = (1280,960)
		self.fig_pos = (0,10)
		self.fig = glumpy.figure(self.fig_size, self.fig_pos)
		self.trackball = trackball.Trackball(0.0,0.0,1.0,10.0)
		self.eye = eye.Eye(center=[0.0, 0.0, -10.0], focus=[0.0,0.0,0.0], up=[0.0,1.0,0.0])
		
		self.tb_show = c_bool(1)
		self.eye_show = c_bool(0)
		self.points_show = c_bool(1)

		self.full = c_bool(0)
		self.color = (c_float * 4)(0.,0.,0.,1.0)
	

	def quit(self, *args, **kwargs):
		sys.exit()

	def main(self):
		self.setup_atb()

		self.fig.window.push_handlers(	self.on_init,
							 			self.on_mouse_drag,
							 			self.on_mouse_scroll,
							 			self.on_key_press,
							 			self.on_key_release)
		self.fig.window.push_handlers(atb.glumpy.Handlers(self.fig.window))
		self.fig.window.push_handlers(self.on_draw)
		self.fig.window.set_title(self.title)
		glumpy.show()


	def draw_scene(self):
		gl.glEnable( gl.GL_BLEND ) 
		# gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_SRC_ALPHA) 
		gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

		gl.glPushMatrix()
		gl.glTranslatef(*self.point_manager.avg)
		gl.glPointSize(self.point_manager._get_scale())
		
		if self.points_show:
			self.verts.draw( gl.GL_POINTS, 'pnc' )
		
		for c in self.camera_manager.get_cams():
			gl.glPushMatrix()
			gl.glMultMatrixf(c.R_gl)
			gl.glTranslatef(*c.t)

			if c.cone_show:
				gl.glPushMatrix()
				# cone is constructed on z axis toward image center
				# rotate so that it goes through pupil position point
				gl.glMultMatrixf(c.R_cone_gl)
				gl.glPointSize(4.0)
				c.inside_cone_vbo.draw(gl.GL_POINTS, 'pnc')
				
				gl.glTranslatef(0,0,-c.cone_len)
				gl.glColor4f(1.0,1.0,1.0,0.25)
				glut.glutSolidCone(c.cone_r, c.cone_len , 32 , 1 )
				gl.glPopMatrix()

			if c.pyramid_show:
				gl.glEnable(gl.GL_TEXTURE_2D) 
				gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_SRC_ALPHA) 
				c.img.draw(-c.img_W, -c.img_H, -c.img_Z, c.img_W*2, c.img_H*2)
				gl.glDisable(gl.GL_TEXTURE_2D) 
				gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

			gl.glPopMatrix()
			
			if c.pyramid_show:
				gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_LINE ) #wireframe display mode		
				c.pyramid.draw(gl.GL_QUADS, 'pnc')
				if c.eye_point is not None:
					# gl.glEnable(gl.GL_POINT_SMOOTH)
					gl.glPointSize(10.0)
					c.eye_point.draw(gl.GL_POINTS, 'pnc')

			gl.glPolygonMode( gl.GL_FRONT_AND_BACK, gl.GL_FILL )
			gl.glDepthMask (gl.GL_TRUE)
		


		gl.glPopMatrix()

	def on_init(self):
		gl.glEnable (gl.GL_LIGHT0)
		gl.glLightfv (gl.GL_LIGHT0, gl.GL_DIFFUSE,  (1.0, 1.0, 1.0, 1.0))
		gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT,  (0.1, 0.1, 0.1, 1.0))
		gl.glLightfv (gl.GL_LIGHT0, gl.GL_AMBIENT,  (0.1, 0.1, 0.1, 1.0))
		gl.glLightfv (gl.GL_LIGHT0, gl.GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
		gl.glLightfv (gl.GL_LIGHT0, gl.GL_POSITION, (0.0, 1.0, 2.0, 1.0))
		gl.glEnable (gl.GL_BLEND)
		gl.glEnable (gl.GL_COLOR_MATERIAL)
		#gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
		#gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

	def on_draw(self):
		self.fig.clear(self.color[0], self.color[1], self.color[2], self.color[3])
		if self.full.value:
			self.fig.window.set_fullscreen(1)
		else:
			self.fig.window.set_fullscreen(0)

		if self.eye_show.value:
			self.eye._show()
			self.eye.push()
			self.draw_scene()
			self.eye.pop()

		if self.tb_show.value:
			self.trackball.push()
			self.draw_scene()
			self.trackball.pop()


	def on_mouse_drag(self, x, y, dx, dy, button):
		if self.space_key:
			if button == 2:
				self.trackball.pan_to(x, y, dx, dy)
				self.fig.redraw()
			if button == 8: # right button to pan
				self.trackball.zoom_to(x, y, dx, dy)
				self.fig.redraw()
		else:
			if button == 2:
				self.trackball.drag_to(x,y,dx,dy)
				self.bar.update()
				self.fig.redraw()
			if button == 8: # right button to pan
				self.trackball.zoom_to(x, y, dx, dy)
				self.fig.redraw()

	def on_mouse_scroll(self, x, y, dx, dy):
		# not working?
		print "scroll event"
		self.trackball.zoom_to(x,y,3*dx,3*dy)
		self.bar.update()
		self.fig.redraw()

	def on_key_press(self, symbol, modifiers):
		if symbol == glumpy.window.key.ESCAPE:
			sys.exit()
		if symbol ==  65289: # TAB
			self.space_key = True

	def on_key_release(self, symbol, modifiers):
		if symbol ==  65289: # TAB
			self.space_key = False


	def setup_atb(self):
		atb.init()
		self.bar = atb.Bar(name="Controls", label="Controls",
				help="Scene controls", color=(50,50,50), alpha=50,
				text='light', position=(10, 10), size=(200, 440))

		self.bar.add_var("World/Zoom", step=0.01, min=0.01, max=1.0,
					getter=self.trackball._get_zoom, setter=self.trackball._set_zoom)

		self.bar.add_var("World/Distance", step=1, min=1, max=300, 
				getter=self.trackball._get_distance, setter=self.trackball._set_distance)
		self.bar.add_var("World/Show_World", self.tb_show, help="Show/Hide Trackball Camera")
		
		self.bar.add_separator("")
		self.bar.add_var("Eye/Show_Eye", self.eye_show, help="Show/Hide Eye Camera")
		self.bar.add_var("Eye/Camera", step=1, min=0, max=self.camera_manager.get_num_cams()-1, 
				getter=self.eye._get_current, 
				setter=self._set_current_camera,
				key="SPACE")

		self.bar.add_separator("")
		self.bar.add_var("Image/Scale", step=0.00001, min=0.00001, getter=self.camera_manager.get_img_scale, 
					setter=self.camera_manager.set_img_scale )
		self.bar.add_button("Show_Images", self.camera_manager.pyramid_show, key="1", help="Show All Images")
		self.bar.add_button("Hide_Images", self.camera_manager.pyramid_hide, key="2", help="Hide All Images")
		self.bar.add_button("Show_Cones", self.camera_manager.cone_show, key="3", help="Show All Fixation Cones")
		self.bar.add_button("Hide_Cones", self.camera_manager.cone_hide, key="4", help="Hide All Images")

		self.bar.add_separator("")
		self.bar.add_var("Points/Show_Points", self.points_show, key="RETURN", help="Show/Hide Points")
		self.bar.add_var("Points/Size", step=0.5, min=1.0, max=20.0, getter=self.point_manager._get_scale, 
					setter=self.point_manager._set_scale )
		self.bar.add_button("Square Point", self.point_manager._make_square, key="9", help="Render square points")
		self.bar.add_button("Circular Point", self.point_manager._make_smooth, key="0", help="Render smooth points")

		self.bar.add_separator("")
		self.bar.add_var("Background/Color", self.color, open=False)
		self.bar.add_separator("")
		self.bar.add_var("Background/Fullscreen", self.full, help="Fullscreen mode for presentation")
		self.bar.add_button("Quit", self.quit, key="ESCAPE", help="Quit application")

	def _set_current_camera(self, value):
		i = int(value)
		for c, i in zip(self.camera_manager.get_cams(), xrange(0,self.camera_manager.get_num_cams())):
			if i == value: 
				c.cone_show = True
				c.pyramid_show = True
			else:
				c.cone_show = False
				c.pyramid_show = False
		self.eye._set_current(value)



	def _set_Points(self, point_manager):
		self.point_manager = point_manager
	def _set_Cameras(self, camera_manager):
		self.camera_manager = self.camera_manager
	def _set_Points_Cameras(self, point_manager, camera_manager):
		self.point_manager = point_manager
		self.camera_manager = camera_manager
		self.eye._set_cams(camera_manager.cameras)

		self.point_manager.make_AABB()
		self.point_manager.make_verts()	

		self.eye._set_pt_avg(self.point_manager.avg)
		self.verts = glumpy.graphics.VertexBuffer(self.point_manager.verts)			



