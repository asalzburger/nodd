"""Strict unscaled, centred two-section prism contract for barrel CSG audits."""
import math
from edge_native import native_capacity as inherited_capacity


def check_sections(shape):
    kind=str(shape.ClassName())
    if kind=='TGeoCompositeShape':
        node=shape.GetBoolNode();check_sections(node.GetLeftShape());check_sections(node.GetRightShape());return
    if kind!='TGeoXtru':return
    if shape.GetNz()!=2:raise ValueError('native prism requires two sections')
    half=(shape.GetZ(1)-shape.GetZ(0))/2
    if half<=0 or not math.isclose(shape.GetZ(0),-half,rel_tol=0,abs_tol=1e-10) or not math.isclose(shape.GetZ(1),half,rel_tol=0,abs_tol=1e-10):raise ValueError('native prism sections must be centred')
    for i in (0,1):
        if abs(shape.GetXOffset(i))>1e-10 or abs(shape.GetYOffset(i))>1e-10 or not math.isclose(shape.GetScale(i),1,rel_tol=0,abs_tol=1e-10):raise ValueError('native prism offsets/scales unsupported')


def native_capacity(shape):
    check_sections(shape)
    return inherited_capacity(shape)
