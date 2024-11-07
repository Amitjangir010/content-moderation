# 🛡️ Content Moderation System

This project is a Content Moderation System that uses machine learning models to analyze text and images for harmful content. It provides a web interface for real-time moderation and an analytics dashboard to view moderation statistics.

## 📂 Project Structure

- **`app.py`**: The main Streamlit application file that provides the user interface for content moderation and analytics.
- **`src/database/db.py`**: Contains the database setup using SQLAlchemy for logging moderation results.
- **`src/models/text_classifier.py`**: Implements the `TextModerator` class for analyzing text content using a pre-trained transformer model.
- **`src/models/image_classifier.py`**: Implements the `ImageModerator` class for analyzing image content using a pre-trained transformer model.
- **`requirements.txt`**: Lists all the Python dependencies required to run the project.

## ✨ Features

- **📝 Text Moderation**: Analyzes text input to determine if it is toxic or safe.
- **🖼️ Image Moderation**: Analyzes uploaded images to determine if they are NSFW (Not Safe For Work) or safe.
- **📊 Analytics Dashboard**: Provides insights into moderation activities, including key metrics and visualizations.

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Amitjangir010/content-moderation.git
   cd content-moderation
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Usage

1. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to `http://localhost:8501` to access the application.

## 🗄️ Database

The application uses SQLite to store moderation logs. The database file is named `moderation.db` and is located in the project root directory.

## 🤖 Models

- **Text Model**: Uses the `unitary/toxic-bert` model for text classification.
- **Image Model**: Uses the `Falconsai/nsfw_image_detection` model for image classification.

They will be downloaded automatically when the application is running
