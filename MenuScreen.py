

import numpy
import ctypes
import time
import math
import threading
from textwrap import dedent

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram

from openvr.glframework import shader_string
from controlModule import controlInputModule
from TextureControl import TextureControl
controlMod= None
texControl= None
"""
Menu for the STL Visualizer app
"""


class MenuScreen(object):
    """
    Draws the menu

    """


    def __init__(self,control_mod):
        global controlMod,texControl
        
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
        self.width=350
        self.height=math.ceil(self.width/1.57)
        controlMod=control_mod
        texControl=TextureControl(self.width)
        self.texture_modifying_thread = threading.Thread()

    
    def init_gl(self):
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
        
        
        vertices_array=numpy.array(self.window_vertices)

     

        
        glEnable(GL_DEPTH_TEST)   

        #inizializzo texture
        self.menu_texture = glGenTextures(1)
        #print("generazione nome texture:")
        #print(self.menu_texture)
        #time.sleep(5)
        self.tex = texControl.generateTexture(controlMod.menuStatus.menu_dict,'param1')
        
        #questa istruzione va commentata se non uso più grayscale
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        
        glBindTexture(GL_TEXTURE_2D, self.menu_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R8,self.width,self.height,0,GL_RED,GL_UNSIGNED_BYTE,self.tex)
        #glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        

        self.pixel_buffer=glGenBuffers(1)
        
        
        #self.texture_modifying_thread.start()
    def display_gl(self, modelview, projection):
        status,selected_param=controlMod.menuControl()

        if(status['enabled']):

            glUseProgram(self.shader)
            glUniformMatrix4fv(0, 1, False, projection)
            glUniformMatrix4fv(4, 1, False, modelview)
            glBindVertexArray(self.vao)
            #comprendi come aggiornare texture
            
            glBindTexture(GL_TEXTURE_2D, self.menu_texture)


           

            if(status['modified']):
                
                self.tex=texControl.modifyTexture(status,selected_param)
                
               
                glTexSubImage2D(GL_TEXTURE_2D, 0,0,0,self.width,self.height,GL_RED,GL_UNSIGNED_BYTE,self.tex)
        

                
            


            glDrawArrays(GL_TRIANGLE_STRIP,0, 4);
            
            error=glGetError()
            if error != 0:
                print(error)

            

    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        
        self.shader = 0
        if self.vao:
            glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0