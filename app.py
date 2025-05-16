import pygame
import mysql.connector

pygame.init()

# MySQL setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Anjana2517",
    database="banking_db"
)
cursor = db.cursor()

# Pygame setup
WIDTH, HEIGHT = 800, 600  # Increased height to show 5 transactions
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Online Banking System")
font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()

# Load background image
background_image = pygame.image.load("bank.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)

# Input state
username_input = ""
password_input = ""
amount_input = ""
active_box = None
active_amount = False

# State
current_user = None
message = ""
transactions_list = []  # Stores last 5 transactions
screen_state = "login"

# Input boxes
username_box = pygame.Rect(250, 100, 200, 40)
password_box = pygame.Rect(250, 160, 200, 40)
login_btn = pygame.Rect(250, 230, 90, 40)
register_btn = pygame.Rect(360, 230, 90, 40)

# Dashboard buttons
check_balance_btn = pygame.Rect(100, 100, 200, 50)
amount_box = pygame.Rect(400, 100, 150, 40)
deposit_btn = pygame.Rect(400, 160, 150, 50)
withdraw_btn = pygame.Rect(400, 230, 150, 50)
transaction_btn = pygame.Rect(100, 170, 200, 50)
logout_btn = pygame.Rect(100, 240, 200, 50)

# Helper functions
def draw_text(text, x, y, color=WHITE):
    screen.blit(font.render(text, True, color), (x, y))

def login(username, password):
    global current_user
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    if user:
        current_user = user
        return True
    return False

def register(username, password):
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    return True

def get_balance():
    cursor.execute("SELECT balance FROM users WHERE id = %s", (current_user[0],))
    return cursor.fetchone()[0]

def deposit(amount):
    cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, current_user[0]))
    cursor.execute("INSERT INTO transactions (user_id, type, amount) VALUES (%s, 'deposit', %s)", (current_user[0], amount))
    db.commit()

def withdraw(amount):
    if get_balance() >= amount:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, current_user[0]))
        cursor.execute("INSERT INTO transactions (user_id, type, amount) VALUES (%s, 'withdraw', %s)", (current_user[0], amount))
        db.commit()
        return True
    return False

def view_transactions():
    cursor.execute("SELECT type, amount, timestamp FROM transactions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 5", (current_user[0],))
    return cursor.fetchall()

# Main loop
running = True
while running:
    screen.blit(background_image, (0, 0))
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if screen_state == "login":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if username_box.collidepoint(event.pos):
                    active_box = 'username'
                elif password_box.collidepoint(event.pos):
                    active_box = 'password'
                else:
                    active_box = None

                if login_btn.collidepoint(event.pos):
                    if login(username_input, password_input):
                        screen_state = "dashboard"
                        message = ""
                        username_input, password_input = "", ""
                        transactions_list = []
                    else:
                        message = "Invalid credentials."

                elif register_btn.collidepoint(event.pos):
                    if register(username_input, password_input):
                        message = "Registered!"
                    else:
                        message = "Username already taken."

            if event.type == pygame.KEYDOWN:
                if active_box == 'username':
                    if event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    else:
                        username_input += event.unicode
                elif active_box == 'password':
                    if event.key == pygame.K_BACKSPACE:
                        password_input = password_input[:-1]
                    else:
                        password_input += event.unicode

        elif screen_state == "dashboard":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if amount_box.collidepoint(event.pos):
                    active_amount = True
                else:
                    active_amount = False

                if check_balance_btn.collidepoint(event.pos):
                    message = f"Balance: ${get_balance():.2f}"
                    transactions_list = []

                elif deposit_btn.collidepoint(event.pos):
                    try:
                        amt = float(amount_input)
                        if amt > 0:
                            deposit(amt)
                            message = f"Deposited ${amt:.2f}"
                            amount_input = ""
                        else:
                            message = "Enter positive amount."
                        transactions_list = []
                    except:
                        message = "Invalid amount."
                        transactions_list = []

                elif withdraw_btn.collidepoint(event.pos):
                    try:
                        amt = float(amount_input)
                        if amt > 0:
                            if withdraw(amt):
                                message = f"Withdrew ${amt:.2f}"
                                amount_input = ""
                            else:
                                message = "Insufficient balance."
                        else:
                            message = "Enter positive amount."
                        transactions_list = []
                    except:
                        message = "Invalid amount."
                        transactions_list = []

                elif transaction_btn.collidepoint(event.pos):
                    transactions_list = view_transactions()
                    message = "Last 5 Transactions:"

                elif logout_btn.collidepoint(event.pos):
                    current_user = None
                    screen_state = "login"
                    message = ""
                    amount_input = ""
                    transactions_list = []

            if event.type == pygame.KEYDOWN and active_amount:
                if event.key == pygame.K_BACKSPACE:
                    amount_input = amount_input[:-1]
                elif event.unicode.isnumeric() or event.unicode == ".":
                    amount_input += event.unicode

    # Drawing interface
    if screen_state == "login":
        draw_text("Username:", 140, 105)
        draw_text("Password:", 140, 165)
        pygame.draw.rect(screen, BLUE if active_box == 'username' else GRAY, username_box)
        pygame.draw.rect(screen, BLUE if active_box == 'password' else GRAY, password_box)
        draw_text(username_input, username_box.x + 5, username_box.y + 5)
        draw_text("*" * len(password_input), password_box.x + 5, password_box.y + 5)

        pygame.draw.rect(screen, GRAY, login_btn)
        pygame.draw.rect(screen, GRAY, register_btn)
        draw_text("Login", login_btn.x + 10, login_btn.y + 5, BLACK)
        draw_text("Register", register_btn.x + 5, register_btn.y + 5, BLACK)

    elif screen_state == "dashboard":
        draw_text(f"Welcome {current_user[1]}", 100, 40)

        # Buttons and Input
        pygame.draw.rect(screen, GRAY, check_balance_btn)
        pygame.draw.rect(screen, GRAY, transaction_btn)
        pygame.draw.rect(screen, GRAY, logout_btn)

        draw_text("Check Balance", check_balance_btn.x + 10, check_balance_btn.y + 10, BLACK)
        draw_text("View Transactions", transaction_btn.x + 10, transaction_btn.y + 10, BLACK)
        draw_text("Logout", logout_btn.x + 10, logout_btn.y + 10, BLACK)

        draw_text("Amount:", 310, 110)
        pygame.draw.rect(screen, BLUE if active_amount else GRAY, amount_box)
        draw_text(amount_input, amount_box.x + 5, amount_box.y + 5)

        pygame.draw.rect(screen, GRAY, deposit_btn)
        pygame.draw.rect(screen, GRAY, withdraw_btn)
        draw_text("Deposit", deposit_btn.x + 30, deposit_btn.y + 10, BLACK)
        draw_text("Withdraw", withdraw_btn.x + 25, withdraw_btn.y + 10, BLACK)

    # Draw message and transactions
    y_offset = 420
    draw_text(message, 50, y_offset, WHITE)

    for i, txn in enumerate(transactions_list):
        txn_text = f"{txn[0].capitalize()} ${txn[1]} on {txn[2].strftime('%Y-%m-%d %H:%M:%S')}"
        draw_text(txn_text, 50, y_offset + (i + 1) * 25, WHITE)

    pygame.display.update()
    clock.tick(30)

pygame.quit()
