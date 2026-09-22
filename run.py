#!/usr/bin/env python3
"""
AquaGuard ML - Application Launcher
Launches the FastAPI backend and serves the React dashboard single-page application.
"""
import sys
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("  AquaGuard ML | Water Potability Triage & Early Warning System")
    print("  Production Engine v2.4.0 (FastAPI + React/Tailwind/ReactBits)")
    print("  Serving Application at: http://localhost:8000")
    print("  Interactive Swagger Docs: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
