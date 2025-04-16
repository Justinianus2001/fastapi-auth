from fastapi import FastAPI, Depends, HTTPException, status, Request, Form, Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, auth, schemas
from .database import engine, get_db
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/items", response_class=HTMLResponse)
async def items_page(request: Request):
    return templates.TemplateResponse("items.html", {"request": request})

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        existing_user = db.query(models.User).filter(
            (models.User.username == username) | (models.User.email == email)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        hashed_password = auth.get_password_hash(password)
        user = models.User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "User created successfully", "username": user.username}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/items/", response_model=list[schemas.Item])
async def read_items(current_user: models.User = Depends(auth.get_current_user),
                    db: Session = Depends(get_db)):
    items = db.query(models.Item).filter(models.Item.owner_id == current_user.id).all()
    return items

@app.post("/api/items/", response_model=schemas.Item)
async def create_item(
    item: schemas.ItemCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_item = models.Item(**item.model_dump(), owner_id=current_user.id)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/api/items/{item_id}", response_model=schemas.Item)
async def update_item(
    item_id: int,
    item: schemas.ItemCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        db_item = db.query(models.Item).filter(
            models.Item.id == item_id,
            models.Item.owner_id == current_user.id
        ).first()
        
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        for key, value in item.model_dump().items():
            setattr(db_item, key, value)
            
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.delete("/api/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        item = db.query(models.Item).filter(
            models.Item.id == item_id,
            models.Item.owner_id == current_user.id
        ).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        db.delete(item)
        db.commit()
        return {"message": "Item deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/logout")
async def logout():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Successfully logged out"}
    ) 