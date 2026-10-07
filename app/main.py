"""Flask web API that exposes the calculator over HTTP."""

import hmac
import os
import platform
import socket

from flask import Flask, jsonify, request

from app import __version__
from app.calculator import OPERATIONS, calculate


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        return jsonify(
            app="s16-calculator-api",
            version=__version__,
            git_sha=os.environ.get("GIT_SHA", "local"),
            hostname=socket.gethostname(),
            python=platform.python_version(),
            endpoints=["/health", "/api/<operation>?a=<n>&b=<n>", "/api/secure/ping"],
            operations=sorted(OPERATIONS),
        )

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/<operation>")
    def api_calculate(operation):
        try:
            a = float(request.args["a"])
            b = float(request.args["b"])
        except KeyError:
            return jsonify(error="query parameters 'a' and 'b' are required"), 400
        except ValueError:
            return jsonify(error="'a' and 'b' must be numbers"), 400

        try:
            result = calculate(operation, a, b)
        except KeyError:
            return jsonify(error=f"unknown operation '{operation}'",
                           operations=sorted(OPERATIONS)), 404
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        return jsonify(operation=operation, a=a, b=b, result=result)

    @app.get("/api/secure/ping")
    def secure_ping():
        """Needs the X-API-Key header to match the API_KEY env var.

        In CI the key comes from the GitHub repository secret DEMO_API_KEY.
        """
        expected = os.environ.get("API_KEY")
        if not expected:
            return jsonify(error="API_KEY is not configured on the server"), 503
        supplied = request.headers.get("X-API-Key", "")
        if not hmac.compare_digest(supplied, expected):
            return jsonify(error="invalid or missing X-API-Key"), 401
        return jsonify(status="authorized", message="secret-protected endpoint reached")

    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
