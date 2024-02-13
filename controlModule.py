import openvr
import math
import numpy
from MenuStatus import MenuStatus
class controlInputModule:
	def __init__(self, pose_array):
		self.rotationAmount = 0
		self.translationDelta = [0,0,0]
		self.rotationAxis = [0,0,1]
		self.left_controller_id= None 
		self.right_controller_id= None
		
		self.last_left_angle= 0
		self.last_right_angle= 0

		self.left_isdragging = False
		self.right_isdragging = False
		self.last_left_pos = None
		self.last_right_pos = None
		
		self.pose_array=pose_array  
		
		self.lockedRotation= 0

		self.rotationMatrix=numpy.array([[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]], dtype = numpy.float32)
		
		self.controllerRotationMatrix=numpy.array([[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]], dtype = numpy.float32)
		self.controllerRotationMatrix_static=numpy.array([[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]], dtype = numpy.float32)
		self.controllerRotationMatrix_reset=numpy.array([[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]], dtype = numpy.float32)
		
		self.trackpadRotationMatrix=numpy.array([[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]], dtype = numpy.float32)

		self.paused= False
		self.left_pause_pressed= False
		self.right_pause_pressed= False

		#variabili di stato menu
		self.menuStatus = MenuStatus()
		self.left_pause_pressed = False
		self.right_pause_pressed = False
		self.left_trackpad_pressed = False
		self.right_trackpad_pressed = False

	def getDelta(self,pos1,pos2):
		return [pos1[0] - pos2[0], pos1[1] - pos2[1], pos1[2] - pos2[2]]


	def getFinalDelta(self,pos1,pos2):


		return [pos1[0] + pos2[0], pos1[1] + pos2[1], pos1[2] + pos2[2]] 


	def get_controller_ids(self):

		left = None
		right = None
		for i in range(openvr.k_unMaxTrackedDeviceCount):
			device_class = openvr.VRSystem().getTrackedDeviceClass(i)
			if device_class == openvr.TrackedDeviceClass_Controller:
				role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(i)
				if role == openvr.TrackedControllerRole_RightHand:
					right = i
				if role == openvr.TrackedControllerRole_LeftHand:
					left = i
		return left, right

	def get_controller_pos(self,controller_id):
		controller_pose = self.pose_array[controller_id]
		controller_matrix=controller_pose.mDeviceToAbsoluteTracking
		return [controller_matrix[0][3],controller_matrix[1][3],controller_matrix[2][3]]

	def get_controller_rotation(self,controller_id):
		controller_pose = self.pose_array[controller_id]
		controller_matrix=controller_pose.mDeviceToAbsoluteTracking
		return numpy.array([[controller_matrix[0][0],controller_matrix[0][1],controller_matrix[0][2],0],
		[controller_matrix[1][0],controller_matrix[1][1],controller_matrix[1][2],0],
		[controller_matrix[2][0],controller_matrix[2][1],controller_matrix[2][2],0],
		[0,0,0,1.0]], dtype = numpy.float32)


	def get_rotation_matrix(self,axis, angle):         
		axis = axis/numpy.linalg.norm(axis)
		s = math.sin(angle)
		c = math.cos(angle)
		oc = 1.0 - c
		matrix =numpy.array([[oc * axis[0] * axis[0] + c,           oc * axis[0] * axis[1] - axis[2] * s,  oc * axis[2] * axis[0] + axis[1] * s,  0.0],
				[oc * axis[0] * axis[1] + axis[2] * s,  oc * axis[1] * axis[1] + c,           oc * axis[1] * axis[2] - axis[0] * s,  0.0],
				[oc * axis[2] * axis[0] - axis[1] * s,  oc * axis[1] * axis[2] + axis[0] * s,  oc * axis[2] * axis[2] + c,           0.0],
				[0.0,                                0.0,                                0.0,                                1.0]], dtype = numpy.float32)

		return matrix
                

	
	def from_controller_state_to_dict(self,pControllerState):
		# docs: https://github.com/ValveSoftware/openvr/wiki/IVRSystem::GetControllerState
		d = {}
		d['unPacketNum'] = pControllerState.unPacketNum
        
		# on trigger .y is always 0.0 says the docs
		d['trigger'] = pControllerState.rAxis[1].x
        
		# 0.0 on trigger is fully released
		# -1.0 to 1.0 on joystick and trackpads
		d['trackpad_x'] = pControllerState.rAxis[0].x
		d['trackpad_y'] = pControllerState.rAxis[0].y
        
        # These are published and always 0.0
        # for i in range(2, 5):
        #     d['unknowns_' + str(i) + '_x'] = pControllerState.rAxis[i].x
        #     d['unknowns_' + str(i) + '_y'] = pControllerState.rAxis[i].y
		d['ulButtonPressed'] = pControllerState.ulButtonPressed
		d['ulButtonTouched'] = pControllerState.ulButtonTouched
        
        # To make easier to understand what is going on
        # Second bit marks menu button
		d['menu_button'] = bool(pControllerState.ulButtonPressed >> 1 & 1)
        
        # 32 bit marks trackpad
		d['trackpad_pressed'] = bool(pControllerState.ulButtonPressed >> 32 & 1)
		d['trackpad_touched'] = bool(pControllerState.ulButtonTouched >> 32 & 1)
        
        # third bit marks grip button
		d['grip_button'] = bool(pControllerState.ulButtonPressed >> 2 & 1)
        
        # System button can't be read, if you press it
        # the controllers stop reporting
		return d

	def control(self):
		localRotationAmount = 0
		localTranslationDelta = [0,0,0]
		leftTranslationDelta = [0,0,0]
		rightTranslationDelta = [0,0,0]
		localRotationAxis = [0,1,0]
		modified = 0
		trackpadRotationMatrix=numpy.array([[1,0,0,0],
		[0,1,0,0],
		[0,0,1,0],
		[0,0,0,1]], dtype = numpy.float32)
		
 
         #controlli
		if self.left_controller_id is None or self.right_controller_id is None:
			self.left_controller_id, self.right_controller_id = self.get_controller_ids()
            
		if self.left_controller_id or self.right_controller_id:
			#controller sinistro
			if self.left_controller_id != None:
				currentpose= self.pose_array[self.left_controller_id]
				result, pControllerState = openvr.VRSystem().getControllerState(self.left_controller_id)
				controller_dict = self.from_controller_state_to_dict(pControllerState)
				#print(controller_dict)
				#pausa, quando viene messo in pausa l'osso è spostato in avanti e poi torna indietro
				if (controller_dict['menu_button'] == True and self.left_pause_pressed == False):
					self.paused = not self.paused
					self.left_pause_pressed = True
					if(self.paused):
						leftTranslationDelta[2]= leftTranslationDelta[2] -3
					else:
						leftTranslationDelta[2]= leftTranslationDelta[2] +3
				elif(controller_dict['menu_button'] == False):
					self.left_pause_pressed = False

				#print("pausa:")
				#print(self.paused)

				
				#manda in avanti o indietro col trackpad
				if (controller_dict['trackpad_pressed'] == True and self.paused == False):
					leftTranslationDelta[0]= controller_dict['trackpad_x']/45
					leftTranslationDelta[2]= -controller_dict['trackpad_y']/45
				#gira
				elif (controller_dict['trackpad_touched'] == True and self.paused == False):
					
					if (self.last_left_angle== 0):
						self.last_left_angle=math.asin(controller_dict['trackpad_y'])
						modified = 1
					
					else:
						#print("trackpad sinistro toccato")
						
						localRotationAmount = math.asin(controller_dict['trackpad_y']) - self.last_left_angle
						localRotationAxis = [0,1,0]
						numpy.matmul(self.trackpadRotationMatrix,self.get_rotation_matrix(localRotationAxis, localRotationAmount), out = self.trackpadRotationMatrix)
						self.last_left_angle=math.asin(controller_dict['trackpad_y'])
						modified = 1
				#drag
				if(controller_dict['trigger'] == 1.0 and self.lockedRotation !=2 and self.paused == False):
					print("trigger sinistro toccato. posizione controller sinistro: ")
					print(self.get_controller_pos(self.left_controller_id))
					if (self.left_isdragging == False):
						self.left_isdragging = True
						self.last_left_pos = self.get_controller_pos(self.left_controller_id)
						self.controllerRotationMatrix_reset=numpy.linalg.inv(self.get_controller_rotation(self.left_controller_id))
						self.lockedRotation = 1
					
					elif(currentpose.bPoseIsValid):
						#print("posa valida.")
						leftTranslationDelta = self.getDelta(self.get_controller_pos(self.left_controller_id), self.last_left_pos)
						
						self.controllerRotationMatrix=self.get_controller_rotation(self.left_controller_id)
						numpy.matmul(self.controllerRotationMatrix,self.controllerRotationMatrix_reset,out=self.controllerRotationMatrix)
						numpy.matmul(self.controllerRotationMatrix_static,self.controllerRotationMatrix,out=self.controllerRotationMatrix)
						
						#print("delta locale del sinistro:")
						#print(leftTranslationDelta)
						self.last_left_pos = self.get_controller_pos(self.left_controller_id)
						self.lockedRotation = 1
					else:
						self.left_isdragging = False
						leftTranslationDelta =[0,0,0]
				else:
					self.left_isdragging = False
					#leftTranslationDelta =[0,0,0]
					if(self.lockedRotation !=2):
						self.controllerRotationMatrix_static=self.controllerRotationMatrix
					self.lockedRotation = 0

			#controller destro
			if self.right_controller_id != None:
				currentpose= self.pose_array[self.right_controller_id]
				result, pControllerState = openvr.VRSystem().getControllerState(self.right_controller_id)
				controller_dict = self.from_controller_state_to_dict(pControllerState)
				#print(controller_dict)
				#pausa
				if (controller_dict['menu_button'] == True and self.right_pause_pressed == False):
					self.paused = not self.paused
					self.right_pause_pressed = True
					if(self.paused):
						rightTranslationDelta[2]= rightTranslationDelta[2] -3
					else:
						rightTranslationDelta[2]= rightTranslationDelta[2] +3
				elif(controller_dict['menu_button'] == False):
					self.right_pause_pressed = False
				#print("pausa:")
				#print(self.paused)
				#manda in avanti o indietro col trackpad
				if (controller_dict['trackpad_pressed'] == True and self.paused == False):
					rightTranslationDelta[0]= controller_dict['trackpad_x']/45
					rightTranslationDelta[2]= -controller_dict['trackpad_y']/45
				#gira
				elif (controller_dict['trackpad_touched'] == True and self.paused == False):
					
					if (self.last_right_angle== 0):
						self.last_right_angle= math.asin(controller_dict['trackpad_y'])
						modified = 1
					
					else:
						#print("trackpad destro toccato. rotationAmount:")
						localRotationAmount = math.asin(controller_dict['trackpad_y']) - self.last_right_angle
						#print(localRotationAmount)
						localRotationAxis = [0,0,1]
						numpy.matmul(self.trackpadRotationMatrix,self.get_rotation_matrix(localRotationAxis, localRotationAmount), out = self.trackpadRotationMatrix)
						self.last_right_angle= math.asin(controller_dict['trackpad_y'])
						modified = 1
				#drag
				if(controller_dict['trigger'] == 1.0 and self.lockedRotation != 1 and self.paused == False):
					#print("trigger destro toccato.")
					#print(self.get_controller_pos(self.right_controller_id))
					if (self.right_isdragging == False):
						self.right_isdragging = True
						self.last_right_pos = self.get_controller_pos(self.right_controller_id)
						self.controllerRotationMatrix_reset=numpy.linalg.inv(self.get_controller_rotation(self.right_controller_id))
						self.lockedRotation = 2

					elif(currentpose.bPoseIsValid):
						#print("posa valida.")
						rightTranslationDelta = self.getDelta(self.get_controller_pos(self.right_controller_id),self.last_right_pos)
						self.last_right_pos=self.get_controller_pos(self.right_controller_id)
						
						self.controllerRotationMatrix = self.get_controller_rotation(self.right_controller_id)
						numpy.matmul(self.controllerRotationMatrix,self.controllerRotationMatrix_reset,out=self.controllerRotationMatrix)
						numpy.matmul(self.controllerRotationMatrix_static,self.controllerRotationMatrix,out=self.controllerRotationMatrix)
						self.lockedRotation = 2
					
					else:
						self.right_isdragging = False
						rightTranslationDelta =[0,0,0]				
				else:
					self.right_isdragging = False
					#rightTranslationDelta =[0,0,0]
					if (self.lockedRotation !=1):
						self.controllerRotationMatrix_static=self.controllerRotationMatrix
					self.lockedRotation = 0

		if (modified == 0):
			self.last_left_angle = 0
			self.last_right_angle = 0

		localTranslationDelta =self.getFinalDelta(leftTranslationDelta,rightTranslationDelta)
		print("delta locale:")
		print(localTranslationDelta)
		numpy.matmul(self.controllerRotationMatrix,self.trackpadRotationMatrix,out=self.rotationMatrix)
		
		#numpy.matmul(self.rotationMatrix,localRotationMatrix,out=self.rotationMatrix)
		#self.rotationMatrix = localRotationMatrix
		
		
		self.translationDelta = self.getFinalDelta(self.translationDelta,localTranslationDelta)
		#print("delta finale:")
		#print(self.translationDelta)           

            
    

		return self.translationDelta,self.rotationMatrix

		#funzioni menu
	def menuControl(self):
		status=self.menuStatus.menu_dict
		print("entro nel controllo del menù")
		#print("stato:")
		#print(status)
		status['modified'] = False


		if self.left_controller_id is None or self.right_controller_id is None:
			self.left_controller_id, self.right_controller_id = self.get_controller_ids()
		#print("ho eseguito controllo sui controller")
		if self.left_controller_id or self.right_controller_id:
			#print("almeno un controller è presente")
			#controller sinistro
			if self.left_controller_id != None:
				#print("controller sinistro:")
				currentpose= self.pose_array[self.left_controller_id]
				result, pControllerState = openvr.VRSystem().getControllerState(self.left_controller_id)
				controller_dict = self.from_controller_state_to_dict(pControllerState)
				#print(controller_dict)
				if (controller_dict['menu_button'] == True and self.left_menu_enabled == False):
					status['enabled'] = not status['enabled']
					print("ho premuto pausa")
					self.left_menu_enabled = True
				elif(controller_dict['menu_button'] == False):
					self.left_menu_enabled = False
				#print("pausa:")
				#print(self.paused)
				#print("menù abilitato:")
				#print(status['enabled'])
				if (controller_dict['trackpad_pressed'] == True and self.paused == True and self.left_trackpad_pressed == False):
					self.left_trackpad_pressed= True
					status['modified'] = True
					trackpad_y= controller_dict['trackpad_y'] 
					trackpad_x= controller_dict['trackpad_x']
					print("ho premuto e risulta modificato")
					if (trackpad_y > -0.3 and trackpad_y < 0.5 and trackpad_x> 0.5 ):
						self.menuStatus.augmentSelectedParam()
					if (trackpad_y > -0.3 and trackpad_y < 0.5 and trackpad_x< -0.5 ):
						self.menuStatus.diminishSelectedParam()
					if (trackpad_y < -0.6 ):
						self.menuStatus.selectNextParam()
					if (trackpad_y > 0.6 ):
						self.menuStatus.selectPrevParam()
				elif(controller_dict['trackpad_pressed'] == False):
					self.left_trackpad_pressed= False



			#controller destro
			if self.right_controller_id != None:
				#print("controller destro:")
				currentpose= self.pose_array[self.right_controller_id]
				result, pControllerState = openvr.VRSystem().getControllerState(self.right_controller_id)
				controller_dict = self.from_controller_state_to_dict(pControllerState)
				#print(controller_dict)
				if (controller_dict['menu_button'] == True and self.right_menu_enabled == False):
					status['enabled'] = not status['enabled']
					self.right_menu_enabled = True
				elif(controller_dict['menu_button'] == False):
					self.right_menu_enabled = False
				#print("pausa:")
				#print(self.paused)
				#print("menù abilitato:")
				#print(status['enabled'])
				#per modifiare premi a destra e sinistra, decidi griglia di input validi
				if (controller_dict['trackpad_pressed'] == True and self.paused == True and self.right_trackpad_pressed == False):
					self.right_trackpad_pressed= True
					trackpad_y= controller_dict['trackpad_y'] 
					trackpad_x= controller_dict['trackpad_x']
					status['modified'] = True
					print("ho premuto e risulta modificato")
					if (trackpad_y > -0.3 and trackpad_y < 0.5 and trackpad_x> 0.5 ):
						self.menuStatus.augmentSelectedParam()
					if (trackpad_y > -0.3 and trackpad_y < 0.5 and trackpad_x< -0.5 ):
						self.menuStatus.diminishSelectedParam()
					if (trackpad_y < -0.6 ):
						self.menuStatus.selectNextParam()
					if (trackpad_y> 0.6 ):
						self.menuStatus.selectPrevParam()
				elif(controller_dict['trackpad_pressed'] == False):
					self.right_trackpad_pressed= False




		self.menuStatus.menu_dict = status
		return status,self.menuStatus.getSelectedParam()

