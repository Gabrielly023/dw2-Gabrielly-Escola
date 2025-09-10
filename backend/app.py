from fastapi import FastAPI

# Criar instância do FastAPI
app = FastAPI()

# Endpoint GET /health
@app.get('/health')
def health():
    return {"status": "ok"}

# Configuração para rodar com uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


