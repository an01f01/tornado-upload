import os
import asyncio
import tornado.httpserver
import tornado.options
import tornado.ioloop
import tornado.web
import tornado.wsgi

from tornado import gen, web, template


tornado.options.define('port', default='8888', help='REST API Port', type=int)

class BaseHandler(tornado.web.RequestHandler):
    """
    Base handler gonna to be used instead of RequestHandler
    """
    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.write('Error %s' % status_code)
        else:
            self.write('BOOM!')

class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    """
    Default handler gonna to be used in case of 404 error
    """
    pass

class StatusHandler(BaseHandler):
    async def get(self):
        self.set_status(200)
        self.write({'message': 'File upload REST API working as expected'})
        self.finish()
    
class UploadHandler(BaseHandler):
    async def get(self):
        return self.render('uploads.html')

class FileUploadHandler(BaseHandler):
    def post(self):
        # Retrieve file from the request
        fileinfo = self.request.files['file'][0] 
        filename = fileinfo['filename']
        content_type = fileinfo['content_type']
        file_body = fileinfo['body']

        # Saving file to directory
        output_file_path = os.path.join('uploads', filename)
        with open(output_file_path, 'wb') as output_file:
            output_file.write(file_body)

        self.set_status(200)
        self.write(f"File '{filename}' with content type '{content_type}' uploaded and saved.")
        self.finish()


def make_app():
    settings = dict(
        cookie_secret=str(os.urandom(45)),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        default_handler_class=ErrorHandler,
        default_handler_args=dict(status_code=404)
    )
    return tornado.web.Application([
            (r"/", StatusHandler),
            (r"/upload", UploadHandler),
            (r"/api", FileUploadHandler),
        ], **settings)

async def main():
    # Create the uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    print(f"🚀 Starting stats tornado server.......... http://localhost:{tornado.options.options.port}")
    app = make_app()
    app.listen(tornado.options.options.port)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
