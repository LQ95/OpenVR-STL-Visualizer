import numpy
from PIL import Image, ImageDraw, ImageFont,ImagePalette
import math
class TextureControl(object):
	def __init__(self,width):
		#inizializzato con la larghezza, il resto è tutto parametrizzato di conseguenza
		self.width=width
		self.height=math.ceil(self.width/1.5)
		self.fontsize = math.ceil(self.height/15)
		self.tex= Image.new('RGBA',(self.width,self.height), color= 'black')
		#self.palette=[0,0,0,255,0,0,255,255,255]
		self.fnt=ImageFont.truetype('arial.ttf', self.fontsize)
		self.draw= ImageDraw.Draw(self.tex)
		black_RGB=(0,0,0)
		white_RGB=(255,255,255)
		green_RGB=(0,255,0)
		black_grayscale=0
		white_grayscale=255
		grey_grayscale=128
		self.black=black_RGB
		self.white=white_RGB
		self.green=green_RGB
		self.default_fill_color = self.white
		self.evidenced_fill_color = self.green
		self.first_column_x = math.ceil(self.width/36)
		self.second_column_x = math.ceil(self.width/1.7)

		
		self.parameterCoordinates={
		'param1':(self.first_column_x,math.ceil(self.height/5.8)),
		'param2':(self.first_column_x,math.ceil(self.height/2.3)),
		'param3':(self.first_column_x,math.ceil(self.height/1.45)),
		'param4':(self.second_column_x,math.ceil(self.height/5.8)),
		'param5':(self.second_column_x,math.ceil(self.height/2.3)),
		'param6':(self.second_column_x,math.ceil(self.height/1.16))
		}

		self.parameterTextDescriptions={
		'param1':"desc1",
		'param2':"desc2",
		'param3':"desc3",
		'param4':"desc4",
		'param5':"desc5",
		'param6':"desc6"
		}

		self.parameterValueTextDistance = math.ceil(self.fontsize*1.5)
		self.prevParameter='param1'

	def generateTexture(self,menu_dict,selected_param):
		#self.tex.putpalette(self.palette)
		#genera l'immagine 
		tex=self.tex

		#Setup per scriverci sopra
		d = self.draw
		fnt = self.fnt
		
		#carica un logo per il menu
		logo_path = "your_logo_here.png"
		logo = Image.open(logo_path )
		logo = logo.resize( (math.ceil(self.width/3.7),math.ceil(self.height/4.6)) )
		logo_attachment_point_coords = (-math.ceil(self.width/78), -math.ceil(self.height/80))
		tex.paste(logo, logo_attachment_point_coords)
		
		default_fill_color = self.default_fill_color
		evidenced_fill_color = self.evidenced_fill_color
		text_fill_color = default_fill_color
		parameterCoordinates=self.parameterCoordinates
		param_value= ""
		
		#scrivi
		#evidenzia il testo del parametro selezionato
		title_coords=(math.ceil(self.width/2.75),math.ceil(self.height/70))
		d.text(title_coords, "Parameter Menu",font=fnt, fill=text_fill_color)

		if(selected_param == 'param1'):
			text_fill_color = evidenced_fill_color
		print("evidenzia? text fill color:")
		print(text_fill_color)

		param_coordinates= parameterCoordinates['param1']
		d.text(param_coordinates, "desc1",font=fnt, fill=text_fill_color)
		param_value = str(menu_dict["param1"])

		param_value_coords= (param_coordinates[0],param_coordinates[1] + self.parameterValueTextDistance)
		d.text(param_value_coords, param_value,font=fnt, fill=text_fill_color)

		text_fill_color = default_fill_color


		param_coordinates= parameterCoordinates['param2']

		d.text(param_coordinates, "desc2",font=fnt, fill=text_fill_color)
		param_value=str(menu_dict["param2"])

		param_value_coords= (param_coordinates[0],param_coordinates[1] + self.parameterValueTextDistance)
		d.text(param_value_coords, param_value,font=fnt, fill=text_fill_color)
		


		param_coordinates= parameterCoordinates['param3']

		d.text(param_coordinates, "desc3",font=fnt, fill=text_fill_color)
		param_value=str(menu_dict["param3"])

		param_value_coords= (param_coordinates[0],param_coordinates[1] + self.parameterValueTextDistance)
		d.text(param_value_coords, param_value,font=fnt, fill=text_fill_color)


		param_coordinates= parameterCoordinates['param4']

		d.text(param_coordinates, "desc4",font=fnt, fill=text_fill_color)
		
		param_value=str(menu_dict["param4"])
		param_value_coords= (param_coordinates[0],param_coordinates[1] + self.parameterValueTextDistance)
		d.text(param_value_coords, param_value,font=fnt, fill=text_fill_color)

		param_coordinates= parameterCoordinates['param5']

		d.text(param_coordinates, "desc5",font=fnt, fill=text_fill_color)
		param_value=str(menu_dict["param5"])
		
		param_value_coords= (param_coordinates[0],param_coordinates[1] + self.parameterValueTextDistance)
		d.text(param_value_coords, param_value,font=fnt, fill=text_fill_color)

		param_coordinates= parameterCoordinates['param6']

		d.text(param_coordinates, "desc6",font=fnt, fill=text_fill_color)

		tex.save('pil_test.png')

		


		#converti
		tex_array= numpy.array(list(tex.getdata()))  
		
		return tex_array

	def modifyTexture(self,menu_dict,selected_param):

		tex=self.tex
		#Setup per scriverci sopra
		d = self.draw
		fnt = self.fnt
		default_fill_color = self.default_fill_color
		evidenced_fill_color = self.evidenced_fill_color
		text_fill_color = evidenced_fill_color
		parameterValueTextDistance = self.parameterValueTextDistance

		#ritrova le coordinate del parametro nuovo e del parametro precedentemente evidenziato o modificato
		param_coordinates=self.parameterCoordinates[selected_param]
		text_desc=self.parameterTextDescriptions[selected_param]

		if(selected_param !=self.prevParameter):
			text_fill_color = default_fill_color
			prev_param_coordinates=self.parameterCoordinates[self.prevParameter]
			prev_text_desc=self.parameterTextDescriptions[self.prevParameter]
			d.text(prev_param_coordinates, prev_text_desc,font=fnt, fill=text_fill_color)
			
			prev_parameter_value_text_coords = (prev_param_coordinates[0],prev_param_coordinates[1] + parameterValueTextDistance)
			prev_param_value=str(menu_dict[self.prevParameter])
			d.text(prev_parameter_value_text_coords, prev_param_value,font=fnt, fill=text_fill_color)
			
			text_fill_color=evidenced_fill_color
			d.text(param_coordinates, text_desc,font=fnt, fill=text_fill_color)

		
		
		parameter_value_text_coords = (param_coordinates[0],param_coordinates[1] + parameterValueTextDistance)
		
		#cancella solo l'area dove bisogna riscrivere il valore
		tex.paste( self.black, (parameter_value_text_coords[0], parameter_value_text_coords[1], parameter_value_text_coords[0]+math.ceil(self.width/11), parameter_value_text_coords[1]+self.fontsize))

		param_value=str(menu_dict[selected_param])
		d.text(parameter_value_text_coords, param_value,font=fnt, fill=text_fill_color)


		self.prevParameter=selected_param

		tex_array= numpy.array(list(tex.getdata()))  

		return tex_array


	def generateEmptyBackground(self, color):
		img= list()

		for i in range(30):
			for j in range(20):
				img.append([color[0],color[1],color[2],1.0])

		return numpy.array(img)

	def generateSampleImage(self):
		img= list()

		for i in range(30):
			for j in range(20):
				img.append([i*j/602,i*j/601,i*j/600,1.0])

		return numpy.array(img)



