"""Preserve the existing local Python sensitivity controls with pristine ACTS."""
import math
import pytest
import acts
from acts.examples import nodd

mm = acts.UnitConstants.mm
gctx = acts.GeometryContext.dangerouslyDefaultConstruct()

@pytest.mark.parametrize(
    "surface",
    [
        acts.Surface.createPlane(
            acts.Transform3.Identity(), acts.RectangleBounds(10.0, 5.0)
        ),
        acts.Surface.createDisc(
            acts.Transform3.Identity(), acts.RadialBounds(10.0, 20.0)
        ),
        acts.Surface.createCylinder(
            acts.Transform3.Identity(), acts.CylinderBounds(20.0, 50.0)
        ),
    ],
)
def test_surface_sensitivity_is_independent_of_identifier(surface):
    assert surface.isSensitive is False
    identifier = acts.GeometryIdentifier(sensitive=7)
    surface.assignGeometryId(identifier)
    assert surface.isSensitive is False

    surface.assignIsSensitive(isSensitive=True)
    assert surface.isSensitive is True
    assert surface.geometryId == identifier

    surface.assignIsSensitive(False)
    assert surface.isSensitive is False
    assert surface.geometryId == identifier


def test_python_sensitive_modules_in_layer_blueprint():
    surfaces = []
    for i in range(8):
        phi = i * math.tau / 8
        transform = (
            acts.Transform3(acts.Vector3(50 * math.cos(phi), 50 * math.sin(phi), 0))
            * acts.AngleAxis3(phi + math.pi / 2, acts.Vector3(0, 0, 1))
            * acts.AngleAxis3(math.pi / 2, acts.Vector3(1, 0, 0))
        )
        surface = acts.Surface.createPlane(transform, acts.RectangleBounds(10, 20))
        surface.assignIsSensitive(True)
        surfaces.append(surface)

    root = acts.Blueprint(envelope=acts.ExtentEnvelope(r=[1 * mm, 1 * mm]))
    layer = root.addLayer("sensitive-barrel")
    layer.layerType = acts.LayerBlueprintNode.LayerType.Cylinder
    layer.surfaces = surfaces
    layer.envelope = acts.ExtentEnvelope(r=[1 * mm, 1 * mm], z=[1 * mm, 1 * mm])
    options = acts.BlueprintOptions()
    options.defaultNavigationPolicyFactory = acts.NavigationPolicyFactory.make().add(
        acts.TryAllNavigationPolicy
    )
    geometry = root.construct(options, gctx, level=acts.logging.WARNING)
    visited = []
    geometry.visitSurfaces(visited.append)
    assert len(visited) == len(surfaces)
    assert all(surface.isSensitive for surface in visited)
    assert all(surface.geometryId.sensitive != 0 for surface in visited)
    assert len({surface.geometryId.value for surface in visited}) == len(surfaces)
