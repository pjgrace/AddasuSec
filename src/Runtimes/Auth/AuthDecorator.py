import falcon
from functools import wraps
from fastapi import HTTPException, status
from falcon import HTTPUnauthorized, HTTPForbidden
from Runtimes.Auth.JWTUtils import decode_token

def require_role(*allowed_roles):
    """
    Decorator to restrict access based on user roles from req.context.user
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, req, resp, *args, **kwargs):
            user = getattr(req.context, "user_id", None)
            if user is None:
                raise falcon.HTTPUnauthorized(description="Authentication required")
            if user.get("role") not in allowed_roles:
                raise falcon.HTTPForbidden(description=f"Access denied for role: {user.get('role')}")
            return func(self, req, resp, *args, **kwargs)
        return wrapper
    return decorator


def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(self, req, *args, **kwargs):
            if isinstance(req, falcon.Request):
                user = getattr(req.context, "user", None)
                if not user:
                    raise HTTPUnauthorized(description="Authentication required")
                if user.get("role") != required_role:
                    raise HTTPForbidden(description=f"{required_role} role required")
                return func(self, *args, **kwargs)
            else:
                try:
                    payload = decode_token(req)  # Your JWT decode function
                except Exception as e:
                    raise HTTPUnauthorized(description=str(e), challenges=["Bearer"])
                if payload.get("role") != required_role:
                    raise HTTPForbidden(description=f"{required_role} role required")
                return func(self, *args, **kwargs)
                
        return wrapper
    return decorator


def protect_component_with_role(required_role):
    def class_decorator(cls):
        method_decorator = role_required(required_role)
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                continue
            attr = getattr(cls, attr_name)
            if callable(attr):
                setattr(cls, attr_name, method_decorator(attr))
        return cls
    return class_decorator