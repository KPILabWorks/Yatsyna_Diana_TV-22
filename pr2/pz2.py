#https://youtu.be/q0f23LkwmCw
import pandas as pd
import sqlite3

df = pd.read_csv('music_sentiment_dataset.csv')

conn = sqlite3.connect('music_sentiment.db')
cursor = conn.cursor()

df.to_sql('music_sentiment', conn, if_exists='replace', index=False, dtype={
    'User_ID': 'TEXT',
    'User_Text': 'TEXT',
    'Sentiment_Label': 'TEXT',
    'Recommended_Song_ID': 'TEXT',
    'Song_Name': 'TEXT',
    'Artist': 'TEXT',
    'Genre': 'TEXT',
    'Tempo (BPM)': 'INTEGER',
    'Mood': 'TEXT',
    'Energy': 'TEXT',
    'Danceability': 'TEXT'
})

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_id ON music_sentiment (User_ID);
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_song_id ON music_sentiment (Recommended_Song_ID);
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_sentiment ON music_sentiment (Sentiment_Label);
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_genre_tempo ON music_sentiment (Genre, "Tempo (BPM)");
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_mood_energy ON music_sentiment (Mood, Energy);
""")

conn.commit()
conn.close()

print("DataFrame успішно збережено у SQLite з індексами!")
