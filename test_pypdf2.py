try:
    import PyPDF2
    print("PyPDF2 imported successfully!")
    print(f"PyPDF2 version: {PyPDF2.__version__}")
except ImportError as e:
    print(f"Error importing PyPDF2: {e}")
