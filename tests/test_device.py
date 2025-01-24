import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from pygryfsmart.device import Device

@pytest.fixture
def mock_device():
    device = Device(port="/dev/ttyUSB0")
    device.send_data = AsyncMock()
    device.open_connection = AsyncMock()
    device.read_data = AsyncMock()
    device.close_connection = AsyncMock()
    return device

@pytest.mark.asyncio
async def test_set_out(mock_device):
    await mock_device.set_out(1, 3, 1)
    mock_device.send_data.assert_called_once_with("AT+SetOut=1,0,0,1,0,0,0\n\r")

@pytest.mark.asyncio
async def test_send_data(mock_device):
    await mock_device.send_data("AT+TestCommand\n\r")
    mock_device.send_data.assert_called_once_with("AT+TestCommand\n\r")

@pytest.mark.asyncio
async def test_set_key_time(mock_device):
    await mock_device.set_key_time(100, 200, 1, 2, 1)
    mock_device.send_data.assert_called_once_with("AT+Key=1,2,100,200,1\n\r")

@pytest.mark.asyncio
async def test_set_rol(mock_device):
    await mock_device.set_rol(1, 2, 100, 1)
    mock_device.send_data.assert_called_once_with("AT+SetRol=1,100,0,1,0,0,102\n\r")

@pytest.mark.asyncio
async def test_reset(mock_device):
    mock_device.data["OUT"] = {0: [1, 0, 1, 0, 1, 0]}
    await mock_device.reset(0, update_states=True)
    mock_device.send_data.assert_any_call("AT+RST=0\n\r")
    mock_device.send_data.assert_any_call("AT+SetOut=0,1,0,1,0,1,0\n\r")
