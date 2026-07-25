# Vault Nest

<p align="center">
  <b>Secure, Private Cloud Storage over Tor</b><br>
  A privacy-focused cloud storage application built with Flutter and Flask.
</p>

---

## 📖 Overview

Vault Nest is a secure cloud storage platform that allows users to upload, download, and manage files through the Tor network. It consists of a Flutter Android application and a Flask backend, providing end-to-end privacy without relying on traditional cloud providers.

> **Note:** This project is currently a demonstration/prototype and is limited to a small number of users.

---

## ✨ Features

- 🔒 Secure user authentication
- 📧 Email verification
- 📂 Upload and download files
- 🗑️ Delete files
- 👤 Delete account
- 📊 User storage quota
- 🧅 Tor (.onion) connectivity
- 📱 Flutter Android client
- 🌐 Flask backend
- 🔐 Privacy-first architecture

---

## 🏗️ Tech Stack

### Frontend
- Flutter
- Dart
- Android WebView
- Kotlin (Native Android)

### Backend
- Flask
- SQLAlchemy
- PostgreSQL / SQLite (Development)
- Flask-Login
- Flask-Mail

### Networking
- Tor
- SOCKS5 Proxy
- NanoHTTPD

---

## 📂 Project Structure

```
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

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/your-username/vault-nest.git
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

## 🔒 Security

Vault Nest is designed with privacy as a priority.

- User authentication
- Password hashing
- Tor network communication
- Private file storage
- Session management

---

## 📱 Android

The Android application automatically connects through Tor before accessing the server.

---

## ⚠️ Disclaimer

This project is intended for educational and demonstration purposes.

While security best practices have been followed where possible, Vault Nest has **not** undergone a professional security audit. Do not use it to store highly sensitive or mission-critical data without performing your own security review.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

Feel free to fork the repository and submit a pull request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Developer

**Abdullah Khabbab Tasib**

Software Engineering Student  
University of Dhaka

GitHub: https://github.com/tasib-dev

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub!
