
#classe ausiliaria per gestire lo stato del menù fuori dalla classe di controllo

class MenuStatus(object):
	def __init__(self):
		self.menu_dict = {}

		#parametri di esempio
		self.menu_dict['param1'] = 7
		self.menu_dict['param2'] = 6
		self.menu_dict['param3'] = 8
		self.menu_dict['param4'] = 3
		self.menu_dict['param5'] = 1

		#parametri necessari per il controllo
		self.menu_dict['enabled'] = False
		self.menu_dict['modified'] = False

		#parametri interni
		self.param_array= ('param1','param2','param3','param4','param5','param6')
		self.selected_param = 0


	def getSelectedParam(self):
		return self.param_array[self.selected_param]

	#selezione
	def selectNextParam(self):
		curr_param=self.selected_param+1
		array_length=len(self.param_array)
		if(curr_param < array_length):
			self.selected_param += 1
		elif(curr_param >= array_length ):
			self.selected_param = 0


	def selectPrevParam(self):
		curr_param=self.selected_param-1
		array_length=len(self.param_array)
		if(curr_param >= 0):
			self.selected_param -= 1
		elif(curr_param < 0 ):
			self.selected_param = array_length -1

	#modifica
	def augmentSelectedParam(self):
		param=self.getSelectedParam()
		quantity=1
		if (param == "param1"):
			quantity = 50
		if (param == "param6"):
			return
		self.menu_dict[param] += quantity

	def diminishSelectedParam(self):
		param=self.getSelectedParam()
		quantity=1
		if (param == "param1"):
			quantity = 50
		if (param == "param6"):
			return
		if(self.menu_dict[param] > 0):
			self.menu_dict[param] -= quantity




