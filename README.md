# Vault Nest

Secure, Private Cloud Storage over Tor

---

## Overview

Vault Nest is a privacy-focused cloud storage application built with Flutter and Flask. It enables users to securely upload, download, and manage files through the Tor network, providing a private alternative to traditional cloud storage services.

> **Note:** This project is currently intended for demonstration and educational purposes.

---

## Features

- Secure user authentication
- Email verification
- File upload and download
- File deletion
- Account deletion
- User storage quota
- Tor (.onion) connectivity
- Flutter Android client
- Flask backend
- Privacy-focused architecture

---

## Tech Stack

### Frontend

- Flutter
- Dart
- Android WebView
- Kotlin

### Backend

- Flask
- SQLAlchemy
- PostgreSQL / SQLite
- Flask-Login
- Flask-Mail

### Networking

- Tor
- SOCKS5 Proxy
- NanoHTTPD

---

## Project Structure

```text
VaultNest/
│
├── flutter_app/
│   ├── lib/
│   ├── android/
│   └── ...
│
├── flask_backend/
│   ├── app.py
│   ├── templates/
│   ├── static/
│   ├── models.py
│   └── ...
│
└── README.md
```

---

## Getting Started

### Clone the repository

```bash
git clone https://github.com/tasib-dev/vault-nest.git
cd vault-nest
```

### Backend

```bash
cd flask_backend
pip install -r requirements.txt
python app.py
```

### Flutter

```bash
cd flutter_app
flutter pub get
flutter run
```

---

## Security

Vault Nest is designed with privacy in mind and includes:

- Secure user authentication
- Password hashing
- Tor-based communication
- Session management
- Private file storage

---

## Android Application

The Android application automatically establishes a Tor connection before accessing the server, allowing users to interact with the hidden service without requiring a separate Tor browser.

---

## Disclaimer

Vault Nest is an educational project and has not been professionally security audited. It should not be used to store highly sensitive or mission-critical data without additional security review.

---

## Contributing

Contributions are welcome. Feel free to fork the repository, create a new branch, and submit a pull request.

---

## License

This project is licensed under the MIT License.

---

## Developer

**Abdullah Khabbab Tasib**

Software Engineering Student  
University of Dhaka

GitHub: https://github.com/tasib-dev

---

## Support

If you find this project useful, consider starring the repository on GitHub.
