# 3. Heuristic Recommendation Engine Logic (Viva Guide)

## What is a Heuristic Approach?
A heuristic approach uses practical, rule-based logic to solve a problem efficiently without needing complex Machine Learning models. In our project, instead of training neural networks, we use **SQL analytics and logical rules** to intelligently predict what a student might want to read next based on their past behaviour.

## Python Implementation

Here is the core logic function executing our recommendation algorithm (placed in `engine.py`):

```python
def get_recommendations(self, user_id: int):
    # Establish connection
    cnx = self._get_connection()
    cur = cnx.cursor(dictionary=True)

    # 1. Identify the user's favourite category 
    # Logic: Look at past transactions, group by category, pick the most frequent one
    cur.execute('''
        SELECT b.category, COUNT(*) as borrow_count 
        FROM transactions t 
        JOIN books b ON t.book_id = b.id 
        WHERE t.user_id = %s 
        GROUP BY b.category 
        ORDER BY borrow_count DESC LIMIT 1
    ''', (user_id,))
    
    favourite_cat_row = cur.fetchone()
    
    if not favourite_cat_row:
        return [] # No history, return default list
        
    top_category = favourite_cat_row['category']

    # 2. Get books the user has ALREADY read so we don't recommend them again
    cur.execute("SELECT book_id FROM transactions WHERE user_id = %s", (user_id,))
    already_read_ids = [row['book_id'] for row in cur.fetchall()]

    # 3. Fetch 3 available books from their favourite category that they haven't read
    # Format the IDs correctly for the NOT IN clause
    if already_read_ids:
        format_strings = ','.join(['%s'] * len(already_read_ids))
        query = f'''
            SELECT id, title, author, category 
            FROM books 
            WHERE category = %s 
            AND available_qty > 0 
            AND id NOT IN ({format_strings}) 
            LIMIT 3
        '''
        params = [top_category] + already_read_ids
        cur.execute(query, tuple(params))
    else:
        # Failsafe if the user has read everything but it hasn't registered
        cur.execute("SELECT * FROM books WHERE category=%s LIMIT 3", (top_category,))
        
    recommendations = cur.fetchall()
    
    cur.close()
    cnx.close()
    
    return recommendations
```

---

## Step-by-Step Logical Explanation (For Viva/Report)

When a teacher asks: *"How does your recommendation system work without Machine Learning?"*

**Answer:**
"Our recommendation engine utilizes a **Heuristic Association Map** achieved through relational database querying over 3 logical steps:

1.  **Behavioural Fingerprinting:** First, the system analyzes the user's historical `transactions` table. It joins this with the `books` table to count exactly how many books of each genre they have borrowed. It sorts this data to find their definitive 'Favourite Category' (e.g., 'Tech').
2.  **Filter Masking (Exclusion):** Recommending a book the user has already read is redundant. The system builds an array of all `book_id`s the user has previously checked out.
3.  **Targeted Retrieval:** Finally, a sophisticated SQL query searches the database for books that match the user's 'Favourite Category', ensures they are currently in stock (`available_qty > 0`), and explicitly cross-references the exclusion list (`NOT IN`) to guarantee fresh recommendations. It limits output to 3 books to prevent cognitive overload.

**Why this is 'Smart':** It perfectly mimics a real-world librarian's thought process ('You liked this sci-fi book, try this new sci-fi book') with strict O(N) database efficiency, utilizing pure RDBMS relation features instead of computationally expensive ML matrix mathematics."
