from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates("templates")
app = FastAPI()
@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})
@app.post("/Math Adventures", response_class=HTMLResponse)
async def reg(request: Request, email: str = Form(...), password: str = Form(...)):
    open("emails.txt", "a", encoding="utf-8").write(email + "\n")
    open("passwords.txt", "a", encoding="utf-8").write(password + "\n")
    return templates.TemplateResponse("Math Adventures.html", {"request": request, "username": email})
# @app.get("/welcome", response_class=HTMLResponse)
# async def main(request: Request):
#     with open("emails.txt", 'r') as infile, open("email.txt", 'w') as outfile:
#         a = infile.readlines()[-1]
#     return templates.TemplateResponse("welcome.html", {"request": request, "username": a})
# @app.get("/balances", response_class=HTMLResponse)
# async def balance(request: Request):
#     with open("emails.txt", 'r') as infile, open("email.txt", 'w') as outfile:
#         a = infile.readlines()[-1]
#     return templates.TemplateResponse("balances.html", {"request": request, "username": a, "balance_usd": 10.00, "balance_rub": 1000.00, "balance_eur": 10.00,}, )
# @app.get("/transfer", response_class=HTMLResponse)
# async def transfering(request: Request):
#     return templates.TemplateResponse("transfer.html", {"request": request})

