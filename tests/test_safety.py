from pathlib import Path

from ai_health_copilot.core.cleaner.safety import is_sensitive_path


def test_sensitive_browser_and_credential_names():
    assert is_sensitive_path(Path("C:/Users/x/AppData/Local/Google/Chrome/User Data/Default/Login Data"))
    assert is_sensitive_path(Path("C:/Users/x/AppData/Local/Chrome/User Data/Default/Cookies"))
    assert is_sensitive_path(Path("C:/Users/x/Downloads/passwords.txt"))
    assert is_sensitive_path(Path("C:/Users/x/Firefox/Profiles/abc/logins.json"))
    assert is_sensitive_path(Path("C:/Users/x/AppData/Roaming/Mozilla/Firefox/Profiles/abc/key4.db"))
    assert is_sensitive_path(Path("C:/keys/private.pem"))
    assert is_sensitive_path(Path("C:/Users/x/Desktop/bank.credit card scan.pdf"))


def test_non_sensitive_paths_allowed():
    assert not is_sensitive_path(Path("C:/Windows/Temp/junk_123.tmp"))
    assert not is_sensitive_path(Path("C:/Users/x/AppData/Local/Google/Chrome/User Data/Default/Cache/f_000001"))
    assert not is_sensitive_path(Path("C:/Users/x/Downloads/setup_installer.exe"))
    assert not is_sensitive_path(Path("C:/Windows/SoftwareDistribution/Download/wu_123.cab"))
    assert not is_sensitive_path(Path("C:/Windows/Prefetch/APP.EXE-1A2B.pf"))


def test_is_sensitive_accepts_strings():
    assert is_sensitive_path("C:/Users/x/Downloads/passwords.txt")
    assert not is_sensitive_path("C:/Users/x/Downloads/video.mp4")
