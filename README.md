# Photo-share Application

A Flask-based photo sharing platform that allows users to create albums, upload photos/videos, and share them securely.

## Features

- User authentication system
- Album creation and management
- Photo and video upload support
- Nested folder structure
- Sharing capabilities
- MongoDB integration

## Technical Requirements

- Python 3.x
- Flask
- MongoDB
- PyMongo
- PyYAML
- Werkzeug

## Project Structure

- `/static/photoshare` - Stores uploaded files and album data
- `/templates` - HTML templates
- `main.py` - Core application logic
- `config.yaml` - Configuration file

## Supported File Types

- Images: PNG, JPG, JPEG, GIF
- Videos: MP4, WEBM, OGG

## Key Features Explained

### Album Management
- Create albums and nested folders
- Upload multiple files simultaneously
- Organize content hierarchically

### Sharing System
- Toggle sharing for albums
- Recursive sharing for nested folders
- Public access links for shared content

### Security
- Session-based authentication
- Password hashing
- Secure file handling
- Input sanitization

## API Endpoints

- `/login` - User authentication
- `/photoshare` - Main album view
- `/photoshare/<album_id>` - Individual album view
- `/photoshare/<album_id>/upload` - File upload endpoint
- `/photoshare/create` - Album creation
- `/photoshare/share/<album_id>` - Shared album access
- `/photoshare/toggle-share/<album_id>` - Toggle sharing status

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open-source and available for modification and use under the MIT license.

### MIT License

```
MIT License

Copyright (c) 2025 Ralph King

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
