# 1. Database Schema & ER Diagram Logic

## Database Schema

The **LibraryPro** system uses a relational database named `librarypro`. Below are the SQL queries used to create the core tables, along with an explanation of the relationships and data types.

### SQL Queries

```sql
-- 1. Users Table
CREATE TABLE `users` (
    `id`       INT          NOT NULL AUTO_INCREMENT,
    `name`     VARCHAR(150) NOT NULL,
    `email`    VARCHAR(150) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    `roll_no`  VARCHAR(50)  DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Books Table
CREATE TABLE `books` (
    `id`            INT          NOT NULL AUTO_INCREMENT,
    `title`         VARCHAR(255) NOT NULL,
    `author`        VARCHAR(255) NOT NULL,
    `category`      VARCHAR(100) NOT NULL DEFAULT 'General',
    `isbn`          VARCHAR(20)  DEFAULT NULL,
    `total_qty`     INT          NOT NULL DEFAULT 1,
    `available_qty` INT          NOT NULL DEFAULT 1,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Transactions Table (Linking Users and Books)
CREATE TABLE `transactions` (
    `id`          INT          NOT NULL AUTO_INCREMENT,
    `user_id`     INT          NOT NULL,
    `book_id`     INT          NOT NULL,
    `issue_date`  DATE         NOT NULL,
    `due_date`    DATE         DEFAULT NULL,
    `status`      ENUM('issued','returned','overdue') NOT NULL DEFAULT 'issued',
    `fine_amount` DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`book_id`) REFERENCES `books`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## Primary Key and Foreign Key Relationships

*   **Primary Keys (PK):** The `id` column in each table acts as the Primary Key. It is an auto-incrementing integer that guarantees every record (a particular user, a specific book, or a single transaction event) has a unique identifier.
*   **Foreign Keys (FK):** The `transactions` table tracks *who* borrowed *what*. Therefore, it contains two Foreign Keys:
    *   `user_id`: Links back to `id` in the `users` table.
    *   `book_id`: Links back to `id` in the `books` table.
*   **Relationship Type:** This creates a **Many-to-Many** relationship between Users and Books. A user can borrow many books, and a book can be borrowed by many users over time. The `transactions` table acts as the intersection/junction table.
*   **Cascade Deletion:** `ON DELETE CASCADE` ensures that if a user or book is removed from the database, all their associated transaction records are also automatically deleted to maintain database integrity (no orphan records).

---

## Data Types and Justification (2nd Year B.Tech Standard)

Choosing the correct data types ensures both memory efficiency and data integrity:

1.  **`INT` (Integer):** Used for IDs and book quantities. 
    *   *Why:* Arithmetic operations and index lookups (for Primary Keys) are significantly faster with integers than strings.
2.  **`VARCHAR(n)` (Variable Character):** Used for names, emails, passwords, and titles.
    *   *Why:* Unlike `CHAR` (which pads spaces to fill a fixed length), `VARCHAR` only allocates as much memory as the actual text length up to the limit 'n'. It represents optimal storage for highly varied string lengths.
3.  **`DATE`:** Used for `issue_date` and `due_date`.
    *   *Why:* We only care about the specific day a book is due, not the exact time. It saves space compared to `DATETIME`.
4.  **`ENUM`:** Used for transaction `status` ('issued', 'returned', 'overdue').
    *   *Why:* Restricts input to a predefined list. This prevents system bugs introduced by typos (e.g., stopping someone from typing 'return' instead of 'returned').
5.  **`DECIMAL(8,2)`:** Used for `fine_amount`.
    *   *Why:* Financial/currency values should never be stored as `FLOAT` due to floating-point precision errors in computer architecture. `DECIMAL(8,2)` guarantees exact values up to 8 digits with 2 decimal places (e.g., 999999.99).
