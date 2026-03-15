from __future__ import annotations

import ctypes
import subprocess
import time

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
KEYEVENTF_KEYUP = 0x0002

NOW_PLAYING_SCRIPT = """
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime | Out-Null
$null = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager,Windows.Media.Control,ContentType=WindowsRuntime]
$manager = [Windows.Media.Control.GlobalSystemMediaTransportControlsSessionManager]::RequestAsync().GetAwaiter().GetResult()
$session = $manager.GetCurrentSession()
if ($null -eq $session) { return }
$properties = $session.TryGetMediaPropertiesAsync().GetAwaiter().GetResult()
if ($null -ne $properties -and -not [string]::IsNullOrWhiteSpace($properties.Title)) {
    $properties.Title
}
"""


def press_media_play_pause() -> None:
    ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
    time.sleep(0.03)
    ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_KEYUP, 0)


def press_media_next_track() -> None:
    ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, 0, 0)
    time.sleep(0.03)
    ctypes.windll.user32.keybd_event(VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_KEYUP, 0)


def get_now_playing_title() -> str:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", NOW_PLAYING_SCRIPT],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()
