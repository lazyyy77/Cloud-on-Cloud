class CorsMiddleware(object):
    """中间件：跨域访问"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # process_template_response(), process_response() 只能二选一、根据view的response类型，重载相应方法。
    def process_template_response(self, request, response):
        # 如果view 使用了render渲染response，使用这个中间件
        response["Access-Control-Allow-Origin"] = "*"
        return response

    def process_response(self, request, response):
        # 如果view使用HttpResponse, 将使用这个中间件
        response["Access-Control-Allow-Origin"] = "*"
        return response
