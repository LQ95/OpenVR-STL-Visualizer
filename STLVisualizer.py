#from CubeMod import CubeMod
from STLModel import STLModel 
#from SimpleTriangle import SimpleTriangle 
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor
from openvr.glframework.sdl_app import SdlApp



if __name__ == "__main__":
	renderer = OpenVrGlRenderer(multisample=2)
	renderer.append(STLModel(renderer.poses,))
	renderer.append(TrackedDevicesActor(renderer.poses))
	with SdlApp(renderer, "Visualizing a 3D model in VR") as app:
		app.run_loop()