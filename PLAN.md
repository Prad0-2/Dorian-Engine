Parallel Universe Habit Tracker – MVP Build & GCP Integration Instructions
For Gemini Cloud CLI

This document contains all instructions required for Gemini CLI to build and deploy the MVP version of the Parallel Universe Habit Tracker app (Streamlit + Python backend), including all missing features, all GCP integrations, and all required components.

1. MVP Product Requirements

Gemini CLI must implement the following features so the app functions end-to-end and demonstrates the core value of the product.

1.1 User Onboarding
Features Required

Firebase Authentication (email/password login)

User provides:

Full name

Primary goal (e.g., weight, job, fitness, habits)

Target date

User uploads a selfie

Create user document in Firestore under /users/{userId}

Trigger initial future-self avatar generation

Firestore Fields (User Document)
users/{userId}:
  name
  email
  createdAt
  mainGoal
  targetDate
  currentAvatarUrl
  latestDriftScore

1.2 Initial Future-Self Avatar Generation
Requirements

Use Vertex AI (Imagen or Gemini Image) to generate a visual representation of the user’s future self based on:

User selfie

User goal

User timeline

Save the generated image to Cloud Storage

Save the image URL to Firestore under currentAvatarUrl

Storage Path
gs://<bucket>/avatars/{userId}/initial.png

1.3 Daily Habit Check-In
Requirements

User taps “Completed” or “Not Completed”

Save the result in Firestore under:

users/{userId}/habits/{YYYY-MM-DD}


Recalculate drift score

Trigger avatar update (only if needed)

Habit Document Fields
completed: true/false
timestamp

1.4 Drift Score Calculation
MVP Logic

+2 for each completed day

–4 for each missed day

–5 extra penalty if user misses 3+ consecutive days

Score must be clamped between 0 and 100

Firestore Update
users/{userId}/latestDriftScore

1.5 Avatar Update Engine (Basic Version)
Requirements

If drift score increases → generate a slightly improved avatar

If drift score decreases → generate a slightly degraded avatar

Use Vertex AI for generation

Save updated version to Storage

Save URL under:

users/{userId}/avatars/{avatarId}

1.6 Main Dashboard
UI Must Display

Current avatar

Drift score

Consistency percentage

Today’s check-in buttons

Weekly summary

Avatar “before vs after” comparison slider

1.7 Weekly Progress Summary
Requirements

Compute last 7 days consistency

Calculate drift score change

Generate weekly avatar snapshot (optional)

Save report to:

users/{userId}/weekly_reports/{reportId}

2. Required GCP Integrations

Gemini CLI must implement or verify the following integrations.

2.1 Firestore Schema Setup

Collections required:

/users
/users/{userId}/habits
/users/{userId}/avatars
/users/{userId}/weekly_reports

2.2 Secret Manager Integration

Secrets to store securely:

Firebase Admin SDK credentials

Vertex AI API keys

Service account JSON

Storage bucket config

Secrets must be mounted in Cloud Run.

2.3 Cloud Run Deployment

Ensure:

App builds via Cloud Build

App deploys successfully

All dependencies (firebase-admin, vertexai, google-cloud-storage, firestore) work

Environment variables load correctly

Secret Manager integration works

2.4 Firebase Authentication

Integrate Firebase Auth for:

Email/password login

Token verification in backend

Mapping userId to Firestore

2.5 Cloud Scheduler Jobs

Create two scheduled tasks:

1. Weekly Drift Recalculation

Trigger Cloud Run endpoint:

/tasks/weekly_update

2. Weekly Report Generator

Trigger endpoint:

/tasks/weekly_summary


Schedules:

Every Sunday, 7 AM UTC (or region equivalent)

2.6 Logging & Error Handling

Gemini CLI must implement:

Cloud Logging

Cloud Monitoring

Error handling for:

Firestore errors

Image generation failures

Storage upload failures

Vertex API timeouts

3. Required Code Additions

Gemini CLI must modify or create the following files:

Backend Files

logic.py

Initial avatar generation

Drift score logic

Avatar regeneration logic

db.py

Firestore read/write methods

Habit logs

Weekly reports

Avatar URLs

tasks.py

Weekly drift update job

Weekly summary generator

auth.py

Firebase token verification

Frontend (Streamlit)

app.py

Routing

Navigation

Authentication gatekeeping

ui_onboarding.py

Signup + goal input + selfie upload

ui_dashboard.py

Avatar display

Drift score

Habit check-in

ui_weekly_report.py

Show weekly summaries

Infrastructure Files

cloudbuild.yaml

Must include new files

Must enable Secret Manager access

Commands to create:

Cloud Scheduler jobs

Secret Manager entries

IAM permissions

4. End-to-End Acceptance Criteria

The MVP is complete when:

User can log in

User can upload selfie

User sets a goal

Initial avatar is generated and stored

User logs daily habits

Drift score updates correctly

Avatar updates reflect drift

Weekly summary is generated

Dashboard functions properly

App is fully deployed on Cloud Run

Firestore + Storage + Vertex AI all work with live users

No fatal errors occur during normal sessions

5. Execution Instruction for Gemini CLI

Gemini CLI must:

Read this document

Generate missing code

Patch existing code

Create required GCP integrations

Redeploy via Cloud Build → Cloud Run

Run validation checks

Output a summary of work completed