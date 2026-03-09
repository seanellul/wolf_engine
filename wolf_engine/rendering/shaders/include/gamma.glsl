// Shared gamma correction — sRGB encode/decode
// Call gamma_decode(color) before shading, gamma_encode(color) after

const vec3 gamma = vec3(2.2);
const vec3 inv_gamma = 1.0 / gamma;

vec3 gamma_decode(vec3 color) {
    return pow(color, gamma);
}

vec3 gamma_encode(vec3 color) {
    return pow(color, inv_gamma);
}
