#import glm
import numpy
import openvr
import math
from textwrap import dedent
import itertools
from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
from OpenGL.GL.shaders import compileShader, compileProgram

from openvr.glframework import shader_string
from STLinto3DModel import STLloader
from controlModule import controlInputModule
loader=STLloader()
loader.load_stl('your path to an STL here')
model=loader.model 
controlMod= None

"""
Color cube for use in "hello world" openvr apps
"""


class ThreeDKnee(object):
    """
    Draws a knee
    
    """
    
    def __init__(self, pose_array):
        global controlMod
        self.shader = 0
        self.vao = None
        self.vertex_iterator=itertools.cycle(model.meshes[0].vertices)
        self.num_vert=model.meshes[0].num_vertices
        self.pose_array= pose_array
        controlMod=controlInputModule(pose_array)





    def find_headset_pose(self):
        for i in range(1, len(self.pose_array)):
            pose = self.pose_array[i]
            #print (self.pose_array[i].mDeviceToAbsoluteTracking)
            if not pose.bDeviceIsConnected:
                continue
            if not pose.bPoseIsValid:
                continue
                device_class = openvr.VRSystem().getTrackedDeviceClass(i)
                if device_class == openvr.TrackedDeviceClass_HMD:
                    print ("controller trovato")
                    return pose




    #codice grafica
    
    def init_gl(self):
  #servono model e view matrix separate
        vertex_shader = compileShader(#glVertex*2 quando hai fatto l'interlacciamento con le normali
            shader_string("""
            // Adapted from @jherico's RiftDemo.py in pyovr
            
            layout(location = 0) uniform mat4 Projection = mat4(1);
            layout(location = 4) uniform mat4 ModelView = mat4(1);
            
            layout(location = 8) uniform mat4 Model = mat4(1);

            layout(location = 12) uniform vec3 lightPos_world;

            layout(location = 15) uniform vec3 translateDelta;

            layout (location = 18) uniform mat4 UserControlRotationMatrix = mat4(1);
            
            float Size = 0.7;
            
            layout(std430, binding = 3) buffer positionBuffer
            {
                vec4 position_and_normals[];
            };
            
            mat4 View= ModelView/Model;




            //Rotation transformation

            mat4 rotation3dX(float angle) {
            float s = sin(angle);
            float c = cos(angle);

            return mat4(
            1.0, 0.0, 0.0, 0.0,
            0.0, c, s, 0.0,
            0.0, -s, c, 0.0,
            0.0, 0.0, 0.0, 1.0);
            }

            mat4 rotation3dY(float angle) {
            float s = sin(angle);
            float c = cos(angle);

            return mat4(
            c, 0.0, -s, 0.0,
            0.0, 1.0, 0.0, 0.0,
            s, 0.0, c, 0.0,
            0.0, 0.0, 0.0, 1.0);
            }

            mat4 rotation3dZ(float angle) {
                float s = sin(angle);
                float c = cos(angle);

                return mat4(
                    c, s, 0.0, 0.0,
                    -s, c, 0.0, 0.0,
                    0.0, 0.0, 1.0, 0.0,
                    0.0, 0.0, 0.0, 1.0);
                }

            mat4 rotationMatrix(vec3 axis, float angle)
                {
                    axis = normalize(axis);
                    float s = sin(angle);
                    float c = cos(angle);
                    float oc = 1.0 - c;
    
                return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                            oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                            oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                            0.0,                                0.0,                                0.0,                                1.0);
                }

            mat4 TranslationMatrix(float x, float y, float z)
            {
                return mat4(1.0, 0.0, 0.0, 0.0,
                            0.0, 1.0, 0.0, 0.0,
                            0.0, 0.0, 1.0, 0.0,
                            x, y, z, 1.0);

            }




            



            out vec3 Normal_cameraspace;
            out vec3 EyeDirection_cameraspace;
            out vec3 LightDirection_cameraspace;
            out vec3 Position_worldspace;
            out vec3 LightPosition_worldspace;

            vec3 vertexNormal_modelspace;
            vec3 currpos;
            
            mat4 DefaultTranslationMatrix = TranslationMatrix(0.1,1.3,-0.8);
            mat4 DefaultRotationMatrix = rotationMatrix(vec3(0,0,1), 3.14) * rotationMatrix(vec3(0,1,0), -1.57);
            
            mat4 UserControlTranslationMatrix = TranslationMatrix(translateDelta.x,translateDelta.y,translateDelta.z);
             



            mat4 Modified_Model= UserControlTranslationMatrix * DefaultTranslationMatrix * UserControlRotationMatrix * DefaultRotationMatrix ;

            void main() {

              
             

              vertexNormal_modelspace = normalize(vec3(position_and_normals[(gl_VertexID*2)+1].x, position_and_normals[(gl_VertexID*2)+1].y,position_and_normals[(gl_VertexID*2)+1].z));
              vertexNormal_modelspace= (mat3(transpose(inverse(Modified_Model))) * vertexNormal_modelspace);
              

              //vertexNormal_modelspace= (UserControlRotationMatrix * vec4(vertexNormal_modelspace,1.0)).xyz;
              //vertexNormal_modelspace = (DefaultTranslationMatrix * vec4(vertexNormal_modelspace,1.0)).xyz;

              Normal_cameraspace = ( ModelView* vec4(vertexNormal_modelspace,1.0)).xyz;
              
              //cerco di generare il modello centrato rispetto all'origine
              //currpos= vec3(position_and_normals[gl_VertexID*2].x-0.55, position_and_normals[gl_VertexID*2].y,position_and_normals[gl_VertexID*2].z- 0.57);
              float x_coeff;
              float z_coeff;
              float y_coeff;
              x_coeff = -0.67;
              y_coeff = -0.5;
              z_coeff = -0.47;
              
   
              currpos = vec3(position_and_normals[gl_VertexID*2].x+x_coeff, position_and_normals[gl_VertexID*2].y+y_coeff,position_and_normals[gl_VertexID*2].z+z_coeff);
              
              currpos= (Modified_Model * vec4(currpos,1.0)).xyz;

              //ruoto sull'asse dell'origine
              //currpos= (UserControlRotationMatrix  * vec4(currpos,1.0)).xyz;
              // traslo davanti agli occhi dell'utente
              //currpos = (DefaultTranslationMatrix * vec4(currpos,1.0)).xyz;

              


              Position_worldspace = (Model * vec4(currpos,1)).xyz;

              vec3 vertexPosition_cameraspace = (ModelView * vec4(currpos* Size,1)).xyz;
              EyeDirection_cameraspace = vec3(0,0,0) - vertexPosition_cameraspace;

              

              LightPosition_worldspace = vec3(0,0.4,-0.3);

              vec3 LightPosition_cameraspace = ( View * vec4(LightPosition_worldspace,1)).xyz;
              LightDirection_cameraspace = LightPosition_cameraspace + EyeDirection_cameraspace;

              gl_Position = Projection * ModelView * vec4(currpos* Size, 1.0);



            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(
            shader_string("""
            in vec3 Normal_cameraspace;
            in vec3 EyeDirection_cameraspace;
            in vec3 LightDirection_cameraspace;
            in vec3 Position_worldspace;
            in vec3 LightPosition_worldspace;
            out vec3 color;
            
            
            void main() {
              vec3 LightColor = vec3(0.8,0.8,0.8);
              float LightPower = 0.65f;

              float distance = length( LightPosition_worldspace - Position_worldspace );

              // Normal of the computed fragment, in camera space
              vec3 n =  normalize(Normal_cameraspace) ;
              // Direction of the light (from the fragment to the light)
              vec3 l = normalize(LightDirection_cameraspace) ;
              // Cosine of the angle between the normal and the light direction, 
              // clamped above 0
              //  - light is at the vertical of the triangle -> 1
              //  - light is perpendicular to the triangle -> 0
              //  - light is behind the triangle -> 0
              float cosTheta = clamp( dot( n,l ), 0,1 );

              // Eye vector (towards the camera)
              vec3 E = normalize(EyeDirection_cameraspace);
              // Direction in which the triangle reflects the light
              vec3 R = reflect(-l,n);
              // Cosine of the angle between the Eye vector and the Reflect vector,
              // clamped to 0
              //  - Looking into the reflection -> 1
              //  - Looking elsewhere -> < 1
              float cosAlpha = clamp( dot( E,R ), 0,1 );
              
              vec3 MaterialDiffuseColor = vec3(0.8, 0.8, 0.8);
              vec3 MaterialAmbientColor = vec3(0.3,0.3,0.3) * MaterialDiffuseColor;
              vec3 MaterialSpecularColor = vec3(0.5,0.5,0.5);


              color = // Ambient : simulates indirect lighting
                        MaterialAmbientColor +
                        // Diffuse : "color" of the object
                            MaterialDiffuseColor * LightColor * LightPower * cosTheta ;
                        // Specular : reflective highlight, like a mirror
                           // MaterialSpecularColor * LightColor * LightPower * pow(cosAlpha,5) / (distance*distance);
            }
            """), 
            GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)
        #
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        # array_buffer=glGenBuffers(1)
        # glBindBuffer(GL_ARRAY_BUFFER,array_buffer)
        # glBufferData(GL_ARRAY_BUFFER, model.meshes[0].num_vertices * sizeof(GLfloat*3), numpy.array(model.meshes[0].vertices), GL_STATIC_DRAW)

        # posAttrib = glGetAttribLocation(program, "position")
        # glVertexAttribPointer(posAttrib, 3, GL_FLOAT, GL_TRUE, 0, 0);
        # glEnableVertexAttribArray(posAttrib);
        # glEnable(GL_DEPTH_TEST)
        print("proprietà oggetto mesh in python:")
        print(dir(model.meshes[0]))
        print("\n")
        print("num vertici:")
        print(model.meshes[0].num_vertices)
        print("num uv:")
        print(model.meshes[0].num_uv_components)
        print("colori:")
        print(model.meshes[0].colors)
        print("lunghezza array indici:")
        print(len(model.meshes[0].indices))
        print("lunghezza array normali:")
        print(len(model.meshes[0].normals))


        #converto i dati di assimp in array numpy 
        vertices_array=numpy.array(model.meshes[0].vertices)
        normals_array=numpy.array(model.meshes[0].normals)

        
        #normalizzazione
        min_val = numpy.min(vertices_array)
        max_val = numpy.max(vertices_array)
        vertices_array_normalized = (vertices_array - min_val) / (max_val - min_val)

        #costruzione array finale
        vertices_and_normals= numpy.ones((vertices_array.size+normals_array.size,4),dtype=numpy.float32)
        

        for index,v in enumerate(vertices_array_normalized): #aggiungo coordinata W altrimenti lo shader non lo legge bene
                vertices_and_normals[index*2][0]=v[0]
                vertices_and_normals[index*2][1]=v[1]
                vertices_and_normals[index*2][2]=v[2]
                vertices_and_normals[(index*2)+1][0]=normals_array[index][0]
                vertices_and_normals[(index*2)+1][1]=normals_array[index][1]
                vertices_and_normals[(index*2)+1][2]=normals_array[index][2]


        ssbo=glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, (vertices_array.size -2) * vertices_array.itemsize, vertices_and_normals, GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 3, ssbo)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, 0)
        glEnable(GL_DEPTH_TEST)        
    




        
    def display_gl(self, modelview, projection):
        
        translationDelta,rotationMatrix = controlMod.control()

    


        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        model=[[1,1,1,1],[1,1,1,1],[1,1,1,1],[1,1,1,1]]
        light_pos=[0.0,0.0,0.0]
        glUniformMatrix4fv(8, 1, False, numpy.array(model))
        #prendi luce dal punto in cui si trova l'elmetto
        HMD_pose=self.pose_array[0]
  
        HMD_matrix=HMD_pose.mDeviceToAbsoluteTracking
        light_pos=[HMD_matrix[0][3],HMD_matrix[1][3],HMD_matrix[2][3]]
        #print(light_pos)
        glUniform3f(12, light_pos[0], light_pos[1],light_pos[2])
        glUniform3f(15, translationDelta[0], translationDelta[1],translationDelta[2])
        glUniformMatrix4fv(18, 1, False, numpy.array(rotationMatrix))

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.num_vert)

    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        self.shader = 0
        if self.vao:
            glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0

