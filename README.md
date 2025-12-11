# 💰 AI Expense Guardian: Real-time Receipt Audit and Risk Prediction

## Project Overview
The AI Expense Guardian is a modern, responsive web application built with Streamlit and deployed using Docker and OpenShift. It demonstrates a powerful financial process automation workflow: leveraging a simulated AI model to perform Optical Character Recognition (OCR) on expense receipts, categorize the spending, and immediately assign a Risk Score based on predefined corporate policies and anomaly detection.

This tool significantly accelerates the expense approval process by automatically flagging high-risk or policy-violating expenses, providing instant **Auto-Approve** or **Auto-Reject** recommendations. The application also features a Coaching section with aggregate analysis and budget forecasting.

## 🚀 Features
- **Real-time Receipt Upload**: Users can upload JPG or PNG receipt images.
- **AI Analysis**: Extracts data (Vendor, Amount, Category) and calculates a dynamic Risk Score (0-100).
- **Dynamic Risk Scoring**: Flag expenses based on amount thresholds (e.g., > $1000) and suspicious vendor types.
- **Styled Risk Summary**: Visually distinct card displaying the final approval recommendation.
- **Coaching & Budget Forecasting**: Aggregated financial advice and predicted monthly spend.
- **Containerization**: Includes `Dockerfile` for deployment in environments like OpenShift or Render.

## 📦 Project Structure
```
├── app.py                      # Main Streamlit application, UI, and business logic
├── .streamlit/                 # Directory containing Streamlit configuration files
│   └── config.toml             # Configuration for OpenShift (disables XSRF protection)
├── Dockerfile                  # Defines the non-root, production-ready container image
├── docker-compose.yml          # Local environment setup for quick development
├── k8s_deployment.yaml         # Kubernetes/OpenShift Deployment, Service, and Route
├── requirements.txt            # Python dependencies (Streamlit, pandas, pytest)
├── test_app.py                 # Unit tests for core business logic (risk flagging)
└── README.md                   # This file
```

## 🚀 Deployment (Streamlit Cloud)

This app is optimized for **Streamlit Cloud**. Follow these steps to deploy:

1.  **Push to GitHub**: Ensure this code is in a public or private GitHub repository.
2.  **Sign Up/Login**: Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3.  **Deploy App**:
    *   Click **"New app"**.
    *   Select your repository (`Eye-Spend`), branch (`main`), and main file path (`app.py`).
    *   Click **"Deploy!"**.
4.  **Configure Secrets (CRITICAL)**:
    *   Once the app is deploying/live, click the "Manage app" button (bottom right) or "Settings" (three dots > Settings).
    *   Go to the **"Secrets"** section.
    *   Add your API key in the following format:
        ```toml
        GEMINI_API_KEY = "your-google-gemini-api-key-here"
        ```
    *   Save. The app will reboot and connect to the AI model.

---

## 🛠️ Local Development

The easiest way to run the application locally is using pip or Docker.

### Option 1: Python (Pip)
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Option 2: Docker Compose
```bash
docker-compose up --build
```
Access the app at: `http://localhost:8501`

## ☁️ OpenShift Deployment (Alternative)
This application is configured for secure deployment on OpenShift.

1.  **Build & Push Image**:
    ```bash
    docker build -t your-registry.io/your-namespace/expense-app:latest .
    docker push your-registry.io/your-namespace/expense-app:latest
    ```
2.  **Configure Secrets**:
    ```bash
    kubectl create secret generic app-secrets \
      --from-literal=api-key=*** \
      --namespace=redkom-dev
    ```
3.  **Apply Manifest**:
    Update `k8s_deployment.yaml` with your image URL and apply:
    ```bash
    oc apply -f k8s_deployment.yaml
    ```

## 🧪 Testing
Run unit tests locally:
```bash
pytest
```
