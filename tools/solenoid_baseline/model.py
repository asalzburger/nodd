"""PROTOTYPE vacuum finite winding and PR6 energy/volume sizing, SI units.

Adapted from PR6 tools/magnetic_study/sizing.py at d2437a7d84dbd02eed098c2a6341c5447cc42701.
Uniform azimuthal current density throughout a finite annular winding pack.
No steel, conductor critical surface, quench or production geometry model.
"""
from functools import lru_cache
import math
import numpy as np

MU0 = 4e-7 * math.pi

@lru_cache(maxsize=12)
def gauss(n):
    if isinstance(n, bool) or not isinstance(n, int) or n < 2:
        raise ValueError('quadrature orders must be integers >=2')
    return np.polynomial.legendre.leggauss(n)


def pack_current(a, b, length, b0):
    if not all(math.isfinite(x) for x in (a, b, length, b0)):
        raise ValueError('finite inputs required')
    if not 0 < a < b or length <= 0 or abs(b0) > 5:
        raise ValueError('invalid winding bounds or central field above 5 T')
    h = length / 2
    return b0 / (MU0 * h * (math.asinh(b / h) - math.asinh(a / h)))


def stored_energy(a, b, length, b0, nr=48, nphi=192):
    """All-space vacuum energy via Neumann integral with analytic axial integration.

    G(d) = integral_0^L (L-u)/sqrt(u^2+d^2) du.
    Endpoint-free quadrature handles the integrable logarithmic singularity.
    """
    j = pack_current(a, b, length, b0)
    x, w = gauss(nr)
    r = (a + b) / 2 + (b - a) / 2 * x
    w = w * (b - a) / 2
    x, v = gauss(nphi)
    phi = (x + 1) * math.pi / 2
    v = v * math.pi / 2
    rr = r[:, None] * r[None, :]
    d = np.sqrt((r[:, None, None] - r[None, :, None])**2
                + 4 * rr[:, :, None] * np.sin(phi / 2)**2)
    g = length * np.arcsinh(length / d) - np.hypot(length, d) + d
    angular = np.sum(g * (v * np.cos(phi))[None, None, :], axis=2)
    return float(MU0 * j * j * np.sum(w[:, None] * w[None, :] * rr * angular))


def axis_field(z, a, b, length, b0):
    j = pack_current(a, b, length, b0)
    def end(u):
        return 0 if u == 0 else u * (math.asinh(b / abs(u)) - math.asinh(a / abs(u)))
    return MU0 * j / 2 * (end(z + length / 2) - end(z - length / 2))


def validate_config(c, tracker):
    keys = ('central_field_T', 'central_field_max_T', 'vessel_inner_radius_m',
            'cold_mass_length_m', 'axial_gap_per_end_m', 'inner_radius_scale',
            'inner_radius_offset_m', 'outer_gap_scale', 'energy_per_cold_volume_J_m3',
            'winding_radial_fraction_of_cold_mass', 'assembly_outer_radius_m',
            'ecal_radial_gap_m', 'ecal_axial_gap_m')
    if not all(type(c[k]) in (int, float) and math.isfinite(c[k]) and c[k] > 0 for k in keys):
        raise ValueError('positive finite sizing inputs required')
    if c['central_field_T'] > c['central_field_max_T'] or c['central_field_max_T'] > 5:
        raise ValueError('central field cap exceeded')
    if not c['winding_radial_fraction_of_cold_mass'] <= 1:
        raise ValueError('winding must fit cold mass')
    if c['vessel_inner_radius_m'] <= tracker['tracker_region_rmax_mm'] / 1000:
        raise ValueError('vessel intersects tracker reservation')
    if c['cold_mass_length_m'] < 2 * tracker['tracker_region_zmax_mm'] / 1000:
        raise ValueError('winding does not cover tracker reservation axially')


def solve(c):
    rv, length, b0 = (c[k] for k in ('vessel_inner_radius_m', 'cold_mass_length_m', 'central_field_T'))
    a = rv * c['inner_radius_scale'] + c['inner_radius_offset_m']
    fraction, density = c['winding_radial_fraction_of_cold_mass'], c['energy_per_cold_volume_J_m3']
    def evaluate(t):
        return (stored_energy(a, a + fraction * t, length, b0),
                math.pi * ((a + t)**2 - a*a) * length)
    lo, hi = 1e-4, a
    if evaluate(lo)[0] <= density * evaluate(lo)[1]:
        raise ValueError('root below minimum thickness')
    while evaluate(hi)[0] > density * evaluate(hi)[1]:
        hi *= 2
        if hi > 100 * a:
            raise ValueError('cannot bracket cold-volume root')
    for _ in range(42):
        t = (lo + hi) / 2
        u, v = evaluate(t)
        if u > density * v:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    u, volume = evaluate(t)
    b = a + fraction * t
    energies = [stored_energy(a, b, length, b0, n, 4*n) for n in (24, 48, 96)]
    relative = abs(energies[-1] / energies[-2] - 1)
    if relative > 5e-4 or abs(u / (volume * density) - 1) > 1e-8:
        raise ValueError('energy convergence or volume closure failed')
    outer = a + t + c['outer_gap_scale'] * (a - rv)
    if outer >= c['assembly_outer_radius_m']:
        raise ValueError('vessel exceeds assembly reservation')
    return dict(vessel_inner_radius_m=rv, cold_inner_radius_m=a,
                winding_outer_radius_m=b, cold_outer_radius_m=a+t,
                vessel_outer_radius_m=outer, cold_mass_length_m=length,
                vessel_length_m=length+2*c['axial_gap_per_end_m'],
                central_field_T=b0, pack_J_A_mm2=pack_current(a, b, length, b0)/1e6,
                ampere_turns=pack_current(a, b, length, b0)*(b-a)*length,
                stored_energy_MJ=u/1e6, cold_volume_m3=volume,
                energy_density_MJ_m3=u/volume/1e6,
                energy_density_relative_residual=abs(u/(volume*density)-1),
                refinement_orders=[[24,96],[48,192],[96,384]],
                refinement_energy_MJ=[e/1e6 for e in energies], relative_refinement=relative,
                assembly_spare_radial_m=c['assembly_outer_radius_m']-outer,
                proposed_ecal_inner_radius_m=c['assembly_outer_radius_m']+c['ecal_radial_gap_m'],
                proposed_ecal_endcap_front_m=length/2+c['axial_gap_per_end_m']+c['ecal_axial_gap_m'],
                axis_field_T=[dict(z_m=z, Bz_T=axis_field(z,a,b,length,b0))
                              for z in (0., 1., 2., 3., 3.375, 3.6, 3.85)])
