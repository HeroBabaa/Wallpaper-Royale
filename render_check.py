import comtypes.client
from comtypes import GUID, HRESULT, COMMETHOD
from ctypes import POINTER, byref
from ctypes.wintypes import HWND, BOOL







# Define the IVirtualDesktopManager interface.
class IVirtualDesktopManager(comtypes.IUnknown):
    _iid_ = GUID("{a5cd92ff-29be-454c-8d04-d82879fb3f1b}")
    _methods_ = [
        # By specifying 'retval' on the out parameter, comtypes returns the BOOL value directly.
        COMMETHOD([], HRESULT, "IsWindowOnCurrentDesktop",
                  (['in'], HWND, 'topLevelWindow'),
                  (['out', 'retval'], POINTER(BOOL), 'pfOnCurrentDesktop')),
    ]

def is_window_on_current_desktop(hwnd):
    """
    Uses the IVirtualDesktopManager COM interface to check if the given window (by handle)
    is on the current virtual desktop.
    Returns True if the window is on the current desktop or if an error occurs.
    """
    try:
        CLSID_VirtualDesktopManager = GUID("{aa509086-5ca9-4c25-8f95-589d3c07b48a}")
        # Create the COM object using CoCreateInstance.
        vdm = comtypes.CoCreateInstance(CLSID_VirtualDesktopManager, interface=IVirtualDesktopManager)
        # Call the method with just the window handle.
        on_current = vdm.IsWindowOnCurrentDesktop(hwnd)
        return bool(on_current)
    except Exception as e:
        print("Virtual desktop check error:", e)
        # If there's an error, assume the window is visible.
        return True
