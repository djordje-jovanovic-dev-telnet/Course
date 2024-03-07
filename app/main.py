from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = False

    try:
        conn = psycopg2.connect(host = 'localhost', database = 'TestDatabase', user = 'postgres', password = '1234', cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull")
    except Exception as error:
        print("Connecting to database failed")
        print(f"Error: {error}")



def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p
    
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
        
my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "title of post 2", "content": "content of post 2", "id": 2}] 

@app.get("/")
def root():
    return {"message": "Hey"}

@app.get("/posts")
def get_posts():
    cursor.execute("""select * from posts""")
    post = cursor.fetchall()
    return {"data": post}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 10000)
    cursor.execute("""insert into posts (title, content, published) values (%s, %s, %s) returning * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}
def get_post(id: int, response: Response):
    cursor.execute("""select * from posts where id = %s""", (str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'post with id: {id} is not found')
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""delete from posts where id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Post with {id} does not exist')
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    print(post)
    index = find_index_post(id)
    
    if index == None:
        raise HTTPException(status=status.HTTP_404_NOT_FOUND, detail = f'Post with {id} does not exist')
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}
    