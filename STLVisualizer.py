
from STLModel import STLModel
from MenuScreen import MenuScreen 
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.color_cube_actor import ColorCubeActor
from openvr.tracked_devices_actor import TrackedDevicesActor
from openvr.glframework.sdl_app import SdlApp
from controlModule import controlInputModule



"""
Minimal sdl programming example which colored OpenGL cube scene that can be closed by pressing ESCAPE.
"""


if __name__ == "__main__":
	renderer = OpenVrGlRenderer(multisample=2)
	controlMod= None
	controlMod=controlInputModule(renderer.poses)
	renderer.append(ThreeDKnee(renderer.poses,controlMod))
	renderer.append(MenuScreen(controlMod))
	renderer.append(TrackedDevicesActor(renderer.poses))
	with SdlApp(renderer, "Visualizing a 3D model in VR") as app:
		app.run_loop()