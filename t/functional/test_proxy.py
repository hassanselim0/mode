from unittest.mock import MagicMock, Mock
import pytest
from mode import Service, label, shortlabel
from mode.proxy import ServiceProxy
from mode.utils.mocks import AsyncMock


class Proxy(ServiceProxy):

    def __init__(self, service, *args, **kwargs):
        self._proxied_service = service
        super().__init__(*args, **kwargs)

    @property
    def _service(self):
        return self._proxied_service


class test_Proxy:

    @pytest.fixture
    def service(self):
        s = Mock(name='service', autospec=Service)
        s.attach_mock(AsyncMock(), 'add_runtime_dependency')
        s.attach_mock(AsyncMock(), 'add_async_context')
        s.attach_mock(AsyncMock(), 'start')
        s.attach_mock(AsyncMock(), 'maybe_start')
        s.attach_mock(AsyncMock(), 'crash')
        s.attach_mock(AsyncMock(), 'stop')
        s.attach_mock(AsyncMock(), 'restart')
        s.attach_mock(AsyncMock(), 'wait_until_stopped')
        return s

    @pytest.fixture
    def subservice(self):
        return Mock(name='subservice')

    @pytest.fixture
    def proxy(self, *, service):
        return Proxy(service)

    def test_add_dependency(self, *, proxy, service, subservice):
        proxy.add_dependency(subservice)
        service.add_dependency.assert_called_once_with(subservice)

    @pytest.mark.asyncio
    async def test_add_runtime_dependency(self, *, proxy, service, subservice):
        ret = await proxy.add_runtime_dependency(subservice)
        service.add_runtime_dependency.assert_called_once_with(subservice)
        assert ret is service.add_runtime_dependency.coro()

    @pytest.mark.asyncio
    async def test_add_async_context(self, *, proxy, service):
        context = MagicMock()
        ret = await proxy.add_async_context(context)
        service.add_async_context.assert_called_once_with(context)
        assert ret is service.add_async_context.coro()

    def test_add_context(self, *, proxy, service):
        context = MagicMock()
        ret = proxy.add_context(context)
        service.add_context.assert_called_once_with(context)
        assert ret is service.add_context()

    @pytest.mark.asyncio
    async def test_start(self, *, proxy, service):
        await proxy.start()
        service.start.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_maybe_start(self, *, proxy, service):
        await proxy.maybe_start()
        service.maybe_start.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_crash(self, *, proxy, service):
        exc = KeyError()
        await proxy.crash(exc)
        service.crash.assert_called_once_with(exc)

    def test__crash(self, *, proxy, service):
        exc = KeyError()
        proxy._crash(exc)
        service._crash.assert_called_once_with(exc)

    @pytest.mark.asyncio
    async def test_stop(self, *, proxy, service):
        await proxy.stop()
        service.stop.assert_called_once_with()

    def test_service_reset(self, *, proxy, service):
        proxy.service_reset()
        service.service_reset.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_restart(self, *, proxy, service):
        await proxy.restart()
        service.restart.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_wait_until_stopped(self, *, proxy, service):
        await proxy.wait_until_stopped()
        service.wait_until_stopped.assert_called_once_with()

    def test_set_shutdown(self, *, proxy, service):
        proxy.set_shutdown()
        service.set_shutdown.assert_called_once_with()

    def test_started(self, *, proxy, service):
        assert proxy.started is service.started

    def test_crashed(self, *, proxy, service):
        assert proxy.crashed is service.crashed

    def test_should_stop(self, *, proxy, service):
        assert proxy.should_stop is service.should_stop

    def test_state(self, *, proxy, service):
        assert proxy.state is service.state

    def test_label(self, *, proxy):
        assert label(proxy) == 'Proxy'

    def test_shortlabel(self, *, proxy):
        assert shortlabel(proxy) == 'Proxy'

    def test_beacon(self, *, proxy, service):
        assert proxy.beacon is service.beacon
        new_beacon = proxy.beacon = Mock(name='new_beacon')
        assert service.beacon is new_beacon
