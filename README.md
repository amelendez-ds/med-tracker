# 💊 Med Tracker API

A cloud-native microservice designed to track medication inventory and automate multi-channel low-stock alerts. Built with FastAPI and hosted on Render.

## 🚀 Features

* **Headless REST API:** Fully functional CRUD operations for tracking medications, dosages, and daily consumption.
* **Proactive Alerts:** Automated logic calculates `days_remaining` based on current stock and daily dosage.
* **Daily Automation:** A secure, token-protected `/daily-automation/` endpoint triggered by a cloud-native Cron Job.
* **Multi-Channel Notifications:** Alerts are broadcasted via email (using the Resend HTTP API) and push notifications (via Discord Webhooks) when stock falls below the 14-day threshold.
* **Serverless Database:** Data is persisted using Neon PostgreSQL.

## 🛠️ Tech Stack

* **Backend:** Python 3.12+, FastAPI, Pydantic
* **Database:** SQLModel (ORM), Neon Serverless PostgreSQL
* **Notifications:** Resend API (Email), Discord Webhooks (Push)
* **Package Management:** `uv`
* **Containerization:** Docker
* **Hosting:** Render (Web Service + Cron Job)

## 💻 Local Development Setup

To run this project locally, you will need to set up your environment variables and install the dependencies using `uv`.

## ☁️ Cloud Architecture
This project is deployed on **Render** using a dual-service architecture:

1. Web Service (Docker): Runs the FastAPI application and connects to the Neon PostgreSQL database.
2. Cron Job (Docker): A lightweight worker that wakes up daily. It executes trigger.py, which sends an authorized POST request to the Web Service to automatically deduct pills, calculate stock, and dispatch HTTP alerts to **Resend** and **Discord**.

## 🚦 Key API Endpoints

- GET /medications/ - List all tracked medications.
- POST /medications/ - Add a new medication to track.
- PUT /medications/{med_id}/take - Subtract the daily dosage from the current pill count manually.
- PUT /medications/{med_id}/refill - Add new pills to the total inventory.
- GET /check-stock - Manually trigger the threshold math and alert logic.
- POST /daily-automation/ - Secured endpoint used by the Cron Job to automate the daily check.
