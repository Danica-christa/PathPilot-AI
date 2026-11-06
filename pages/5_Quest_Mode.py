
import streamlit as st
import random
import time

st.set_page_config(
    page_title="PathPilot FunZone",
    page_icon="🎮",
    layout="wide"
)

# =====================================
# BRIGHT ARCADE THEME
# =====================================

st.markdown("""
<style>
.stApp {
    background: #FFF9F2;
    color: #243047;
}

[data-testid="stSidebar"] {
    background: #F0E9FF;
}

[data-testid="stSidebar"] * {
    color: #29213F !important;
}

[data-testid="stHeader"] {
    background: #FFF9F2;
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
}

h1, h2, h3, p, label {
    color: #243047 !important;
}

[data-testid="stMarkdownContainer"] {
    color: #243047;
}

[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 16px;
    border: 2px solid #E9E0FF;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: #243047 !important;
}

div.stButton > button {
    background: white;
    color: #29334B !important;
    border: 2px solid #D8C8FF;
    border-radius: 14px;
    font-weight: 700;
    min-height: 48px;
}

div.stButton > button:hover {
    background: #EDE4FF;
    border-color: #8B5CF6;
    color: #35216A !important;
}

div.stButton > button:disabled {
    background: #E8E8F0;
    color: #586174 !important;
    border-color: #D7D7E3;
}

[data-testid="stAlert"] {
    border-radius: 14px;
}

.arcade-hero {
    background: linear-gradient(120deg, #FFE0ED, #E6E0FF, #D8F6FF);
    padding: 30px;
    border-radius: 22px;
    border: 2px solid #E8D6FF;
    margin-bottom: 20px;
}

.arcade-hero h1 {
    font-size: 38px;
    color: #452B75 !important;
    margin-bottom: 10px;
}

.arcade-hero p {
    color: #4F4665 !important;
    font-size: 17px;
}

.game-card {
    background: white;
    border: 2px solid #E9E0FF;
    border-radius: 18px;
    padding: 20px;
    text-align: center;
    min-height: 130px;
}

.game-card h3 {
    color: #452B75 !important;
}

.game-card p {
    color: #596579 !important;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# SESSION STATE
# =====================================

def init(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


init("fun_game", "🏠 Game Lobby")
init("fun_played", 0)
init("fun_wins", 0)

init("ttt", [""] * 9)
init("ttt_done", False)
init("ttt_result", "")

init("rps_result", None)

init("memory_cards", [])
init("memory_open", [])
init("memory_matched", [])
init("memory_moves", 0)
init("memory_done", False)

init("mole_position", random.randint(0, 8))
init("mole_score", 0)
init("mole_round", 0)
init("mole_done", False)

init("emoji_index", 0)
init("emoji_score", 0)
init("emoji_answered", False)
init("emoji_feedback", "")

init("reaction_state", "ready")
init("reaction_start", 0.0)
init("reaction_delay", 0.0)
init("reaction_result", None)
init("reaction_best", None)


def record(win):
    st.session_state.fun_played += 1
    if win:
        st.session_state.fun_wins += 1


def navigate(game):
    st.session_state.fun_game = game
    st.rerun()


# =====================================
# TIC TAC TOE LOGIC
# =====================================

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]


def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]

    if all(board):
        return "Draw"

    return None


def computer_move(board):
    empty = [i for i in range(9) if not board[i]]

    for player in ["O", "X"]:
        for i in empty:
            test = board.copy()
            test[i] = player
            if check_winner(test) == player:
                return i

    if 4 in empty:
        return 4

    corners = [i for i in [0, 2, 6, 8] if i in empty]

    if corners:
        return random.choice(corners)

    return random.choice(empty)


def tic_click(i):
    board = st.session_state.ttt

    if st.session_state.ttt_done or board[i]:
        return

    board[i] = "X"
    result = check_winner(board)

    if result is None:
        move = computer_move(board)
        board[move] = "O"
        result = check_winner(board)

    if result:
        st.session_state.ttt_done = True

        if result == "X":
            st.session_state.ttt_result = "🎉 You win!"
            record(True)
        elif result == "O":
            st.session_state.ttt_result = "🤖 Computer wins!"
            record(False)
        else:
            st.session_state.ttt_result = "🤝 It's a draw!"
            record(False)


def reset_tic():
    st.session_state.ttt = [""] * 9
    st.session_state.ttt_done = False
    st.session_state.ttt_result = ""


# =====================================
# ROCK PAPER SCISSORS
# =====================================

def play_rps(player):
    computer = random.choice(
        ["Rock", "Paper", "Scissors"]
    )

    if player == computer:
        result = "Draw"
    elif (
        (player == "Rock" and computer == "Scissors")
        or (player == "Paper" and computer == "Rock")
        or (player == "Scissors" and computer == "Paper")
    ):
        result = "Win"
    else:
        result = "Lose"

    st.session_state.rps_result = (
        player, computer, result
    )

    record(result == "Win")


# =====================================
# MEMORY MATCH
# =====================================

def reset_memory():
    cards = [
        "🍓", "🍓", "🐼", "🐼",
        "🌈", "🌈", "🍩", "🍩",
        "🦋", "🦋", "🍕", "🍕"
    ]

    random.shuffle(cards)

    st.session_state.memory_cards = cards
    st.session_state.memory_open = []
    st.session_state.memory_matched = []
    st.session_state.memory_moves = 0
    st.session_state.memory_done = False


if not st.session_state.memory_cards:
    reset_memory()


def memory_click(i):
    if st.session_state.memory_done:
        return

    opened = st.session_state.memory_open
    matched = st.session_state.memory_matched

    if i in matched or i in opened:
        return

    if len(opened) == 2:
        st.session_state.memory_open = []
        opened = st.session_state.memory_open

    opened.append(i)

    if len(opened) == 2:
        st.session_state.memory_moves += 1

        cards = st.session_state.memory_cards

        if cards[opened[0]] == cards[opened[1]]:
            matched.extend(opened)
            st.session_state.memory_open = []

            if len(matched) == 12:
                st.session_state.memory_done = True
                record(True)


# =====================================
# WHACK A MOLE
# =====================================

def reset_mole():
    st.session_state.mole_position = random.randint(0, 8)
    st.session_state.mole_score = 0
    st.session_state.mole_round = 0
    st.session_state.mole_done = False


def hit_mole(i):
    if st.session_state.mole_done:
        return

    if i == st.session_state.mole_position:
        st.session_state.mole_score += 1

    st.session_state.mole_round += 1

    if st.session_state.mole_round >= 15:
        st.session_state.mole_done = True
        record(st.session_state.mole_score >= 10)
    else:
        st.session_state.mole_position = random.randint(0, 8)


# =====================================
# EMOJI RIDDLES
# =====================================

EMOJI_PUZZLES = [
    ("🦁👑", "The Lion King",
     ["The Lion King", "Jungle Book", "Madagascar"]),
    ("❄️👸", "Frozen",
     ["Frozen", "Cinderella", "Moana"]),
    ("🕷️👨", "Spider-Man",
     ["Batman", "Spider-Man", "Superman"]),
    ("🐼🥋", "Kung Fu Panda",
     ["Kung Fu Panda", "Zootopia", "Finding Nemo"]),
    ("🚢🧊💔", "Titanic",
     ["Titanic", "Avatar", "Frozen"]),
    ("👻🏠", "Haunted House",
     ["Dream House", "Haunted House", "Tree House"]),
    ("🍎📱", "Apple",
     ["Samsung", "Apple", "Google"]),
    ("🌧️🐱🐶", "Raining Cats and Dogs",
     ["Animal Rescue", "Raining Cats and Dogs", "Pet Shop"])
]


def answer_emoji(choice):
    if st.session_state.emoji_answered:
        return

    q = EMOJI_PUZZLES[st.session_state.emoji_index]
    correct = choice == q[1]

    if correct:
        st.session_state.emoji_score += 1
        st.session_state.emoji_feedback = "🎉 Correct!"
    else:
        st.session_state.emoji_feedback = (
            "Not quite! Answer: " + q[1]
        )

    st.session_state.emoji_answered = True


def next_emoji():
    if not st.session_state.emoji_answered:
        return

    if st.session_state.emoji_index == len(EMOJI_PUZZLES) - 1:
        record(st.session_state.emoji_score >= 5)
        st.session_state.emoji_index = len(EMOJI_PUZZLES)
    else:
        st.session_state.emoji_index += 1
        st.session_state.emoji_answered = False
        st.session_state.emoji_feedback = ""


def reset_emoji():
    st.session_state.emoji_index = 0
    st.session_state.emoji_score = 0
    st.session_state.emoji_answered = False
    st.session_state.emoji_feedback = ""


# =====================================
# REACTION RUSH
# =====================================

def start_reaction():
    st.session_state.reaction_state = "waiting"
    st.session_state.reaction_start = time.perf_counter()
    st.session_state.reaction_delay = random.uniform(2, 5)
    st.session_state.reaction_result = None


def reaction_click():
    if st.session_state.reaction_state != "waiting":
        return

    elapsed = (
        time.perf_counter()
        - st.session_state.reaction_start
    )

    if elapsed < st.session_state.reaction_delay:
        st.session_state.reaction_state = "early"
        st.session_state.reaction_result = None
    else:
        ms = int(
            (elapsed - st.session_state.reaction_delay) * 1000
        )

        st.session_state.reaction_result = ms
        st.session_state.reaction_state = "finished"

        best = st.session_state.reaction_best

        if best is None or ms < best:
            st.session_state.reaction_best = ms

        record(ms < 600)


# =====================================
# HEADER AND NAVIGATION
# =====================================

st.markdown("""
<div class="arcade-hero">
    <h1>🎮 PathPilot FunZone</h1>
    <p>
        Your happy place! Take a break, play mini-games,
        and forget about studying for a little while. 🌈
    </p>
</div>
""", unsafe_allow_html=True)

a, b, c = st.columns(3)

a.metric("🎮 Games Played", st.session_state.fun_played)
b.metric("🏆 Wins", st.session_state.fun_wins)
c.metric("🕹️ Games Available", 6)

st.divider()

GAMES = [
    ("❌⭕ Tic-Tac-Toe", "Beat the computer"),
    ("🃏 Memory Match", "Find the matching cards"),
    ("🐹 Whack-a-Mole", "Catch the sneaky mole"),
    ("✊ Rock Paper Scissors", "Quick hand battles"),
    ("🎭 Emoji Riddles", "Guess the emoji clues"),
    ("⚡ Reaction Rush", "Test your reflexes")
]

with st.sidebar:
    st.markdown("## 🎮 FunZone")
    st.caption("Choose your adventure")

    if st.button("🏠 Game Lobby", use_container_width=True):
        navigate("🏠 Game Lobby")

    for name, desc in GAMES:
        if st.button(name, use_container_width=True):
            navigate(name)

    st.divider()
    st.caption("No homework allowed here! 🌴")


# =====================================
# GAME LOBBY
# =====================================

game = st.session_state.fun_game

if game == "🏠 Game Lobby":

    st.header("🕹️ Choose Your Adventure")

    st.write("Six mini-games. Pick your mood!")

    for start in range(0, len(GAMES), 2):
        cols = st.columns(2)

        for col, (name, desc) in zip(
            cols, GAMES[start:start + 2]
        ):
            with col:
                st.markdown(
                    f"""
                    <div class="game-card">
                        <h3>{name}</h3>
                        <p>{desc}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "▶ Play Now",
                    key="lobby_" + name,
                    use_container_width=True
                ):
                    navigate(name)

                st.write("")


# =====================================
# TIC TAC TOE
# =====================================

elif game == "❌⭕ Tic-Tac-Toe":

    st.header("❌⭕ Tic-Tac-Toe")
    st.write("You are ❌. The computer is ⭕.")

    if st.session_state.ttt_result:
        st.success(st.session_state.ttt_result)
    else:
        st.info("Your turn!")

    left, middle, right = st.columns([1, 2, 1])

    with middle:
        for row in range(3):
            cols = st.columns(3)

            for col in range(3):
                i = row * 3 + col

                with cols[col]:
                    value = st.session_state.ttt[i]

                    st.button(
                        "❌" if value == "X"
                        else "⭕" if value == "O"
                        else "·",
                        key=f"ttt_{i}",
                        use_container_width=True,
                        disabled=bool(value) or st.session_state.ttt_done,
                        on_click=tic_click,
                        args=(i,)
                    )

        st.button("🔄 Play Again", on_click=reset_tic)


# =====================================
# MEMORY MATCH
# =====================================

elif game == "🃏 Memory Match":

    st.header("🃏 Memory Match")
    st.write("Flip cards and find all six pairs!")

    a, b = st.columns(2)

    a.metric("Moves", st.session_state.memory_moves)
    b.metric(
        "Pairs Found",
        f"{len(st.session_state.memory_matched) // 2}/6"
    )

    left, middle, right = st.columns([1, 3, 1])

    with middle:
        for row in range(3):
            cols = st.columns(4)

            for col in range(4):
                i = row * 4 + col

                visible = (
                    i in st.session_state.memory_open
                    or i in st.session_state.memory_matched
                )

                label = (
                    st.session_state.memory_cards[i]
                    if visible else "❔"
                )

                with cols[col]:
                    st.button(
                        label,
                        key=f"mem_{i}",
                        use_container_width=True,
                        disabled=i in st.session_state.memory_matched,
                        on_click=memory_click,
                        args=(i,)
                    )

    if st.session_state.memory_done:
        st.success("🎉 You found all six pairs!")

    st.button("🔄 Shuffle Cards", on_click=reset_memory)


# =====================================
# WHACK A MOLE
# =====================================

elif game == "🐹 Whack-a-Mole":

    st.header("🐹 Whack-a-Mole")

    st.write(
        "Find the mole and tap it! "
        "You have 15 turns to score at least 10 hits."
    )

    a, b = st.columns(2)

    a.metric("🐹 Hits", st.session_state.mole_score)
    b.metric(
        "🎯 Turns Left",
        15 - st.session_state.mole_round
    )

    left, middle, right = st.columns([1, 2, 1])

    with middle:
        for row in range(3):
            cols = st.columns(3)

            for col in range(3):
                i = row * 3 + col

                label = (
                    "🐹"
                    if i == st.session_state.mole_position
                    else "🕳️"
                )

                with cols[col]:
                    st.button(
                        label,
                        key=f"mole_{i}",
                        use_container_width=True,
                        disabled=st.session_state.mole_done,
                        on_click=hit_mole,
                        args=(i,)
                    )

    if st.session_state.mole_done:
        if st.session_state.mole_score >= 10:
            st.success("🏆 Mole Master! You win!")
        else:
            st.info("Nice try! Play again to beat your score.")

    st.button("🔄 New Round", on_click=reset_mole)

    st.caption(
        "Turn-based arcade version: the mole changes "
        "position after every click."
    )


# =====================================
# ROCK PAPER SCISSORS
# =====================================

elif game == "✊ Rock Paper Scissors":

    st.header("✊ Rock Paper Scissors")

    st.write("Choose your move!")

    cols = st.columns(3)

    for col, label, choice in zip(
        cols,
        ["✊ Rock", "✋ Paper", "✌️ Scissors"],
        ["Rock", "Paper", "Scissors"]
    ):
        with col:
            st.button(
                label,
                key="rps_" + choice,
                use_container_width=True,
                on_click=play_rps,
                args=(choice,)
            )

    result = st.session_state.rps_result

    if result:
        player, computer, outcome = result

        emojis = {
            "Rock": "✊",
            "Paper": "✋",
            "Scissors": "✌️"
        }

        a, b = st.columns(2)

        a.metric("You", emojis[player])
        b.metric("Computer", emojis[computer])

        if outcome == "Win":
            st.success("🎉 You win!")
        elif outcome == "Lose":
            st.error("🤖 Computer wins!")
        else:
            st.info("🤝 It's a draw!")


# =====================================
# EMOJI RIDDLES
# =====================================

elif game == "🎭 Emoji Riddles":

    st.header("🎭 Emoji Riddles")

    st.write("Can you guess the movie, brand or phrase?")

    index = st.session_state.emoji_index

    if index >= len(EMOJI_PUZZLES):
        st.success(
            f"🎉 Game finished! Your score: "
            f"{st.session_state.emoji_score}/"
            f"{len(EMOJI_PUZZLES)}"
        )

        st.button(
            "🔄 Play Again",
            on_click=reset_emoji
        )

    else:
        puzzle = EMOJI_PUZZLES[index]

        st.progress(index / len(EMOJI_PUZZLES))

        st.write(
            f"Question {index + 1} of {len(EMOJI_PUZZLES)}"
        )

        st.markdown(
            f"<h1 style='text-align:center;font-size:70px'>"
            f"{puzzle[0]}</h1>",
            unsafe_allow_html=True
        )

        for i, option in enumerate(puzzle[2]):
            st.button(
                option,
                key=f"emoji_{index}_{i}",
                use_container_width=True,
                disabled=st.session_state.emoji_answered,
                on_click=answer_emoji,
                args=(option,)
            )

        if st.session_state.emoji_answered:
            st.info(st.session_state.emoji_feedback)

            st.button(
                "➡️ Next Riddle",
                on_click=next_emoji
            )

        st.metric(
            "⭐ Score",
            st.session_state.emoji_score
        )


# =====================================
# REACTION RUSH
# =====================================

elif game == "⚡ Reaction Rush":

    st.header("⚡ Reaction Rush")

    st.write(
        "Wait for the signal to turn green, "
        "then click as fast as possible!"
    )

    state = st.session_state.reaction_state

    if state == "ready":
        st.info("Ready to test your reflexes?")

        st.button(
            "🚦 Start",
            on_click=start_reaction,
            use_container_width=True
        )

    elif state == "waiting":
        elapsed = (
            time.perf_counter()
            - st.session_state.reaction_start
        )

        if elapsed >= st.session_state.reaction_delay:
            st.success("🟢 GO! CLICK NOW!")
        else:
            st.warning("🔴 WAIT... Don't click yet!")

        st.button(
            "⚡ TAP!",
            on_click=reaction_click,
            use_container_width=True
        )

        st.caption(
            "The signal updates when Streamlit reruns. "
            "This is a casual reaction game, not "
            "a precise reflex measurement."
        )

    elif state == "early":
        st.error("Too early! 😆")

        st.button(
            "🔄 Try Again",
            on_click=start_reaction
        )

    elif state == "finished":
        result = st.session_state.reaction_result

        st.success(f"⚡ Your time: {result} ms")

        st.button(
            "🔄 Play Again",
            on_click=start_reaction
        )

    if st.session_state.reaction_best is not None:
        st.metric(
            "🏆 Best Time",
            f"{st.session_state.reaction_best} ms"
        )


# =====================================
# FOOTER
# =====================================

st.divider()

st.markdown("### 🌈 Fun first, stress later!")

st.write(
    "Take a break, enjoy yourself, and come back "
    "whenever you want another round."
)

if game != "🏠 Game Lobby":
    if st.button("🏠 Back to Game Lobby"):
        navigate("🏠 Game Lobby")

st.caption(
    "PathPilot FunZone | Six mini-games | "
    "Just for fun 💜"
)
