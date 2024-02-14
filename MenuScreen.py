

# file color_cube_actor.py
import numpy
import ctypes
import time
import math
import multiprocessing
import queue
from textwrap import dedent

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram

from openvr.glframework import shader_string
from controlModule import controlInputModule
from TextureControl import TextureControl
#variabili globali
controlMod= None
menu_width=900
texControl= TextureControl(menu_width)
texture_proc_done = multiprocessing.Value(ctypes.c_bool,False)
texture_proc_generate = multiprocessing.Value(ctypes.c_bool,False)
processOver= multiprocessing.Value(ctypes.c_bool,False)
texture_is_loading= multiprocessing.Value(ctypes.c_bool,False)
#menu_tex= None

shared_queue= multiprocessing.Queue(maxsize=2)

#funzione eseguita dal subprocesso
def tex_modify_proc_routine(shared_queue, texture_proc_done, texture_proc_generate,processOver,menu_width,texture_is_loading):
    
    #setup
    texControl= TextureControl(menu_width)

    #non bellissimo ma almeno dovrebbe essere indolore
    menu_dict= {}
    menu_dict['param1'] = 7
    menu_dict['param2'] = 6
    menu_dict['param3'] = 8
    menu_dict['param4'] = 3
    menu_dict['oaram5'] = 1
    texControl.generateTexture(menu_dict,'param1')
    
    #ciclo
    while(1):
        #print("subprocesso avviato, flag generazione: ")
        #print(texture_proc_generate.value)
        #print("subprocesso avviato, flag processOver: ")
        #print(processOver.value)
        
        if(texture_proc_generate.value  == True):
            print("sono nel sub-processo e sto generando")

            print("dimensione coda prima di prendere quello che ci ha messo l'utente?:")
            print(shared_queue.qsize())
            
            received=shared_queue.get()
            print("ricevo status")
            status= received[0]
            print("ricevo param selezionato")
            selected_param= received[1]
            print("status:")
            print(status)
            
            print("parametro selezionato:")
            print(selected_param)

            texture_is_loading.value = True
            menu_tex= texControl.modifyTexture(status,selected_param)
            
            
            print("dimensione coda prima di metterci una texture?:")
            print(shared_queue.qsize())

            shared_queue.put(menu_tex)
            texture_proc_done.value= True
            texture_proc_generate.value= False


texture_modifying_process = multiprocessing.Process(target=tex_modify_proc_routine, args = (shared_queue, texture_proc_done, texture_proc_generate, processOver,menu_width,texture_is_loading ))
"""
Menu for the STL Visualizer app
"""


class MenuScreen(object):
    """
    Draws the menu

    """
    



    


    def __init__(self,control_mod):
        global controlMod,texControl,menu_width
        
        self.shader = 0
        self.vao = None
        self.window_vertices= [
         [0.3, 0.4, 0.0,1.0], # bottom right
        [+0.0, 1.0, 1.0,1.0],  # bottom left
         [0.0, 0.0, 1.0,1.0],
         [+1.0, 0.0, 0.5,1.0]    # top 
         ]
        
        self.menu_texture= None
        self.pixel_buffer= None
        self.mapped_pixel_buffer = None 
        self.tex = None 
        self.width=menu_width
        self.height=math.ceil(self.width/1.57)
        controlMod=control_mod
        
        
    
    def init_gl(self):
        global texture_modifying_process
        vertex_shader = compileShader(
            shader_string("""
            
            
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
            
            

            const vec3 vertices[4] = vec3[4](
              vec3(-0.45, 0.5, -0.5), // 0: lower left rear
              vec3(+0.45, 0.5, -0.5), // 1: lower right rear
              vec3(-0.45, +1.5, -0.5), // 2: upper left rear
              vec3(+0.45, +1.5, -0.5) // 3: upper right rear
            );
            
            const vec2 texCoords[4]= vec2[4](
            vec2(0.0, 1.0), // 0: lower left rear
            vec2(1.0, 1.0), // 1: lower right rear
            vec2(0.0, 0.0), // 2: upper left rear
            vec2(1.0, 0.0) // 3: upper right rear

            );

           

            out vec2 texCoord; 
            
            void main() {
             
             
              texCoord=texCoords[gl_VertexID];
              gl_Position = Projection * ModelView * vec4(vertices[gl_VertexID] , 1.0);
            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(
            shader_string("""
            out vec4 FragColor;
            uniform sampler2D Tex;
            in vec2 texCoord;

    
            void main() {
              //FragColor =  vec4(0.5,0.0,0.9,1.0);
              FragColor = texture(Tex, texCoord);
            }
            """), 
            GL_FRAGMENT_SHADER)

        success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS);
        print("vertex:")
        print(success)
        print(glGetShaderInfoLog(vertex_shader))
        success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS);
        print("fragment:")
        print(success)
        print(glGetShaderInfoLog(fragment_shader))
        print("program:")
        self.shader = compileProgram(vertex_shader, fragment_shader)
        glGetProgramInfoLog(self.shader)
        error=glGetError()
        if error != 0:
            print(glGetError())
        success=0
        success = glGetProgramiv(self.shader, GL_LINK_STATUS);
        print(success)
        print(glGetProgramInfoLog(self.shader))

        self.vao = glGenVertexArrays(1)
        
        glBindVertexArray(self.vao)
        #print(sizeof(GLfloat))
        
        
        

     

   
        glEnable(GL_DEPTH_TEST)   

        #inizializzo texture
        self.menu_texture = glGenTextures(1)
        #print("generazione nome texture:")
        #print(self.menu_texture)
        #time.sleep(5)
        self.tex = texControl.generateTexture(controlMod.menuStatus.menu_dict,'param1')
        
        #questa istruzione va commentata se non uso più grayscale
        #glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        
        glBindTexture(GL_TEXTURE_2D, self.menu_texture)
        
        #il formato interno GL_RGBA8 assieme al leggere ogni dato come un byte senza segno sono necessari per visualizzare correttametne il logo
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8,self.width,self.height,0,GL_RGBA,GL_UNSIGNED_BYTE,self.tex)
        #glTexImage2D(GL_TEXTURE_2D, 0, GL_R8,self.width,self.height,0,GL_RED,GL_UNSIGNED_BYTE,self.tex)
        
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        

        self.pixel_buffer=glGenBuffers(1)
        #glBindBuffer(GL_PIXEL_UNPACK_BUFFER,self.pixel_buffer)
        #glBufferData(GL_PIXEL_UNPACK_BUFFER,1100*700*16, None, GL_STREAM_DRAW)
        #glBindBuffer(GL_PIXEL_UNPACK_BUFFER,0)
        
        texture_modifying_process.start()
        time.sleep(3)

    def display_gl(self, modelview, projection):
        global shared_queue,menu_tex,texture_proc_generate,texture_proc_done,texture_is_loading
        status,selected_param=controlMod.menuControl()

        if(status['enabled']):
            print("menù abilitato")
            glUseProgram(self.shader)
            glUniformMatrix4fv(0, 1, False, projection)
            glUniformMatrix4fv(4, 1, False, modelview)
            glBindVertexArray(self.vao)
            #comprendi come aggiornare texture
            
            glBindTexture(GL_TEXTURE_2D, self.menu_texture)


           

            if(status['modified'] and texture_is_loading.value == False):
                #sposta questa istruzione dentro un processo separato,rendi la generazione delle texture asincrona
                #self.tex=texControl.modifyTexture(status,selected_param)
                print("ho modificato, mando su queue?")
               
                shared_queue.put([status,selected_param])
                
                texture_proc_generate.value=True
                #il sub-processo poi renderà questa ultima variabile falsa quando ha finito
                
                

            if(texture_proc_done.value == True):
                print("il sub-processo ha finito")
                self.tex=shared_queue.get()
                texture_is_loading.value = False
                glTexSubImage2D(GL_TEXTURE_2D, 0,0,0,self.width,self.height,GL_RGBA,GL_UNSIGNED_BYTE,self.tex)
                #glTexSubImage2D(GL_TEXTURE_2D, 0,0,0,self.width,self.height,GL_RED,GL_UNSIGNED_BYTE,self.tex)
                
                texture_proc_done.value=False

               

                
            


            glDrawArrays(GL_TRIANGLE_STRIP,0, 4)
            
            error=glGetError()
            if error != 0:
                print(error)

            

    
    def dispose_gl(self):
        global processOver
        processOver.value=True
        texture_modifying_process.join()
        glDeleteProgram(self.shader)
        
        self.shader = 0
        if self.vao:
            glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0
