#version 330 core

#include "include/gamma.glsl"
#include "include/fog.glsl"

out vec4 frag_color;

in vec2 uv;
flat in int tex_id;

uniform sampler2DArray u_texture_array_0;


void main() {
    vec3 tex_col = texture(u_texture_array_0, vec3(uv, tex_id)).rgb;
    tex_col = gamma_decode(tex_col);

    tex_col = apply_fog(tex_col);

    tex_col = gamma_encode(tex_col);
    frag_color = vec4(tex_col, 1.0);
}
