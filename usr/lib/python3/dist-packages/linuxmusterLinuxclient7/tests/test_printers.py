from pathlib import Path
from unittest import mock
from .. import printers
import pytest, os

def test_translateSambaToIpp():
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan\\printer1") == (True, "ipp://linuxmuster.lan/printers/printer1")
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan\\") == (False, None)
    assert printers.translateSambaToIpp("\\\\linuxmuster.lan") == (False, None)
    assert printers.translateSambaToIpp("\\\\\\printer1") == (False, None)