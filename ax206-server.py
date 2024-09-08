from ax206lib import send_base64_image, set_brightness_byval, CURRENT_BRIGHTNESS
import argparse

## Server ##
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='AX206 Image Server', description='Send 480x320 iamges to the AX206 LCD screen')

upload_model = api.model('UploadImage', {
    'image': fields.String(required=True, description='Base64 encoded image in JPG, PNG formats')
})

# Define the model for brightness control
brightness_model = api.model('Brightness', {
    'brightness': fields.Integer(required=True, description='Brightness level (0-7)', min=0, max=7)
})

@api.route('/upload')
class UploadImage(Resource):
    @api.expect(upload_model)
    @api.response(200, 'Image successfully sent to the AX206 LCD screen')
    @api.response(400, 'Missing image data or invalid image data sent (too large for example)')
    @api.response(500, 'This api must be run as root, otherwise exceptions may occur, check and ensure the LCD screen is recognized')
    def post(self):
        """Upload an image in base64 format"""
        data = request.json

        if 'image' not in data:
            return jsonify({'error': 'No image data found'}), 400

        try:
            image_data = data['image']
            send_base64_image(image_data)
            return {'message': 'Success'}, 200
        except Exception as e:
            return {'message': str(e)}, 500

@api.route('/brightness')
class BrightnessControl(Resource):
    @api.expect(brightness_model)
    def post(self):
        """Set the brightness level of the LCD screen"""
        data = request.json
        brightness = data.get('brightness')

        if brightness is None:
            return {'message': 'Brightness level is required'}, 400

        if not (0 <= brightness <= 7):
            return {'message': 'Brightness level must be between 0 and 7'}, 400

        CURRENT_BRIGHTNESS = brightness

        try:
            set_brightness_byval(brightness)
            return {'message': f'Brightness set to {brightness}'}, 200
        except Exception as e:
            return {'message': str(e)}, 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the AX206 LCD API")
    parser.add_argument('--port', type=int, default=5000, help='Port number for the API to run on, default is 5000')
    args = parser.parse_args()
    app.run(debug=True, port = args.port)
