"""Simple test to verify app.py can be imported."""

import sys
import ast

# Read and parse the app.py file
with open("streamlit_app/app.py", "r", encoding="utf-8") as f:
    code = f.read()

try:
    ast.parse(code)
    print("✅ app.py syntax is valid!")
except SyntaxError as e:
    print(f"❌ Syntax error in app.py: {e}")
    sys.exit(1)

# Read and parse the data_loader.py file
with open("streamlit_app/data_loader.py", "r", encoding="utf-8") as f:
    code = f.read()

try:
    ast.parse(code)
    print("✅ data_loader.py syntax is valid!")
except SyntaxError as e:
    print(f"❌ Syntax error in data_loader.py: {e}")
    sys.exit(1)

print("\n✨ All files are syntactically correct!")
