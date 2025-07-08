from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
import uvicorn
import time
from agent import get_ans

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 等待接收消息
            data = await websocket.receive_text()
            print(f"收到消息: {data}")
            
            response = get_ans(data, "deepseek-r1-0528")
            
            # 发送回应
            await websocket.send_json(response)
    except WebSocketDisconnect:
        print("客户端断开连接")

if __name__ == '__main__':
    uvicorn.run(app)

