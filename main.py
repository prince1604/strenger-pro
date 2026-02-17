from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import asyncio
import datetime
import logging
import os
import bcrypt
from jose import jwt
from database import get_db_connection, init_db, db_config
from passlib.context import CryptContext

# --- PRO-LEVEL LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("strenger_activity.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StrengerPro")
logger.info("=========================================")
logger.info("STRENGER PRO ENGINE STARTING...")
logger.info("=========================================")

# --- CONFIGURATION ---
SECRET_KEY = "ULTRA_SECURE_PRO_KEY_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 Hours

app = FastAPI(title="Strenger Pro API", version="2.0.0")

# --- PERFORMANCE & SECURITY MIDDLEWARE ---
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
from starlette.requests import Request

# 1. GZip Compression (Makes responses smaller & faster)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS (Security - Control who can access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change to your actual domain in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Trusted Host (Security - Prevent Host Header Attacks)
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["YOUR_DOMAIN.com", "*.koyeb.app", "localhost"])

# 4. Process Time Monitoring (Performance Tracking)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- STATIC FILES (Absolute Path) ---
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    # Fallback to creating it if missing
    os.makedirs(static_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- AUTH MODELS ---
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    gender: str
    avatar_type: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- SECURITY HELPERS ---
def get_password_hash(password: str):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"CRYPT ERROR: {e}")
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- THE "STRENGER PRO" AI BRAIN ---
import random

class AIStranger:
    def __init__(self):
        self.greetings = ["hey", "hi there", "hello", "asl?", "sup", "hows it going?"]
        self.responses = {
            "default": ["lol", "nvm", "chill", "cool", "oh nice", "same here", "wow", "interesting"],
            "asl": ["19 m uk", "20 f us", "18 m india", "22 f canada", "21 m aus"],
            "bored": ["yea same", "im bored too", "strenger is cool though", "u chat here often?"],
            "bye": ["gtg", "bye!", "see ya", "talk later"]
        }
    
    def get_reply(self, message: str):
        msg = message.lower()
        if "asl" in msg: return random.choice(self.responses["asl"])
        if "bored" in msg or "nothing" in msg: return random.choice(self.responses["bored"])
        if "bye" in msg or "gtg" in msg: return random.choice(self.responses["bye"])
        return random.choice(self.responses["default"])

bot_brain = AIStranger()

# --- WEB SERVER INIT ---
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("DATABASE SYNCHRONIZED SUCCESSFULLY.")
    logger.info("VERSION: 3.0 - ALL FIXES APPLIED (Check Deployment)")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"UI LOAD ERROR: {e}")
        return HTMLResponse(content="<h1>Critical UI Error. Check logs.</h1>", status_code=500)

# --- HEALTH CHECK ENDPOINT ---
@app.get("/health")
async def health_check():
    conn = get_db_connection()
    status = "online" if conn else "offline"
    
    # Get masked config for debugging
    config_debug = {k: v for k, v in db_config.items()}
    if config_debug.get("password"):
        config_debug["password"] = "*****" + config_debug["password"][-3:] if len(config_debug["password"]) > 3 else "***"
        
    from database import last_error
    response = {
        "status": status,
        "database_host": config_debug.get("host"),
        "last_db_error": last_error,
        "region": "EU" if "eu-central" in str(config_debug.get("host")) else "Unknown",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    if conn:
        conn.close()
    return response

# --- CORE BUSINESS LOGIC (REG/LOGIN) ---
@app.post("/register", response_model=Token)
async def register(user: UserRegister):
    logger.info(f"PROTOCOL-REG: {user.username} is requesting entry.")
    
    import re
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password too short (min 6 characters).")
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", user.email):
         raise HTTPException(status_code=400, detail="Invalid email format.")
    
    conn = get_db_connection()
    if not conn:
        from database import last_error
        err_msg = f"Database Error: {last_error}" if last_error else "Database Offline (Unknown Error)"
        logger.error(f"REG-FAIL-DB: {err_msg}")
        raise HTTPException(status_code=503, detail=err_msg)
    
    try:
        from db_helper import get_cursor, execute_insert
        cursor = get_cursor(conn, dict_cursor=False)
        hashed = get_password_hash(user.password)
        
        sql = "INSERT INTO users (username, email, password_hash, gender, avatar_type) VALUES (%s, %s, %s, %s, %s)"
        last_id = execute_insert(cursor, sql, (user.username, user.email, hashed, user.gender, user.avatar_type))
        conn.commit()
        
        logger.info(f"REG-SUCCESS: {user.username} granted ID {last_id}.")
        token = create_access_token(data={"sub": user.email, "id": last_id})
        return {"status": "success", "access_token": token, "token_type": "bearer"}
        
    except Exception as e:
        conn.rollback()
        logger.warning(f"REG-DENIED: {user.username} - {e}")
        if "Duplicate entry" in str(e) or "unique constraint" in str(e) or "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Identity already exists.")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")
    finally:
        cursor.close()
        conn.close()

@app.post("/login", response_model=Token)
async def login(credentials: dict):
    identity = credentials.get('email') or credentials.get('username')
    logger.info(f"PROTOCOL-AUTH: Auth request for {identity}")
    
    conn = get_db_connection()
    if not conn: 
        from database import last_error
        err_msg = f"Database Error: {last_error}" if last_error else "Database Offline"
        raise HTTPException(status_code=503, detail=err_msg)
    
    try:
        from db_helper import get_cursor
        cursor = get_cursor(conn, dict_cursor=True)
        
        cursor.execute("SELECT * FROM users WHERE email=%s OR username=%s", (identity, identity))
        user = cursor.fetchone()
        
        if not user or not verify_password(credentials.get('password'), user['password_hash']):
            logger.warning(f"AUTH-FAILED: Invalid credentials for {identity}")
            raise HTTPException(status_code=401, detail="Access Denied: Invalid Credentials")
            
        logger.info(f"AUTH-SUCCESS: {user['username']} session started.")
        token = create_access_token(data={"sub": user['email'], "id": user['id']})
        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")
    finally:
        cursor.close()
        conn.close()

# --- PRO-LEVEL REAL-TIME ARCHITECTURE ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except:
                self.disconnect(user_id)

    async def broadcast_active_users(self):
        conn = get_db_connection()
        if not conn: return
        from db_helper import get_cursor
        from math import radians, cos, sin, asin, sqrt

        def haversine(lon1, lat1, lon2, lat2):
            # Calculate distance in km
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            return 6371 * c

        cursor = get_cursor(conn, dict_cursor=True)
        try:
            # JOIN users to get username and gender for the map
            cursor.execute("""
                SELECT 
                    s.user_id, 
                    s.latitude as lat, 
                    s.longitude as lon,
                    u.username,
                    u.gender
                FROM active_sessions s
                JOIN users u ON s.user_id = u.id
            """)
            raw_users = cursor.fetchall()
            
            # Normalize to list of dicts
            all_users = []
            if raw_users:
                for u in raw_users:
                    if isinstance(u, dict):
                        d = u
                    else:
                        d = {"user_id": u[0], "lat": u[1], "lon": u[2], "username": u[3], "gender": u[4]}
                    
                    # Ensure floats
                    try:
                        d['lat'] = float(d['lat'])
                        d['lon'] = float(d['lon'])
                        all_users.append(d)
                    except: pass
            
            # Send personalized radius update to each connected user
            # Radius limit: 25 km (Snapchat style visibility)
            RADIUS_KM = 25.0

            for target_id in list(self.active_connections.keys()):
                # Find target user's location
                me = next((u for u in all_users if u['user_id'] == target_id), None)
                if not me: continue
                
                nearby_users = []
                for u in all_users:
                    # Always include self so map centers correctly if needed, or exclude. 
                    # Usually map shows self.
                    if u['user_id'] == target_id:
                        nearby_users.append({**u, "distance": 0, "is_me": True})
                        continue

                    dist = haversine(me['lon'], me['lat'], u['lon'], u['lat'])
                    if dist <= RADIUS_KM:
                        # Append user with calculated distance
                        nearby_users.append({**u, "distance": round(dist, 1), "is_me": False})
                
                msg = json.dumps({"type": "active_users", "users": nearby_users})
                await self.send_personal_message(msg, target_id)

        except Exception as e:
            logger.error(f"BROADCAST-ERROR: {e}")
        finally:
            cursor.close()
            conn.close()

manager = ConnectionManager()

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
    except Exception as e:
        logger.error(f"SECURE-SOCKET-DENIED: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(user_id, websocket)
    logger.info(f"SOCKET-OPEN: User {user_id} established connection.")
    await manager.broadcast_active_users()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'search_nearest':
                lat, lon = message.get('lat', 0), message.get('lon', 0)
                logger.info(f"P2P-SEARCH: User {user_id} scanning at ({lat}, {lon})")
                
                conn = get_db_connection()
                if not conn: continue
                from db_helper import get_cursor, is_postgres
                cursor = get_cursor(conn, dict_cursor=True)
                
                try:
                    # PostgreSQL/MySQL compatible insert/update
                    if is_postgres():
                        # PostgreSQL UPSERT
                        cursor.execute("""
                            INSERT INTO active_sessions (user_id, latitude, longitude, status)
                            VALUES (%s, %s, %s, 'searching')
                            ON CONFLICT (user_id) DO UPDATE 
                            SET latitude=%s, longitude=%s, status='searching', last_active=CURRENT_TIMESTAMP
                        """, (user_id, lat, lon, lat, lon))
                    else:
                        # MySQL UPSERT
                        cursor.execute("""
                            INSERT INTO active_sessions (user_id, latitude, longitude, status)
                            VALUES (%s, %s, %s, 'searching')
                            ON DUPLICATE KEY UPDATE 
                            latitude=%s, longitude=%s, status='searching'
                        """, (user_id, lat, lon, lat, lon))
                    conn.commit()
                    
                    # Simple matching: Find any other user searching (no complex geospatial)
                    cursor.execute("""
                        SELECT user_id FROM active_sessions
                        WHERE user_id != %s AND status = 'searching'
                        LIMIT 1
                    """, (user_id,))
                    
                    match = cursor.fetchone()
                    if match:
                        peer_id = match['user_id'] if isinstance(match, dict) else match[0]
                        logger.info(f"P2P-MATCH: {user_id} <---> {peer_id} (Human Linked)")
                        cursor.execute("UPDATE active_sessions SET status='chatting' WHERE user_id IN (%s, %s)", (user_id, peer_id))
                        conn.commit()
                        await manager.send_personal_message(json.dumps({"type": "match_found", "peer_id": peer_id}), user_id)
                        await manager.send_personal_message(json.dumps({"type": "match_found", "peer_id": user_id}), peer_id)
                    else:

                        # NO HUMAN FOUND IMMEDIATELY: ENTER WAIT LOOP
                        logger.info(f"WAITING: User {user_id} entering retention pool...")
                        
                        # Try to find a match for 7 seconds before giving up
                        found_human = False
                        for _ in range(7):
                            await asyncio.sleep(1)
                            
                            # Check if I was picked up by someone else
                            conn.commit()
                            cursor.execute("SELECT status FROM active_sessions WHERE user_id = %s", (user_id,))
                            me = cursor.fetchone()
                            if me and me.get('status') != 'searching':
                                logger.info(f"MATCH-CHECK: User {user_id} was picked up by peer.")
                                found_human = True
                                break
                            
                            # Check if someone new joined
                            cursor.execute("""
                                SELECT user_id FROM active_sessions
                                WHERE user_id != %s AND status = 'searching'
                                LIMIT 1
                            """, (user_id,))
                            new_peer = cursor.fetchone()
                            
                            if new_peer:
                                peer_id = new_peer['user_id'] if isinstance(new_peer, dict) else new_peer[0]
                                logger.info(f"P2P-MATCH (DELAYED): {user_id} <---> {peer_id}")
                                
                                # Atomic Update Attempt
                                cursor.execute("""
                                    UPDATE active_sessions 
                                    SET status='chatting' 
                                    WHERE user_id IN (%s, %s) AND status='searching'
                                """, (user_id, peer_id))
                                conn.commit()
                                
                                if cursor.rowcount == 2:
                                    await manager.send_personal_message(json.dumps({"type": "match_found", "peer_id": peer_id}), user_id)
                                    await manager.send_personal_message(json.dumps({"type": "match_found", "peer_id": user_id}), peer_id)
                                    found_human = True
                                    break
                        
                        if not found_human:
                             # TIMEOUT REACHED -> DEPLOY BOT
                             logger.info(f"BOT-MATCH: {user_id} paired with AI (Timeout)")
                             cursor.execute("UPDATE active_sessions SET status='chatting' WHERE user_id = %s", (user_id,))
                             conn.commit()
                             
                             await manager.send_personal_message(json.dumps({
                                 "type": "match_found",  
                                 "peer_id": 0,  
                                 "is_bot": True 
                             }), user_id)
                    
                    await manager.broadcast_active_users()
                    
                except Exception as e:
                    logger.error(f"MESH-ENGINE ERROR: {e}")
                finally:
                    cursor.close()
                    conn.close()

            elif message['type'] == 'log_msg':
                peer_id = message.get('peer_id')
                msg_text = message.get('text')
                logger.info(f"CHAT-LOG: {user_id} -> {peer_id}: {msg_text}")
                
                if peer_id == 0:
                    # HANDLE BOT BRAIN
                    await manager.send_personal_message(json.dumps({"type": "bot_typing", "state": True}), user_id)
                    await asyncio.sleep(random.uniform(1, 3)) # Simulate human typing
                    reply = bot_brain.get_reply(msg_text)
                    await manager.send_personal_message(json.dumps({
                        "type": "chat_msg", "peer_id": 0, "text": reply, "from": "stranger"
                    }), user_id)
                    logger.info(f"BOT-REPLY: {user_id} Received: {reply}")

            elif message['type'] == 'ping':
                await manager.send_personal_message(json.dumps({"type": "pong", "ts": message.get("ts")}), user_id)

            elif message['type'] in ['offer', 'answer', 'ice']:
                peer_id = message.get('peer_id')
                if peer_id and peer_id != 0:
                    await manager.send_personal_message(json.dumps(message), peer_id)

    except WebSocketDisconnect:
        logger.info(f"SOCKET-CLOSE: User {user_id} disconnected.")
        manager.disconnect(user_id)
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM active_sessions WHERE user_id = %s", (user_id,))
            conn.commit()
            cursor.close()
            conn.close()
        await manager.broadcast_active_users()
    except Exception as e:
        logger.error(f"SOCKET-CRITICAL: {e}")
        manager.disconnect(user_id)
