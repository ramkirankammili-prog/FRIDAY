from fastapi import Request
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import random
from datetime import datetime

from intelligence import analyze_incident


app = FastAPI(
    title="FRIDAY",
    description="AI Incident Intelligence Platform"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


connected_clients = []

incidents = []


services = [
    "api-gateway",
    "order-service",
    "payment-service",
    "database"
]


# --------------------------------------------------
# NORMAL LOG GENERATOR
# --------------------------------------------------

def create_normal_log():

    service = random.choice(services)

    messages = [
        "Request completed successfully",
        "Health check OK",
        "Request processed",
        "Database query completed",
        "Service operating normally"
    ]

    return {

        "timestamp":
            datetime.now().strftime("%H:%M:%S"),

        "service":
            service,

        "level":
            "INFO",

        "event_type":
            "NORMAL",

        "message":
            random.choice(messages)
    }


# --------------------------------------------------
# INCIDENT LOG GENERATOR
# --------------------------------------------------

def create_incident_logs():

    now = datetime.now().strftime("%H:%M:%S")


    return [

        {
            "timestamp": now,
            "service": "database",
            "level": "ERROR",
            "event_type": "DB_LATENCY",
            "message":
                "Database latency increased to 2400ms"
        },


        {
            "timestamp": now,
            "service": "database",
            "level": "ERROR",
            "event_type": "CONNECTION_POOL",
            "message":
                "Database connection pool reached 95%"
        },


        {
            "timestamp": now,
            "service": "order-service",
            "level": "ERROR",
            "event_type": "DB_TIMEOUT",
            "message":
                "Database connection timeout"
        },


        {
            "timestamp": now,
            "service": "order-service",
            "level": "ERROR",
            "event_type": "ORDER_FAILURE",
            "message":
                "Order creation failed"
        },


        {
            "timestamp": now,
            "service": "payment-service",
            "level": "ERROR",
            "event_type": "PAYMENT_TIMEOUT",
            "message":
                "Payment request timed out"
        },


        {
            "timestamp": now,
            "service": "api-gateway",
            "level": "ERROR",
            "event_type": "HTTP_500",
            "message":
                "HTTP 500 - Checkout request failed"
        }

    ]


# --------------------------------------------------
# WEBSOCKET BROADCAST
# --------------------------------------------------

async def broadcast(data):

    disconnected = []


    for client in connected_clients:

        try:

            await client.send_json(data)

        except:

            disconnected.append(client)


    for client in disconnected:

        if client in connected_clients:

            connected_clients.remove(client)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {

        "name": "FRIDAY",

        "status": "running",

        "message":
            "FRIDAY AI Incident Intelligence Platform"

    }


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():

    return {

        "status": "healthy",

        "services": len(services)

    }


# --------------------------------------------------
# INCIDENT API
# --------------------------------------------------

@app.get("/incidents")
def get_incidents():

    return incidents


# --------------------------------------------------
# WEBSOCKET
# --------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await websocket.accept()

    connected_clients.append(websocket)


    try:

        while True:

            await asyncio.sleep(4)


            # --------------------------------------
            # NORMAL SYSTEM
            # --------------------------------------

            if random.random() > 0.30:

                log = create_normal_log()

                await broadcast({

                    "type":
                        "log",

                    "data":
                        log

                })


            # --------------------------------------
            # INCIDENT
            # --------------------------------------

            else:

                logs = create_incident_logs()


                # Send events one by one

                for log in logs:

                    await broadcast({

                        "type":
                            "log",

                        "data":
                            log

                    })

                    await asyncio.sleep(0.7)


                # ----------------------------------
                # ANALYZE EVENTS
                # ----------------------------------

                analysis = analyze_incident(
                    logs
                )


                # ----------------------------------
                # CREATE INCIDENT
                # ----------------------------------

                incident = {

                    "id":
                        len(incidents) + 1,

                    "status":
                        "ACTIVE",

                    "severity":
                        "CRITICAL",

                    "root_cause":
                        analysis["root_cause"],

                    "confidence":
                        analysis["confidence"],

                    "evidence":
                        analysis["evidence"],

                    "timeline":
                        logs,

                    "analyzed_at":
                        analysis["analyzed_at"]

                }


                incidents.append(
                    incident
                )


                # ----------------------------------
                # SEND INCIDENT TO FRONTEND
                # ----------------------------------

                await broadcast({

                    "type":
                        "incident",

                    "data":
                        incident

                })


    except Exception:

        if websocket in connected_clients:

            connected_clients.remove(
                websocket
            )
@app.post("/otlp/v1/traces")
async def receive_otlp_traces(request: Request):
    data = await request.body()

    print("🔥 FRIDAY received OpenTelemetry data:", len(data), "bytes")

    return {"status": "received"}