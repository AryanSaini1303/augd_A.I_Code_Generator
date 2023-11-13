import time

def dance():
    for _ in range(2):  # Make the dance repeat twice
        print("  o")
        print(" /|\\")
        print("  |")
        print(" / \\")
        time.sleep(0.5)
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        time.sleep(0.5)

dance()  # Call the dance function