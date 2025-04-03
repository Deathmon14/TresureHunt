clues = {
    "route_a": {
        1: {"question": "Find the place where ancient scrolls are stored.", "answer": "Ancient Archives", "next_clue": 2},
        2: {"question": "Inside the Archives, access the high-security node.", "answer": "Cybersecurity Lab", "next_clue": 3},
        3: {"question": "PRISM flagged this vault as corrupted — locate it.", "answer": "Quarantine Bay", "next_clue": 4},
        4: {"question": "Decode the inscription under the mainframe casing.", "answer": "PRISM Core", "next_clue": 5},
        5: {"question": "SHADE’s last ping was from the east wing terminal.", "answer": "Echo Terminal", "next_clue": 6},
        6: {"question": "Final challenge: Solve the vault puzzle.", "answer": "Secret Vault", "next_clue": None}
    },
    "route_b": {
        1: {"question": "Locate the encrypted data center.", "answer": "Data Storage", "next_clue": 2},
        2: {"question": "Decrypt the passcode at the control room.", "answer": "Control Room", "next_clue": 3},
        3: {"question": "Trace the backup logs to the silent corridor.", "answer": "Archive Tunnel", "next_clue": 4},
        4: {"question": "Find the vent node connected to SHADE’s output.", "answer": "Hidden Uplink", "next_clue": 5},
        5: {"question": "SHADE’s core is behind the biometric lock. Where?", "answer": "Biometric Chamber", "next_clue": 6},
        6: {"question": "Final challenge: Solve the vault puzzle.", "answer": "Secret Vault", "next_clue": None}
    },
    "route_c": {
        1: {"question": "Track the AI’s signal to the first location.", "answer": "Main Server", "next_clue": 2},
        2: {"question": "Find the master key in the network hub.", "answer": "Network Hub", "next_clue": 3},
        3: {"question": "Enter the portal marked with a red prism.", "answer": "Simulation Room", "next_clue": 4},
        4: {"question": "Solve the binary riddle near the interface node.", "answer": "Logic Gate", "next_clue": 5},
        5: {"question": "What system was SHADE trying to override?", "answer": "PRISM Subnet", "next_clue": 6},
        6: {"question": "Final challenge: Solve the vault puzzle.", "answer": "Secret Vault", "next_clue": None}
    },
    "route_d": {
        1: {"question": "Begin at the abandoned AI research node.", "answer": "Abandoned Server", "next_clue": 2},
        2: {"question": "Find the backdoor port hidden in plain sight.", "answer": "Port 404", "next_clue": 3},
        3: {"question": "SHADE left coordinates at this central hub.", "answer": "Relay Station", "next_clue": 4},
        4: {"question": "Search for the glitching module behind the library stack.", "answer": "Glitch Module", "next_clue": 5},
        5: {"question": "Crack the firewall and access the last datastream.", "answer": "SHADE Terminal", "next_clue": 6},
        6: {"question": "Final challenge: Solve the vault puzzle.", "answer": "Secret Vault", "next_clue": None}
    }
}


# Bonus challenges that can be triggered randomly
bonus_challenges = [
    {
        "question": "🔎 Hidden Riddle: 'The more of me you take, the more you leave behind. What am I?'",
        "answer": "Footsteps",
        "points": 50
    },
    {
        "question": "🧩 Puzzle Challenge: 'What comes next in the sequence: 1, 4, 9, 16, 25, ?'",
        "answer": "36",
        "points": 50
    },
    {
        "question": "💡 Brain Teaser: 'I have keys but open no locks. I have space but no room. You can enter but not go outside. What am I?'",
        "answer": "Keyboard",
        "points": 50
    },
    {
        "question": "🔍 Cryptic Clue: 'Reverse the word to reveal an animal: god'",
        "answer": "Dog",
        "points": 75
    },
    {
        "question": "📚 Literature Challenge: 'Who wrote the play Hamlet?'",
        "answer": "William Shakespeare",
        "points": 50
    },
    {
        "question": "🎵 Music Trivia: 'Which band released the hit song Bohemian Rhapsody?'",
        "answer": "Queen",
        "points": 50
    },
    {
        "question": "🎬 Movie Challenge: 'Which movie features the quote, May the Force be with you?'",
        "answer": "Star Wars",
        "points": 50
    },
    {
        "question": "🌎 Geography Trivia: 'What is the capital of Canada?'",
        "answer": "Ottawa",
        "points": 50
    },
    {
        "question": "🔢 Number Challenge: 'What is the next prime number after 19?'",
        "answer": "23",
        "points": 50
    },
    {
        "question": "⏳ History Question: 'Who was the first president of the United States?'",
        "answer": "George Washington",
        "points": 50
    },
    {
        "question": "🧠 Logical Puzzle: 'If you multiply me by any other number, the answer will always remain the same. What am I?'",
        "answer": "Zero",
        "points": 50
    },
    {
        "question": "🧩 Wordplay: 'What common English word becomes shorter when you add two letters to it?'",
        "answer": "Short",
        "points": 50
    },
    {
        "question": "🍽️ Food Trivia: 'What is the main ingredient in traditional Japanese miso soup?'",
        "answer": "Miso paste",
        "points": 50
    },
    {
        "question": "🚀 Space Trivia: 'Which planet is known as the Red Planet?'",
        "answer": "Mars",
        "points": 50
    },
    {
        "question": "🕰️ Time Riddle: 'The more you have of me, the less you see. What am I?'",
        "answer": "Darkness",
        "points": 50
    },
    {
        "question": "💡 Math Brain Teaser: 'If a rooster lays an egg on top of a barn, which way does it roll?'",
        "answer": "Roosters don’t lay eggs",
        "points": 75
    },
    {
        "question": "🐉 Mythology Trivia: 'In Greek mythology, who is the king of the gods?'",
        "answer": "Zeus",
        "points": 50
    },
    {
        "question": "🎭 Famous Quotes: 'Who said, I think, therefore I am?'",
        "answer": "René Descartes",
        "points": 50
    }
]
