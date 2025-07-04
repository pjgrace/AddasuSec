import json
import falcon
from Runtimes.runtime import runtime
from MetaArchitecture.MetaArchitecture import MetaArchitecture  # Assume it's available

meta = MetaArchitecture()
rt = runtime(meta)

class CreateComponentResource:
    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        module = data.get('module')
        component = data.get('component')
        result = rt.create(type_, module, component)
        url_ret = meta.getComponentAttributeValue(component, "Host")
        if url_ret is None:
            url_ret = component
        resp.media = {'status': 'created', 'result': url_ret}
        print(url_ret)

class DeleteComponentResource:
    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        component_id = data.get('component_id')
        result = rt.delete(type_, component_id)
        resp.media = {'status': 'deleted', 'result': result}


class ConnectResource:
    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        src = data.get('component_src')
        intf = data.get('component_intf')
        intf_type = data.get('intf_type')
        result = rt.connect(type_, src, intf, intf_type)
        resp.media = {'status': 'connected', 'result': result}


class DisconnectResource:
    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        src = data.get('component_src')
        intf = data.get('component_intf')
        intf_type = data.get('intf_type')
        result = rt.disconnect(type_, src, intf, intf_type)
        resp.media = {'status': 'disconnected', 'result': result}