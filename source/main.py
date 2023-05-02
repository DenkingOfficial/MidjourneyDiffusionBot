from app import create_app

queue = []
app = create_app(queue)
app.run()
