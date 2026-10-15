# CREDIT-STAMP: (c) 2026 Tanachat S. (TANACHAT007) / MEDTHAI - https://github.com/TANACHAT007/diy-spirometer - MIT
# screenshot of the RIGHT side (speaker holes) + mouthpiece, current document
import adsk.core, adsk.fusion, os
app = adsk.core.Application.get()
vp = app.activeViewport
cam = vp.camera
cam.isSmoothTransition = False
cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
cam.viewExtents = 34.0
cam.target = adsk.core.Point3D.create(14.0, 0, -9.0)
cam.eye = adsk.core.Point3D.create(14.0, 60.0, -9.0)
cam.upVector = adsk.core.Vector3D.create(0, 0, 1)
vp.camera = cam
vp.refresh()
out = os.path.join(os.path.expanduser('~'), 'fusion-projects', 'diy-spirometer', '03_renders', 'diy-spirometer_cu_speaker.png')
vp.saveAsImageFile(out, 1280, 960)
print(out)
