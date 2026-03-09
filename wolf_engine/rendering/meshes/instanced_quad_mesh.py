from wolf_engine.rendering.meshes.quad_mesh import QuadMesh
import moderngl as mgl
import numpy as np


class InstancedQuadMesh:
    MAX_INSTANCES = 256

    def __init__(self, eng, objects, shader_program: mgl.Program):
        self.ctx = eng.app.ctx
        self.program = shader_program
        #
        self.objects = objects
        self.num_instances = len(objects)

        # quad vertex buffer
        self.quad_vbo = self.ctx.buffer(QuadMesh.get_vertex_data(self))

        # pre-allocate instance buffers at max capacity
        self.m_model_vbo = self.ctx.buffer(reserve=self.MAX_INSTANCES * 16 * 4)  # 16 floats * 4 bytes
        self.tex_id_vbo = self.ctx.buffer(reserve=self.MAX_INSTANCES * 4)        # 1 int * 4 bytes

        # build VAO once
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.quad_vbo, '4f 2f /v', 'in_position', 'in_uv'),
                (self.m_model_vbo, '16f /i', 'm_model',),
                (self.tex_id_vbo, '1i /i', 'in_tex_id'),
            ],
            skip_errors=True
        )

    def update_buffers(self):
        m_model_list, tex_id_list = [], []

        for obj in self.objects:
            m_model_list += sum(obj.m_model.to_list(), [])
            tex_id_list += [obj.tex_id]

        self.m_model_vbo.write(np.array(m_model_list, dtype='float32'))
        self.tex_id_vbo.write(np.array(tex_id_list, dtype='int32'))

    def render(self):
        self.num_instances = len(self.objects)
        if self.num_instances:
            self.update_buffers()
            self.vao.render(instances=self.num_instances)
