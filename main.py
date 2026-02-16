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

@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        with open("templates/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        logger.error(f"UI LOAD ERROR: {e}")
        return HTMLResponse(content="<h1>Critical UI Error. Check logs.</h1>", status_code=500)

# --- CORE BUSINESS LOGIC (REG/LOGIN) ---
@app.post("/register", response_model=Token)
async def register(user: UserRegister):
    logger.info(f"PROTOCOL-REG: {user.username} is requesting entry.")
    
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
        cursor = get_cursor(conn, dict_cursor=True)
        try:
            cursor.execute("SELECT user_id, latitude as lat, longitude as lon FROM active_sessions")
            users = cursor.fetchall()
            # Convert to list of dicts for PostgreSQL compatibility
            if users:
                msg = json.dumps({"type": "active_users", "users": [dict(u) if hasattr(u, 'items') else u for u in users]})
                for uid in list(self.active_connections.keys()):
                    await self.send_personal_message(msg, uid)
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
                        # ZERO-WAIT AI BOT FALLBACK
                        logger.info(f"BOT-MATCH: Scaling up for User {user_id} (No neighbors found)")
                        # peer_id = 0 represents the system bot
                        await manager.send_personal_message(json.dumps({
                            "type": "match_found", 
                            "peer_id": 0,
                            "system": True,
                            "bot_name": "Stranger"
                        }), user_id)
                        
                        # Send initial bot greeting with a small delay
                        await asyncio.sleep(1)
                        greeting = random.choice(bot_brain.greetings)
                        await manager.send_personal_message(json.dumps({
                            "type": "bot_typing", "state": True
                        }), user_id)
                        await asyncio.sleep(1.5)
                        await manager.send_personal_message(json.dumps({
                            "type": "chat_msg", "peer_id": 0, "text": greeting, "from": "stranger"
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
