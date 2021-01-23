import json

from marshmallow import ValidationError
from nameko import config
from nameko.exceptions import BadRequest
from nameko.rpc import RpcProxy
from werkzeug import Response

from gateway.entrypoints import http
from gateway.exceptions import OrderNotFound, ProductNotFound


class GatewayService(object):
    """
    Service acts as a gateway to other services over http.
    """

    name = 'gateway'

    model1_rpc = RpcProxy('model1')

    @http(
        "GET", "/model1",
        expected_exceptions=ProductNotFound
    )
    def get_model1(self, request):
        """Gets product by `product_id`
        """
        product = self.model1_rpc.get_model1()
        return Response(
            product,
            mimetype='application/json'
        )