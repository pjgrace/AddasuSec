"""
Role-Based Access Control Decorators for Falcon Resources

This module provides decorators to enforce role-based access control
on Falcon API resource methods. It supports extracting user roles from
the Falcon request context or JWT tokens, and enables both method-level
and class-level protection.

Decorators:
- require_role: Restricts access to users with one or more allowed roles.
- role_required: Restricts access to users with a specific role, supports
  Falcon requests or raw JWT tokens.
- protect_component_with_role: Applies role_required to all callable methods
  in a class for class-wide role enforcement.

Dependencies:
- Falcon framework
- Custom JWT decode utility (Runtimes.Auth.JWTUtils.decode_token)

Author: Paul Grace
"""

import falcon
from functools import wraps
from fastapi import HTTPException, status  # Not used, consider removing
from falcon import HTTPUnauthorized, HTTPForbidden
from Runtimes.Auth.JWTUtils import decode_token

def require_role(*allowed_roles):
    """
    Decorator to restrict Falcon resource method access based on user roles.
    
    Args:
        allowed_roles (str): One or more roles allowed to access the method.
    
    Raises:
        HTTPUnauthorized: If user is not authenticated.
        HTTPForbidden: If user's role is not allowed.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, req, resp, *args, **kwargs):
            # Get user info from Falcon request context
            user = getattr(req.context, "user_id", None)
            if user is None:
                raise falcon.HTTPUnauthorized(description="Authentication required")
            if user.get("role") not in allowed_roles:
                raise falcon.HTTPForbidden(description=f"Access denied for role: {user.get('role')}")
            return func(self, req, resp, *args, **kwargs)
        return wrapper
    return decorator


def role_required(required_role):
    """
    Decorator to protect resource methods based on a single required role.
    Supports both Falcon Request objects and raw JWT tokens.
    
    Args:
        required_role (str): The required user role to access the method.
    
    Raises:
        HTTPUnauthorized: If authentication fails or user not present.
        HTTPForbidden: If user's role does not match required_role.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, req, *args, **kwargs):
            print(f"[DEBUG] Entered wrapper of {func.__qualname__}")

            if isinstance(req, falcon.Request):
                # Falcon request path: user stored in req.context.user
                user = getattr(req.context, "user", None)
                print(f"user is {user}")
                if not user:
                    raise HTTPUnauthorized(description="Authentication required")
                if user.get("role") != required_role:
                    raise HTTPForbidden(description=f"{required_role} role required")
                return func(self, *args, **kwargs)

            else:
                # Non-Falcon request assumed to be a JWT token
                try:
                    payload = decode_token(req)  # JWT decode
                except Exception as e:
                    raise HTTPUnauthorized(description=str(e), challenges=["Bearer"])
                if payload.get("role") != required_role:
                    raise HTTPForbidden(description=f"{required_role} role required")
                return func(self, *args, **kwargs)

        return wrapper
    return decorator


def protect_component_with_role(required_role):
    """
    Class decorator to apply role_required decorator to all callable
    methods of a class, enforcing role-based protection.
    
    Args:
        required_role (str): The role required to access any method of the class.
    
    Returns:
        The decorated class with all callable methods wrapped.
    """
    def class_decorator(cls):
        method_decorator = role_required(required_role)
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                # Skip dunder methods
                continue
            attr = getattr(cls, attr_name)
            if callable(attr):
                # Wrap callable methods with role_required
                setattr(cls, attr_name, method_decorator(attr))
        return cls
    return class_decorator
