# Setting Up InsightForge

Getting InsightForge running on your local machine is quick and easy.

> **Note**: This repository is a fork. The original upstream repository can be found here: [m-kavana2005/InsightForge-Autonomous-data-analysis-system](https://github.com/m-kavana2005/InsightForge-Autonomous-data-analysis-system)

---

## 1. Prerequisites
You need to have **Python 3.10** (or higher) installed on your system.

## 2. Installation

Open your terminal or command prompt and run these commands:

```bash
# Clone this repository (if you haven't already)
git clone https://github.com/mohitkgupta13/InsightForge-Autonomous-data-analysis-system.git
cd InsightForge-Autonomous-data-analysis-system

# Navigate into the backend folder
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

## 3. Running the App

To start the application, simply run the backend server:

```bash
# Make sure you are inside the 'backend' folder
python app.py
```

## 4. Open in Browser

Once the server says `[InsightForge] Open http://127.0.0.1:5000 in your browser`, open your web browser and go to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

You are now ready to upload datasets and generate insights!
