import os
import struct
import time
import assimp_py
import numpy
import ctypes

from OpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sdl2
from sdl2 import *
post_flags = (assimp_py.Process_CalcTangentSpace)
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768

  

class STLloader:
    model=[]
    

    #draw the models faces
    # def draw(self):
    #     glEnable(GL_DEPTH_TEST)
    #     for m in self.model.meshes:
    #         print(dir(m))
    #         print("\n")
    #         print(m.num_vertices)
    #         print(len(m.indices))
    #         print(len(m.normals))
    #         i=0
            
    #         glBegin(GL_TRIANGLES)
        

    #         #glBufferData(GL_ARRAY_BUFFER, m.num_vertices, numpy.array(m.vertices), GL_STATIC_DRAW)
    #         #glDrawArrays(GL_TRIANGLES, 0, m.num_vertices);

    #         for i in range(m.num_vertices):
    #             glNormal3f(m.normals[i][0],m.normals[i][1],m.normals[i][2])
    #             glVertex3f(m.vertices[i][0],m.vertices[i][1],m.vertices[i][2])
                
                
    #         glEnd()    
        
        
  
    #load stl file detects if the file is a text file or binary file
    def load_stl(self,filename):
        #read start of file to determine if its a binay stl file or a ascii stl file
        self.model = assimp_py.ImportFile(filename, post_flags)
  





    
#main program loop
def main():


    model1=STLloader()
    #self.model1.load_stl(os.path.abspath('')+'/text.stl')
    model1.load_stl('C:\\Users\\mrapo\\AppData\\Local\\Temp\\MRI.stl')

    


if __name__ == '__main__':
    print("kill with ctrl-C (no frills here!)")
    main()
