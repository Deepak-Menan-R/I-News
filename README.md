# I-News: Personalized News Aggregator

I-News is a **personalized news aggregator** that curates news articles based on user preferences, including **categories** and **location**. The application is built with **React (Frontend)** and **Flask (Backend)**, integrating **NewsAPI** to fetch relevant news articles. Additionally, it features **email notifications**, **translation**, and **text-to-speech** for an enhanced user experience.

## Features
- **User Preferences**: Get news based on selected categories and location.
- **NewsAPI Integration**: Fetch real-time news articles.
- **Email Alerts**: Receive updates if inactive for over an hour.
- **Translation Support**: Read news in multiple languages.
- **Text-to-Speech**: Listen to articles instead of reading.

## Tech Stack
- **Frontend**: React.js, Tailwind CSS
- **Backend**: Flask, SQLite
- **APIs Used**: NewsAPI
- **Authentication**: JWT-based authentication

## Project Structure
```
I-News/
│── frontend/   # React application
│── backend/    # Flask API
│── .gitignore  # Ignore unnecessary files
│── README.md   # Documentation
```

## Installation & Setup
### Prerequisites
- Node.js & npm (for React)
- Python & pip (for Flask)

### Backend (Flask API)
```sh
cd backend
python -m venv venv  # Create virtual environment
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate  # On Windows
pip install -r requirements.txt  # Install dependencies
python app.py  # Run Flask server
```

### Frontend (React App)
```sh
cd frontend
npm install  # Install dependencies
npm start  # Run React app
```

## API Configuration
1. Get a free API key from [NewsAPI](https://newsapi.org/).
2. Create a `.env` file in the `backend` folder and add:
   ```
   NEWS_API_KEY=your_api_key_here
   ```

## Usage
- Sign up and set preferences.
- Get personalized news updates.
- Use translation and text-to-speech features.
- Stay updated with email alerts.

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit changes (`git commit -m "Added new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a Pull Request.

## License
This project is licensed under the MIT License.

