from fastapi import FastAPI, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from models import Base, User, SessionLocal, engine
from schemas import SUser
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Инициализируем папку для шаблонов Jinja2
templates = Jinja2Templates(directory="templates")

# Создаем таблицы в базе данных при запуске приложения
Base.metadata.create_all(bind=engine)

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Функция для проверки пароля
def verify_password(plain_password, hashed_password):
    return plain_password == hashed_password

# Регистрация пользователя
@app.post("/register/", response_model=SUser)
def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    db_user = User(username=username, email=email, hashed_password=password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# Вход пользователя
@app.post("/login/")
def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return templates.TemplateResponse("welcome.html", {"request": request, "username": username})

# Маршрут для отображения формы регистрации
@app.get("/register/", response_class=HTMLResponse)
def get_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Маршрут для отображения формы входа
@app.get("/login/", response_class=HTMLResponse)
def get_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Маршрут для отображения главной страницы банка
@app.get("/", response_class=HTMLResponse)
def get_main_bank_page(request: Request):
    return templates.TemplateResponse("bank_main.html", {"request": request})

# Маршрут для отображения балансов пользователя
@app.get("/balances/", response_class=HTMLResponse)
def get_balances(request: Request, username: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return templates.TemplateResponse("balances.html", {"request": request, "user": db_user})

# Маршрут для перевода денег между валютами
@app.post("/transfer/")
def transfer_funds(request: Request, username: str = Form(...), from_currency: str = Form(...), to_currency: str = Form(...), amount: float = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if from_currency == to_currency:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same currency")

    if from_currency == "USD":
        if db_user.balance_usd < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        db_user.balance_usd -= amount
    elif from_currency == "EUR":
        if db_user.balance_eur < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        db_user.balance_eur -= amount
    elif from_currency == "RUB":
        if db_user.balance_rub < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        db_user.balance_rub -= amount
    else:
        raise HTTPException(status_code=400, detail="Invalid currency")

    if to_currency == "USD":
        db_user.balance_usd += amount
    elif to_currency == "EUR":
        db_user.balance_eur += amount
    elif to_currency == "RUB":
        db_user.balance_rub += amount
    else:
        raise HTTPException(status_code=400, detail="Invalid currency")

    db.commit()
    db.refresh(db_user)

    return templates.TemplateResponse("balances.html", {"request": request, "user": db_user})