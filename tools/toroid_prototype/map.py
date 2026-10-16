"""Read the DES-039 SI field grid; explicit bounds and masked-cell rejection."""
import math
from pathlib import Path
import numpy as np

class FieldMap:
    def __init__(self,path):
        with np.load(Path(path),allow_pickle=False) as f:
            self.r=f['r_m'];self.z=f['z_m'];self.phi=f['phi_deg']
            self.b=f['B_total_cyl_T'];self.valid=f['valid_field']
        if not np.isclose(self.phi[-1]-self.phi[0],30):
            raise ValueError('expected a twelvefold 30 degree fundamental sector')

    def field(self,points):
        """Trilinear interpolation of (Br,Bphi,Bz), then rotate to Cartesian.

        Raises ValueError outside map or when ANY interpolation corner is masked.
        No extrapolation or replacement of conductor/guard NaNs with zeros.
        """
        p=np.asarray(points,dtype=float)
        if p.ndim!=2 or p.shape[1]!=3 or not np.isfinite(p).all():
            raise ValueError('points must be finite Nx3')
        rr=np.hypot(p[:,0],p[:,1]); ph=np.arctan2(p[:,1],p[:,0])
        phi=np.degrees(ph)%30
        coordinates=[rr,p[:,2],phi]; axes=[self.r,self.z,self.phi]
        indices=[];frac=[]
        for q,axis in zip(coordinates,axes):
            if np.any((q<axis[0])|(q>axis[-1])):
                raise ValueError('point outside field-map domain')
            i=np.clip(np.searchsorted(axis,q,side='right')-1,0,len(axis)-2)
            indices.append(i);frac.append((q-axis[i])/(axis[i+1]-axis[i]))
        result=np.zeros((len(p),3))
        for a in (0,1):
            for b in (0,1):
                for c in (0,1):
                    cell=tuple(i+k for i,k in zip(indices,(a,b,c)))
                    if not self.valid[cell].all():
                        raise ValueError('interpolation stencil intersects winding/guard mask')
                    weight=np.ones(len(p))
                    for t,k in zip(frac,(a,b,c)):weight *= t if k else 1-t
                    result += self.b[cell]*weight[:,None]
        cs,sn=np.cos(ph),np.sin(ph)
        return np.column_stack((result[:,0]*cs-result[:,1]*sn,
                                result[:,0]*sn+result[:,1]*cs,result[:,2]))
