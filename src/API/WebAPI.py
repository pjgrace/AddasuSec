import json
import falcon
from Runtimes.runtime import runtime
from MetaArchitecture.MetaArchitecture import MetaArchitecture  # Assume this module is available


# Initialize MetaArchitecture and runtime instances
meta = MetaArchitecture()
rt = runtime(meta)


class StartComponentResource:
    """Falcon resource to start a component based on type and component ID."""

    def on_post(self, req, resp):
        """
        Handle POST request to start a component.

        Expects JSON body with:
            - type: The type of the component
            - component_id: The identifier of the component

        Returns:
            JSON with status and result of the start operation.
        """
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        component = data.get('component_id')

        try:
            result = rt.start(type_, component)
            resp.media = {'status': 'created', 'result': result}
        except Exception:
            resp.media = {'status': 'error in call', 'result': False}


class CreateComponentResource:
    """Falcon resource to create a new component."""

    def on_post(self, req, resp):
        """
        Handle POST request to create a new component.

        Expects JSON body with:
            - type: The type of the component
            - module: The module name containing the component
            - component: The name/id of the component
            - secure: Boolean indicating if the component should be secure

        Returns:
            JSON with status and the URL or identifier of the created component.
        """
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        module = data.get('module')
        component = data.get('component')
        secure = data.get('secure')

        result = rt.create(type_, module, component, secure)
        url_ret = meta.getComponentAttributeValue(component, "Host")
        if url_ret is None:
            url_ret = component
        
        resp.media = {'status': 'created', 'result': url_ret}
        print(url_ret)


class DeleteComponentResource:
    """Falcon resource to delete a component."""

    def on_post(self, req, resp):
        """
        Handle POST request to delete a component.

        Expects JSON body with:
            - type: The type of the component
            - component_id: The identifier of the component to delete

        Returns:
            JSON with status and result of the delete operation.
        """
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        component_id = data.get('component_id')

        result = rt.delete(type_, component_id)
        resp.media = {'status': 'deleted', 'result': result}


class ConnectResource:
    """Falcon resource to connect components/interfaces."""

    def on_post(self, req, resp):
        """
        Handle POST request to connect components.

        Expects JSON body with:
            - type: The type of the connection
            - component_src: Source component ID
            - component_intf: Interface name or ID on the component
            - intf_type: Type of interface

        Returns:
            JSON with status and result of the connect operation.
        """
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        src = data.get('component_src')
        intf = data.get('component_intf')
        intf_type = data.get('intf_type')

        result = rt.connect(type_, src, intf, intf_type)
        resp.media = {'status': 'connected', 'result': result}


class DisconnectResource:
    """Falcon resource to disconnect components/interfaces."""

    def on_post(self, req, resp):
        """
        Handle POST request to disconnect components.

        Expects JSON body with:
            - type: The type of the disconnection
            - component_src: Source component ID
            - component_intf: Interface name or ID on the component
            - intf_type: Type of interface

        Returns:
            JSON with status and result of the disconnect operation.
        """
        data = json.load(req.bounded_stream)
        type_ = data.get('type')
        src = data.get('component_src')
        intf = data.get('component_intf')
        intf_type = data.get('intf_type')

        result = rt.disconnect(type_, src, intf, intf_type)
        resp.media = {'status': 'disconnected', 'result': result}
