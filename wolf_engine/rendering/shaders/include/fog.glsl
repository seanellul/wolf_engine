// Shared fog calculation — exponential squared fog
// Call apply_fog(color) in your fragment shader after all shading

const vec3 fog_color = vec3(0.05);
const float fog_density = 0.015;

vec3 apply_fog(vec3 color) {
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    return mix(color, fog_color, 1.0 - exp2(-fog_density * fog_dist * fog_dist));
}
