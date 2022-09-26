import os
import bin

if __name__ == "__main__":
    app = bin.create_app()
    app.run(debug=True)
