
import falcon
from Runtimes.Auth.JWTUtils import decode_token

class JWTAuthMiddleware:
    def process_request(self, req, resp):
        # Expect token in Authorization header: Bearer <token>
        auth_header = req.get_header("Authorization")
        print(auth_header)
        if auth_header is None or not auth_header.startswith("Bearer "):
            raise falcon.HTTPUnauthorized(
                description="Missing or invalid Authorization header",
                challenges=["Bearer"],
            )

        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
        except Exception as e:
            raise falcon.HTTPUnauthorized(description=str(e), challenges=["Bearer"])

        # Attach user info to request context for later use
        req.context.user = {
            "user_id": payload["sub"],
            "role": payload["role"]
        }
        print(req.context.user)